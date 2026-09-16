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
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def read(name):
    return json.loads((OUT / name).read_text())

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

MAPPING = read('folder_map.json')

def moved(path):
    parts = Path(path).parts
    return str(Path(MAPPING.get(parts[0], parts[0]), *parts[1:]))

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
        if node.module == 'corrosion.research_paths':
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

    for old, new in MAPPING.items():
        check((ROOT / new).is_dir() and not (ROOT / new).is_symlink(), 'canonical directory: ' + new)
        check((ROOT / old).is_symlink() and os.readlink(ROOT / old) == new, 'compatibility link: ' + old)
    changed_links = {row['path']: row['new_target'] for row in read('symlink_changes.json')}
    for row in read('symlinks_before.json'):
        name = moved(row['path']); path = ROOT / name
        expected = changed_links.get(name, row['target'])
        check(path.is_symlink() and os.readlink(path) == expected and path.exists(), 'archived link: ' + name)
    result['compatibility_links'] = len(MAPPING)
    result['preserved_existing_links'] = len(read('symlinks_before.json'))

    edits = {row['path']: row for row in read('edited_files.json')}
    baseline = read('files_before.json')
    result['live_workspace_metadata'] = []
    hashed = parsed = ast_matches = unchanged = 0
    for row in baseline:
        name = moved(row['path']); path = ROOT / name
        if not path.is_file() or path.is_symlink():
            failures.append('missing/changed file type: ' + name); continue
        if name == '.idea/workspace.xml':
            # This ignored IDE session file changed independently during the work.
            # Report it explicitly; do not overwrite a live editor's workspace or
            # confuse its mutable state with frozen scientific evidence.
            result['live_workspace_metadata'].append(dict(
                path=name, before_sha256=row['sha256'], current_sha256=digest(path),
                scope='IDE session metadata; excluded from research preservation'))
            continue
        edit = edits.get(name)
        if edit:
            before = OUT / 'source_before' / name
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
    result.update(baseline_files=len(baseline), edited_existing_files=len(edits),
                  unchanged_files_hashed=hashed, baseline_python_files_parsed=parsed,
                  edited_python_trees_compared=ast_matches)
    if (OUT / 'added_files.json').exists():
        additions=read('added_files.json')
        for row in additions:
            p=ROOT/row['path']
            check(p.is_file() and digest(p)==row['sha256'], 'new file hash: '+row['path'])
            if p.suffix == '.py':
                try: ast.parse(p.read_text())
                except SyntaxError as exc: failures.append('new Python syntax: '+row['path']+': '+str(exc))
        result['added_files_hashed']=len(additions)

    # Only current entry guides are required to have live links; archived prose
    # deliberately retains paths from the state it documented.
    documents = [ROOT/'README.md', ROOT/'CLAUDE.md', ROOT/'report_v2/README.md']
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
    check(len(smoke)==21 and all(r['exit_code']==0 for r in smoke),'runtime smoke receipts')
    result['runtime_smoke_checks_passed']=sum(r['exit_code']==0 for r in smoke)
    result['runtime_note']='Model and smoke checks are saved receipts; this verifier does not execute models.'

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
