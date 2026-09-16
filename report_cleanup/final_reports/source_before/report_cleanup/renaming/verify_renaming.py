"""Verify the renamed handoff without training, rebuilding, or changing Git.

--quick checks layout, edited text, Python syntax, links and saved check receipts.
--full also hashes all 16,202 pre-existing regular files (approximately 49 GB).
--check-git additionally requires the original branch, refs and index unchanged;
use this only while reviewing this uncommitted migration in the original checkout.
Only verification_quick.json or verification_full.json is written by this script.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import os
import re
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def read(name):
    return json.loads((OUT / name).read_text())

@lru_cache(maxsize=None)
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

MAPPING = read('folder_map.json')
SELECTED = ROOT / 'report_cleanup/selected_results'
SELECTED_MANIFEST = json.loads((SELECTED/'move_manifest.json').read_text())
SELECTED_MOVES = {row['old_path']: row['new_path'] for row in SELECTED_MANIFEST['moved_files']}
LIVE_WORKSPACE_METADATA = {'.idea/workspace.xml', '.DS_Store'}

def moved(path):
    parts = Path(path).parts
    renamed = str(Path(MAPPING.get(parts[0], parts[0]), *parts[1:]))
    return SELECTED_MOVES.get(renamed, renamed)

# Only a path/import substitution and the explicitly tested artifact resolver are
# allowed in existing Python syntax trees. Model formulas and constants must match.
class NormalizePaths(ast.NodeTransformer):
    def text(self, text):
        for old, new in sorted(MAPPING.items(), key=lambda x: -len(x[1])):
            text = text.replace(new, old)
        return text.replace('-m corrosion.main', '-m main').replace('uvicorn corrosion.main', 'uvicorn main')

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.value = self.text(node.value)
        return node

    def visit_ImportFrom(self, node):
        if node.module in {'corrosion.research_paths', '_project_paths'}:
            return None
        if node.module:
            node.module = self.text(node.module)
        return node

    def visit_alias(self, node):
        node.name = self.text(node.name)
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == 'resolve_artifact_path':
            assert len(node.args) == 2 and not node.keywords
            assert isinstance(node.args[1], ast.Name) and node.args[1].id == 'artifacts_dir'
            node.func.id = 'Path'
            node.args = node.args[:1]
        if isinstance(node.func, ast.Name) and node.func.id == 'resolve_project_path':
            assert len(node.args) == 1 and not node.keywords
            return ast.BinOp(left=ast.Name(id='ROOT', ctx=ast.Load()), op=ast.Div(), right=node.args[0])
        return node


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--quick', action='store_true')
    group.add_argument('--full', action='store_true')
    parser.add_argument('--check-git', action='store_true')
    args = parser.parse_args()
    failures = []
    result = dict(time_utc=datetime.now(timezone.utc).isoformat(), mode='full' if args.full else 'quick')
    def check(ok, detail):
        if not ok:
            failures.append(detail)

    publication = ROOT/'report_cleanup/publication_tools'
    removal_manifest = json.loads((publication/'removal_manifest.json').read_text())
    retired = {row['path']: row for row in removal_manifest['removed_files']}
    publication_edits = {row['path']: row['sha256'] for row in
                         json.loads((publication/'modified_before.json').read_text())}
    for name in retired:
        check(Path(name).suffix == '.py' and not os.path.lexists(ROOT/name),
              'authorized publication-tool removal: ' + name)
    result['retired_publication_python_files'] = sorted(retired)
    backup = ROOT.parent/removal_manifest['backup']['path_relative_to_repository_parent']
    result['external_publication_backup_present'] = backup.is_file()
    if backup.is_file():
        check(digest(backup) == removal_manifest['backup']['sha256'], 'publication backup integrity')

    build_cleanup = ROOT/'report_cleanup/out_build_cleanup'
    build_manifest = json.loads((build_cleanup/'removal_manifest.json').read_text())
    build_removed = {row['path']: row for row in build_manifest['removed_files']}
    build_edits = {row['path']: row['sha256'] for row in
                   json.loads((build_cleanup/'modified_before.json').read_text())}
    readability_edits = {row['path']: row['before_sha256'] for row in
                         json.loads((ROOT/'report_cleanup/readability_check.json').read_text())['changed_files']}
    selected_edits = {row['path']: row['sha256'] for row in
                      json.loads((SELECTED/'modified_before.json').read_text())}
    selected_before = json.loads((SELECTED/'before.json').read_text())
    original_selection = {row['path']: row for row in selected_before['files']}
    check(set(SELECTED_MOVES) == set(original_selection), 'selected collection relocation scope')
    check(len(SELECTED_MOVES) == len(set(SELECTED_MOVES.values())), 'selected collection unique destinations')
    for old, new in SELECTED_MANIFEST['folder_map'].items():
        check(not os.path.lexists(ROOT/old), 'selected collection old directory remains: ' + old)
        check((ROOT/new).is_dir() and not (ROOT/new).is_symlink(), 'selected collection directory: ' + new)
    for row in SELECTED_MANIFEST['moved_files']:
        name = row['new_path']; path = ROOT/name
        check(name.startswith('selected_results/'), 'selected collection destination scope: ' + name)
        original = original_selection.get(row['old_path'], {})
        check(all(row.get(k) == original.get(k) for k in ['size', 'sha256']),
              'selected collection original identity: ' + name)
        check(path.is_file() and not path.is_symlink() and path.stat().st_size == row['size']
              and digest(path) == row['sha256'], 'selected collection preserved file: ' + name)
    provenance = json.loads((ROOT/'selected_results/manifest.json').read_text())['files']
    research_rows = {row['new_path']: row for row in SELECTED_MANIFEST['moved_files']
                     if Path(row['new_path']).suffix.lower() in {'.png', '.pdf'}}
    check({row['path'] for row in provenance} == set(research_rows)
          and len(provenance) == 30, 'selected research provenance coverage')
    for row in provenance:
        check(row['sha256'] == research_rows.get(row['path'], {}).get('sha256')
              and bool(row['exact_sources']), 'selected research provenance identity: ' + row['path'])
        for source in row['exact_sources']:
            path = ROOT/source
            check(path.is_file() and digest(path) == row['sha256'], 'selected research matching source: ' + source)
    backup = ROOT.parent/SELECTED_MANIFEST['backup']['path_relative_to_repository_parent']
    result['external_selected_results_backup_present'] = backup.is_file()
    if backup.is_file():
        check(digest(backup) == SELECTED_MANIFEST['backup']['sha256'], 'selected results backup integrity')
    result['selected_results_preserved_files_hashed'] = len(SELECTED_MOVES)
    result['selected_results_research_files_with_provenance'] = len(provenance)
    audit = json.loads((ROOT/'report_cleanup/out_audit/inventory.json').read_text())
    audited_builds = {row['path']: row for row in audit['files']
                      if row['classification'] == 'generated_build_cleanup_candidate'}
    check(set(build_removed) == set(audited_builds), 'out build-removal scope')
    for name, row in build_removed.items():
        check(name.startswith('out/') and Path(name).suffix != '.pdf'
              and not os.path.lexists(ROOT/name), 'authorized build-file removal: ' + name)
        original = audited_builds.get(name, {})
        check(all(row.get(k) == original.get(k) for k in ['size', 'sha256']),
              'audited build-file identity: ' + name)
    for name in build_manifest['removed_directories']:
        check(name.startswith('out/') and not os.path.lexists(ROOT/name),
              'removed empty output directory: ' + name)
    preserved_pdfs = {row['path']: row for row in build_manifest['preserved_files']}
    audited_pdfs = {row['path']: row for row in audit['files'] if row['kind'] == 'pdf'}
    check(set(preserved_pdfs) == set(audited_pdfs), 'out PDF preservation scope')
    for name, row in preserved_pdfs.items():
        p = ROOT/name
        check(p.is_file() and not p.is_symlink() and digest(p) == row['sha256']
              == audited_pdfs.get(name, {}).get('sha256'), 'preserved out PDF: ' + name)
    backup = ROOT.parent/build_manifest['backup']['path_relative_to_repository_parent']
    result['external_out_build_backup_present'] = backup.is_file()
    if backup.is_file():
        check(digest(backup) == build_manifest['backup']['sha256'], 'out build backup integrity')
    result['removed_out_build_files'] = len(build_removed)
    result['removed_out_empty_directories'] = len(build_manifest['removed_directories'])
    result['preserved_out_pdfs_hashed'] = len(preserved_pdfs)

    for old, new in MAPPING.items():
        check((ROOT / new).is_dir() and not (ROOT / new).is_symlink(), 'canonical directory: ' + new)
        check(not os.path.lexists(ROOT / old), 'obsolete root alias remains: ' + old)
    changed_links = {row['path']: row['new_target'] for row in read('symlink_changes.json')}
    for row in read('symlinks_before.json'):
        name = moved(row['path']); path = ROOT / name
        expected = changed_links.get(name, row['target'])
        check(path.is_symlink() and os.readlink(path) == expected and path.exists(), 'archived link: ' + name)
    result['removed_root_aliases'] = len(MAPPING)
    result['preserved_existing_links'] = len(read('symlinks_before.json'))

    edits = {row['path']: row for row in read('edited_files.json')}
    baseline = read('files_before.json')
    result['live_workspace_metadata'] = []
    hashed = parsed = ast_matches = unchanged = 0
    for row in baseline:
        name = moved(row['path']); path = ROOT / name
        if name in retired:
            continue  # Explicitly removed optional Python tools; manifest above checks absence.
        if name in build_removed:
            check(row['sha256'] == build_removed[name]['sha256'], 'removed build baseline: ' + name)
            continue
        if not path.is_file() or path.is_symlink():
            failures.append('missing/changed file type: ' + name); continue
        if name in LIVE_WORKSPACE_METADATA:
            # Ignored IDE/Finder state can change outside this task. Report it
            # explicitly without overwriting live application state or confusing
            # it with frozen scientific evidence.
            result['live_workspace_metadata'].append(dict(
                path=name, before_sha256=row['sha256'], current_sha256=digest(path),
                scope='IDE/Finder session metadata; excluded from research preservation'))
            continue
        edit = edits.get(name)
        if edit:
            before = ROOT/edit['before_path'] if 'before_path' in edit else OUT/'source_before'/name
            check(digest(before) == row['sha256'] == edit['before_sha256'], 'before evidence: ' + name)
            check(digest(path) == edit['after_sha256'], 'edited file hash: ' + name)
        elif args.full or path.suffix in {'.py', '.yaml', '.yml', '.toml'}:
            check(digest(path) == row['sha256'], 'preservation hash: ' + name)
            hashed += 1
            unchanged += 1
        else:
            check(path.stat().st_size == row['size'], 'preserved file size: ' + name)
        if path.suffix == '.py':
            try:
                current = ast.parse(path.read_text()); parsed += 1
                if edit:
                    original = ast.parse((OUT / 'source_before' / name).read_text())
                    check(ast.dump(NormalizePaths().visit(original)) == ast.dump(NormalizePaths().visit(current)),
                          'non-path Python change: ' + name)
                    ast_matches += 1
            except Exception as exc:
                failures.append('Python syntax/semantic check: ' + name + ': ' + str(exc))
    result.update(baseline_files=len(baseline), edited_existing_files=len(set(edits)-set(retired)),
                  unchanged_files_hashed=hashed, baseline_python_files_parsed=parsed,
                  edited_python_trees_compared=ast_matches)
    if (OUT / 'added_files.json').exists():
        additions=read('added_files.json')
        for row in additions:
            p=ROOT/row['path']
            if row['path'] in retired:
                check(row['sha256'] == retired[row['path']]['sha256'],
                      'retired Python backup identity: ' + row['path'])
                continue
            check(p.is_file() and digest(p)==row['sha256'], 'new file hash: '+row['path'])
            if p.suffix == '.py':
                try: ast.parse(p.read_text())
                except SyntaxError as exc: failures.append('new Python syntax: '+row['path']+': '+str(exc))
        result['added_files_hashed']=len(additions)

    # Only current entry guides are required to have live links; archived prose
    # deliberately retains paths from the state it documented.
    documents = [ROOT/'README.md', ROOT/'CLAUDE.md', ROOT/'report_v2/README.md']
    documents += [ROOT/'report_v2/scripts/README.md', publication/'README.md',
                  build_cleanup/'README.md', ROOT/'report_cleanup/out_audit/README.md']
    documents += [SELECTED/'README.md', ROOT/'selected_results/README.md',
                  ROOT/'selected_results/condition_assessment/README.md',
                  ROOT/'selected_results/structural_capacity/README.md']
    documents += [ROOT/'report_v2'/name/'README.md'
                  for name in ['article', 'thesis', 'figures', 'tables', 'references']]
    documents += [ROOT/'report_cleanup/report_navigation/README.md']
    documents += list((ROOT/'docs').glob('*.md'))
    documents += [ROOT/new/'README.md' for new in MAPPING.values()]
    link_count = 0
    for doc in documents:
        if not doc.is_file():
            failures.append('missing current guide: ' + str(doc.relative_to(ROOT)))
            continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            target=target.strip().strip('<>')
            if re.match(r'\w+://', target) or target.startswith('#'): continue
            target=unquote(target.split('#')[0])
            if not target: continue
            check((doc.parent/target).exists(), f'document link: {doc.relative_to(ROOT)} -> {target}')
            link_count += 1
    result['current_document_links']=link_count

    tex_inputs=set()
    for master in [ROOT/'report_v2/thesis/v3/thesis.tex',ROOT/'report_v2/article/v3/article.tex']:
        base=master.parent; pending=[master]; seen=set()
        while pending:
            p=pending.pop()
            if p in seen:continue
            seen.add(p); text=p.read_text()
            for kind, raw in re.findall(r'\\(input|include|includegraphics|bibliography)(?:\[[^\]]*\])?\{([^}]+)\}',text):
                if '#' in raw:continue  # the thesis figure macro is checked below
                raw=raw.replace(r'\shared','../..')
                if '\\' in raw:
                    failures.append('unresolved TeX macro in '+raw);continue
                path=base/raw
                if not path.suffix:path=path.with_suffix('.bib' if kind=='bibliography' else '.tex')
                check(path.is_file(), 'TeX dependency: '+str(path))
                tex_inputs.add(str(path.resolve()))
                if kind in ['input','include'] and path.is_file():pending.append(path)
            for name in re.findall(r'\\fig\{([^}]+)\}',text):
                p=ROOT/'report_v2/figures'/f'{name}.pdf'
                check(p.is_file(),'thesis figure: '+name);tex_inputs.add(str(p))
    result['report_inputs_resolved']=len(tex_inputs)

    models_before=read('models_before.json');models_after=read('models_after.json')
    check(len(models_after)==len(models_before)==122,'model inventory count')
    for before, after in zip(models_before,models_after):
        check(after['path']==moved(before['path']),'model path mapping: '+before['path'])
        for key in ['original_path','loaded','type','keys','error','warnings','exit_code']:
            check(before.get(key)==after.get(key),'model check changed: '+before['path']+' '+key)
    result['saved_model_checks'] = dict(total=len(models_after),loaded=sum(r['loaded'] for r in models_after),
        unchanged_preexisting_failures=[r['path'] for r in models_after if not r['loaded']])
    def flatten(x):
        if isinstance(x,list):
            for y in x:yield from flatten(y)
        else:yield x
    prediction_checks=[]
    before_predictions=read('predictions_before.json');after_predictions=read('predictions_after.json')
    check(len(before_predictions)==len(after_predictions)==4,'prediction probe count')
    for before,after in zip(before_predictions,after_predictions):
        check(before['model']==after['model'],'prediction probe identity')
        a=list(flatten(before['predictions']));b=list(flatten(after['predictions']))
        delta=max(abs(x-y) for x,y in zip(a,b))
        check(len(a)==len(b) and all(math.isclose(x,y,rel_tol=0,abs_tol=1e-12) for x,y in zip(a,b)),
              'prediction comparison: '+before['model'])
        prediction_checks.append(dict(model=before['model'],max_absolute_difference=delta,
            bitwise_identical=before['array_sha256']==after['array_sha256']))
    result['prediction_checks']=prediction_checks
    smoke=read('smoke_after.json')
    check(len(smoke)==17 and all(r['exit_code']==0 for r in smoke),'runtime smoke receipts')
    result['runtime_smoke_checks_passed']=sum(r['exit_code']==0 for r in smoke)
    result['runtime_note']='Model and smoke checks are saved receipts; this verifier does not execute models.'

    cleanup = ROOT / 'report_cleanup/alias_removal'
    dependency_check = json.loads((cleanup/'references_resolved_after.json').read_text())
    check(dependency_check['passed'] and not dependency_check['failures'], 'historical path resolution receipts')
    result['historical_paths_preserved'] = dependency_check['existing_dependencies_preserved']
    if args.full:
        # Reuse hashes already computed above, then cover files added by the prior
        # rename stage. Only files explicitly backed up for this cleanup may vary.
        phase_baseline = json.loads((cleanup/'files_before.json').read_text())
        unchanged_phase = 0
        changed_phase = []
        for row in phase_baseline:
            if row['path'] in retired:
                continue
            if row['path'] in build_removed:
                check(row['sha256'] == build_removed[row['path']]['sha256'],
                      'removed build alias-phase baseline: ' + row['path'])
                continue
            if row['path'] in LIVE_WORKSPACE_METADATA:
                # These same live application files are reported separately in
                # the original-baseline pass; scientific files stay hash-checked.
                continue
            path = ROOT / SELECTED_MOVES.get(row['path'], row['path'])
            if not path.is_file() or path.is_symlink():
                failures.append('alias cleanup removed a regular file: ' + row['path'])
                continue
            if digest(path) == row['sha256']:
                unchanged_phase += 1
                continue
            backup = cleanup/'source_before'/row['path']
            recorded_edit = backup.is_file() and digest(backup) == row['sha256']
            recorded_edit |= publication_edits.get(row['path']) == row['sha256']
            recorded_edit |= build_edits.get(row['path']) == row['sha256']
            recorded_edit |= readability_edits.get(row['path']) == row['sha256']
            recorded_edit |= selected_edits.get(row['path']) == row['sha256']
            current_edit = edits.get(row['path'])
            if current_edit:
                recorded_edit |= (current_edit['before_sha256'] == row['sha256']
                                  and current_edit['after_sha256'] == digest(path))
            check(recorded_edit,
                  'unrecorded change during alias cleanup: ' + row['path'])
            changed_phase.append(row['path'])
        result['alias_cleanup_preservation'] = dict(
            baseline_files=len(phase_baseline), unchanged_files=unchanged_phase,
            recorded_changes=changed_phase,
            live_workspace_metadata_excluded=sorted(LIVE_WORKSPACE_METADATA))

    if args.check_git:
        env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
        def git(*argv):return subprocess.check_output(['git',*argv],cwd=ROOT,env=env,text=True)
        original=read('git_before.json')
        state=dict(head=git('rev-parse','HEAD').strip(),branch=git('branch','--show-current').strip(),
                   refs=git('show-ref'),index_sha256=digest(ROOT/git('rev-parse','--git-path','index').strip()))
        for key,value in state.items():check(value==original[key],'Git changed: '+key)
        check(not git('diff','--cached','--name-only'),'staged changes')
        result['git_unchanged']=all(state[k]==original[k] for k in state)
        result['git_after']=state
    result['failures']=failures;result['passed']=not failures
    (OUT/('verification_full.json' if args.full else 'verification_quick.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return bool(failures)

if __name__=='__main__':
    raise SystemExit(main())
