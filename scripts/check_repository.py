#!/usr/bin/env python3
"""Validate bootstrap structure, relative links and the trusted role registry."""
import json
import re
from pathlib import Path
from check_pr_scope import validate_policy

ROOT=Path(__file__).resolve().parents[1]


def main():
    roles=['yu-wei','zaixuan-ji','xingze-zhu','tianqi-hao','yifan-mao','guanjie-xue','yuntao-min']
    required=['README.md','AGENTS.md','CONTRIBUTING.md','.github/CODEOWNERS','.github/team-policy.json','docs/PROJECT_PLAN.md','docs/MODULE_BOUNDARIES.md','docs/PERMISSIONS.md','docs/TASKS.md','docs/ACCEPTANCE.md','docs/requirements/01_PRODUCT_MASTER.md','docs/requirements/ORIGINAL_TASKS.md','prompts/00_CHATGPTWORK_BOOTSTRAP.md']
    required += [f'team/{role}/PLAN.md' for role in roles]
    errors=[f'Missing {f}' for f in required if not (ROOT/f).is_file()]
    validate_policy(json.loads((ROOT/'.github/team-policy.json').read_text()))
    if len(list((ROOT/'prompts/members').glob('*.md'))) != 7: errors.append('Expected seven member prompts')
    if len(list((ROOT/'prompts/website').glob('*.md'))) != 3: errors.append('Expected three website prompts')
    for md in ROOT.rglob('*.md'):
        if '.git' in md.parts: continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',md.read_text()):
            target=target.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'): continue
            p=(md.parent/target).resolve()
            if not p.is_relative_to(ROOT): errors.append(f'Link escapes repository: {md.relative_to(ROOT)}')
            elif not p.exists(): errors.append(f'Broken link: {md.relative_to(ROOT)} -> {target}')
    for error in errors: print(error)
    if errors: raise SystemExit(1)
    print('Bootstrap files, relative links, seven roles, ten role/site prompts and policy are valid.')
    print('Approved website source is pending; no application capability has been tested here.')


if __name__=='__main__': main()
