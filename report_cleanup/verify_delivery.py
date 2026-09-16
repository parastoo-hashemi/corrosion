#!/usr/bin/env python3
"""Verify cleanup preservation without fitting models or rewriting scientific outputs.

Only this tool's records in report_cleanup are written. --full hashes every
pre-cleanup file after applying the documented move mapping; --quick skips that
large-file pass. Historical execution defects are reported, not repaired.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'report_cleanup'
BASE = '7e69d7a'


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(name: str, value) -> None:
    (QA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


class StripDocstrings(ast.NodeTransformer):
    def strip(self, node):
        self.generic_visit(node)
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]
        return node
    visit_Module = strip
    visit_FunctionDef = strip
    visit_AsyncFunctionDef = strip
    visit_ClassDef = strip


def code_tokens(source: str):
    """Ignore comments, layout, and only AST-identified docstring tokens."""
    tree = ast.parse(source)
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node, clean=False) is not None:
                d = node.body[0]
                spans.append((d.lineno, d.end_lineno))
    return [(t.type, t.string) for t in tokenize.generate_tokens(io.StringIO(source).readline)
            if t.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                              tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER)
            and not any(lo <= t.start[0] <= hi for lo, hi in spans)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--quick', action='store_true')
    group.add_argument('--full', action='store_true')
    args = parser.parse_args()
    failures, known, checks = [], [], {}
    before = json.loads((QA / 'all_files_before.json').read_text())
    actions = json.loads((QA / 'planned_actions.json').read_text())
    changes_path = QA / 'code_documentation_changes.json'
    touched = json.loads(changes_path.read_text()) if changes_path.exists() else []
    touched_paths = {r['path'] for r in touched}
    moves = {r['old_path']: r['new_path_or_deleted'] for r in
             csv.DictReader((QA / 'move_manifest.csv').open())}

    checks['links'] = []
    for a in actions:
        if a['compatibility_link']:
            p = ROOT / a['old_path']
            ok = p.is_symlink() and p.exists() and p.resolve() == (ROOT / a['new_path']).resolve()
            checks['links'].append({'path': a['old_path'], 'ok': ok})
            if not ok: failures.append('Compatibility link: ' + a['old_path'])
        if a['action'] == 'ARCHIVE_FROM_GIT':
            expected = hashlib.sha256(subprocess.check_output(
                ['git', 'show', f"{BASE}:{a['old_path']}"], cwd=ROOT)).hexdigest()
            if sha(ROOT / a['new_path']) != expected:
                failures.append('Recovered archive content: ' + a['old_path'])

    checks['syntax_and_code_invariance'] = []
    for record in touched:
        rel = record['path']
        old = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=ROOT, text=True)
        new = (ROOT / rel).read_text()
        compile(new, rel, 'exec')
        ok = (ast.dump(StripDocstrings().visit(ast.parse(old)), include_attributes=False)
              == ast.dump(StripDocstrings().visit(ast.parse(new)), include_attributes=False))
        token_ok = code_tokens(old) == code_tokens(new)
        checks['syntax_and_code_invariance'].append({'path': rel, 'ast_equal': ok,
                                                     'code_tokens_equal': token_ok})
        if not (ok and token_ok): failures.append('Behavioural source diff: ' + rel)
    # Include ignored source directories in syntax verification; no bytecode is emitted.
    all_python = [r['path'] for r in before if r['extension'] == '.py']
    for rel in all_python:
        compile((ROOT / rel).read_text(), rel, 'exec')
    checks['all_existing_python_parse_count'] = len(all_python)

    import yaml
    import tomllib
    checks['configs'] = []
    for r in before:
        if r['extension'] not in ('.yaml', '.yml', '.toml'): continue
        p = ROOT / r['path']
        value = tomllib.loads(p.read_text()) if p.suffix == '.toml' else yaml.safe_load(p.read_text())
        ok = sha(p) == r['sha256']
        checks['configs'].append({'path': r['path'], 'parses': True, 'unchanged': ok})
        if not ok: failures.append('Config changed: ' + r['path'])
        if isinstance(value, dict) and 'specimens' in value:
            coerced = [s for s, v in value['specimens'].items() if v.get('treatment_coarse') is False]
            if coerced: known.append({'path': r['path'], 'issue': 'YAML NO parsed as False', 'specimens': coerced})
        if 'main_first' in p.read_text():
            known.append({'path': r['path'], 'issue': 'Pre-existing main_first scalar substitutions; parse success is not type validation'})

    checks['cli_help'] = []
    for rel in ('augmentation/augment_dataset.py', 'augmentation/make_splits.py',
                'augmentation/create_dataset_variants.py'):
        run = subprocess.run([sys.executable, '-B', rel, '--help'], cwd=ROOT,
                             text=True, capture_output=True)
        checks['cli_help'].append({'path': rel, 'exit_code': run.returncode})
        (QA / (Path(rel).stem + '_help.txt')).write_text(run.stdout + run.stderr)
        if run.returncode: failures.append('CLI help: ' + rel)

    # Imports are deliberately limited to modules whose top level does not run a pipeline.
    import_code = '''import sys
sys.path.insert(0, "main_4/src")
from corrosion_proxy_rul import config, splits, feature_engineering, models_rul_proxy, image_preprocessing
loaded = config.load_configs()
assert len(loaded) == 6
print("Five documented modules imported; six configs loaded; no pipeline called.")
'''
    run = subprocess.run([sys.executable, '-B', '-c', import_code], cwd=ROOT,
                         text=True, capture_output=True)
    checks['module_imports'] = {'exit_code': run.returncode, 'output': run.stdout, 'stderr': run.stderr}
    if run.returncode: failures.append('Documented main_4 module imports')

    # Current user-facing links must resolve; historical archive text is unchanged.
    docs = [ROOT / 'README.md', ROOT / 'CLAUDE.md', ROOT / 'report_v2/README.md']
    docs += list((ROOT / 'docs').glob('*.md'))
    docs += [ROOT / d / 'README.md' for d in ('main', 'main_2', 'main_3', 'main_4', 'main_4_old', 'augmentation')]
    broken = []
    count = 0
    for p in docs:
        if not p.exists(): continue
        for url in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', p.read_text()):
            if re.match(r'\w+://', url) or url.startswith('#'): continue
            url = unquote(url.split('#')[0].strip('<>'))
            count += 1
            if not (p.parent / url).exists(): broken.append({'file': str(p.relative_to(ROOT)), 'target': url})
    checks['curated_links'] = {'checked': count, 'broken': broken}
    if broken: failures.append('Broken curated documentation links')

    # All explicit report build inputs are checked without rebuilding PDFs.
    tex_inputs, unresolved_paths = [], []
    for r in before:
        rel = r['path']
        if r['extension'] != '.tex' or not rel.startswith(('activity_report/', 'report_v2/')): continue
        p = ROOT / rel
        master_dir = p.parent.parent if p.parent.name in ('chapters', 'frontmatter') else p.parent
        source = re.sub(r'(?<!\\)%[^\n]*', '', p.read_text())
        # Respect each master's declared graphics search path; commented includes
        # are historical notes, not dependencies used by the TeX build.
        master_name = 'activity_report.tex' if rel.startswith('activity_report/') else ('article.tex' if '/article/' in rel else 'thesis.tex')
        master = master_dir / master_name
        master_source = master.read_text() if master.exists() else source
        shared_match = re.search(r'\\newcommand\{\\shared\}\{([^}]+)\}', master_source)
        if shared_match:
            source = source.replace(r'\shared', shared_match.group(1))
            for name in re.findall(r'\\fig\{([^}]+)\}', source):
                raw = shared_match.group(1) + '/figures/' + name + '.pdf'
                ok = (master_dir / raw).exists()
                tex_inputs.append({'file': rel, 'command': 'fig', 'target': raw, 'resolves': ok})
                if not ok: failures.append(f'Report figure macro: {rel}: {raw}')
        graphics_dirs = []
        for group in re.findall(r'\\graphicspath\{((?:\{[^}]+\})+)\}', master_source):
            graphics_dirs.extend(master_dir / item for item in re.findall(r'\{([^}]+)\}', group))
        for cmd, raw in re.findall(r'\\(input|include|includegraphics|bibliography)(?:\[[^]]*\])?\{([^}]+)\}', source):
            if '#' in raw or '\\' in raw: continue
            suffixes = (['', '.tex'] if cmd in ('input', 'include') else
                        ['', '.bib'] if cmd == 'bibliography' else ['', '.pdf', '.png', '.jpg'])
            bases = [master_dir, p.parent] + (graphics_dirs if cmd == 'includegraphics' else [])
            ok = any((base / (raw + ext)).exists() for base in bases for ext in suffixes)
            tex_inputs.append({'file': rel, 'command': cmd, 'target': raw, 'resolves': ok})
            if not ok: failures.append(f'Report input: {rel}: {raw}')
        for raw in re.findall(r'\\path\{([^}]+)\}', source):
            raw = raw.replace('\\_', '_')
            # Literal full repository paths; short names/globs have explicit context in the prose.
            if raw.split('/')[0] not in {x['path'].split('/')[0] for x in before}: continue
            if any(ch in raw for ch in '*{}'): continue
            if not (ROOT / raw).exists(): unresolved_paths.append({'file': rel, 'path': raw})
    checks['latex_inputs'] = tex_inputs
    checks['literal_report_paths_missing'] = unresolved_paths
    if unresolved_paths:
        # Preserve pre-existing report wording; distinguish cleanup regressions.
        original_paths = {r['path'] for r in before}
        for item in unresolved_paths:
            if item['path'] in original_paths or item['path'] in moves:
                failures.append('Cleanup broke report path: ' + item['path'])
            else: known.append(dict(item, issue='Pre-existing report path/notation not an exact existing file'))

    checks['historical_source_hashes'] = []
    hash_records = []
    for row in csv.DictReader((ROOT / 'report_v2/tables/source_hashes.csv').open()):
        hash_records.append((row['path'], row['sha256']))
    v3 = json.loads((ROOT / 'report_v2/evidence/v3/figure_checks.json').read_text())
    hash_records += list(v3['sources'].items())
    for rel, expected in hash_records:
        ok = (ROOT / rel).exists() and sha(ROOT / rel) == expected
        checks['historical_source_hashes'].append({'path': rel, 'matches': ok})
        if not ok: failures.append('Historical source hash: ' + rel)

    snapshots = []
    local_state_drift = []
    if args.full:
        for r in before:
            rel = r['path']; actual = moves.get(rel, rel)
            if rel in touched_paths or rel == '.gitignore': continue
            p = ROOT / actual
            now = {'original_path': rel, 'path': actual, 'size': p.stat().st_size if p.exists() else None,
                   'sha256': sha(p) if p.exists() else None}
            snapshots.append(now)
            if now['size'] != r['size'] or now['sha256'] != r['sha256']:
                if rel == '.idea/workspace.xml':
                    # This untracked local IDE state is not edited by cleanup.
                    # Expose its drift instead of restoring over live user state.
                    local_state_drift.append({'before': r, 'after': now,
                                              'disposition': 'Left current IDE state untouched; original retained in full backup.'})
                else:
                    failures.append('Preservation mismatch: ' + rel)
        write_json('all_files_after.json', snapshots)
        protected = json.loads((QA / 'outputs_before.json').read_text())
        names = {r['path'] for r in protected}
        outputs_after = [r for r in snapshots if r['original_path'] in names]
        write_json('outputs_after.json', outputs_after)
        by_name = {r['original_path']: r for r in outputs_after}
        diff = [{'before': r, 'after': by_name.get(r['path'])} for r in protected
                if r['path'] not in by_name or any(r[k] != by_name[r['path']][k] for k in ('size', 'sha256'))]
        write_json('output_preservation_diff.json', diff)
        write_json('local_state_drift.json', local_state_drift)
        checks['full_preservation'] = {'all_original_files_checked': len(snapshots),
                                      'scientific_inputs_outputs_checked': len(protected),
                                      'output_differences': len(diff),
                                      'non_scientific_local_state_drift': len(local_state_drift)}
        if diff: failures.append('Scientific input/output differences')

    result = {'mode': 'full' if args.full else 'quick', 'failures': failures,
              'known_preexisting_limitations': known, 'checks': checks}
    write_json('verification_full.json' if args.full else 'verification_quick.json', result)
    print(json.dumps({'mode': result['mode'], 'failures': failures,
                      'known_limitations': len(known), 'full_preservation': checks.get('full_preservation')}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
