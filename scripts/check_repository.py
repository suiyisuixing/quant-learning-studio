#!/usr/bin/env python3
"""Validate bootstrap structure, relative links and the trusted role registry."""
import json
import re
from pathlib import Path
from check_pr_scope import validate_policy

ROOT=Path(__file__).resolve().parents[1]


def main():
    roles=['yu-wei','zaixuan-ji','xiangze-zhu','tianqi-hao','yifan-mao','guanjie-xue','yuntao-min']
    required=['README.md','PRODUCT.md','AGENTS.md','CONTRIBUTING.md','LICENSE_STATUS.md','.github/CODEOWNERS','.github/team-policy.json','docs/PROJECT_PLAN.md','docs/MODULE_BOUNDARIES.md','docs/ACCESS_MODEL.md','docs/TEAM_ROSTER.md','docs/TASKS.md','docs/INITIALIZATION_REPORT.md','docs/requirements/ORIGINAL_TASKS.md','prompts/START_HERE.md','prompts/01_PRODUCT_MASTER.md','prompts/00_CHATGPTWORK_BOOTSTRAP.md','docs/FOUR_FEATURES.md','docs/UI_BASELINE.md','docs/INTERFACES.md','docs/DEMO_SCRIPT.md','templates/RESEARCH_TEST_PLAN.md','templates/RESEARCH_TEST_DELIVERY.md','templates/DEMO_EVIDENCE.md']
    required += [f'plans/{role}/PLAN.md' for role in roles]
    errors=[f'Missing {f}' for f in required if not (ROOT/f).is_file()]
    validate_policy(json.loads((ROOT/'.github/team-policy.json').read_text()))
    if len(list((ROOT/'prompts/members').glob('*.md'))) != 7: errors.append('Expected seven member prompts')
    if {p.name for p in (ROOT/'prompts/runtime').glob('*.md')} != {'PRE_PLAN.md','REPORT.md','TUTOR.md','LEARNING_FEEDBACK.md'}: errors.append('Expected four R3 runtime prompts')
    feature=json.loads((ROOT/'requirements/four_features.json').read_text())
    if [f['id'] for f in feature['features']]!=['F1','F2','F3','F4']: errors.append('Four feature definitions changed')
    import_manifest=json.loads((ROOT/'docs/SOURCE_IMPORT.json').read_text())
    for f in import_manifest['files']:
        p=ROOT/f['path']
        if not p.is_file(): errors.append('Missing imported source: '+f['path'])
    # UI baseline hashes are evidence of the initial import, not a forever-ban
    # on later approved member changes. Check the original attached archive separately.
    for md in ROOT.rglob('*.md'):
        rel=md.relative_to(ROOT).as_posix()
        if any(part in ('.git','.venv','node_modules') for part in md.parts): continue
        if rel.startswith(('docs/history/','docs/source-baseline/')) or rel=='docs/prompt-pack/R3_SOURCE.md': continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',md.read_text()):
            target=target.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'): continue
            p=(md.parent/target).resolve()
            if not p.is_relative_to(ROOT): errors.append(f'Link escapes repository: {md.relative_to(ROOT)}')
            elif not p.exists(): errors.append(f'Broken link: {md.relative_to(ROOT)} -> {target}')
    for error in errors: print(error)
    if errors: raise SystemExit(1)
    print('R3 files, active relative links, seven roles/four developers, seven member/four runtime prompts and policy are valid.')
    print('Source import is present. This structural check is not F1-F4 or real-model acceptance.')


if __name__=='__main__': main()
