#!/usr/bin/env python3
"""Trusted default-branch policy evaluation; never executes PR code."""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class ScopeError(ValueError):
    pass


def safe_path(value, prefix=False):
    if not isinstance(value, str) or not value or value.startswith('/'):
        raise ScopeError('Invalid repository path')
    checked = value[:-1] if prefix and value.endswith('/') else value
    if any(c in value for c in '\\*?[]') or any(ord(c) < 32 for c in value):
        raise ScopeError('Unsafe repository path')
    if any(p in ('', '.', '..', '.git') for p in checked.split('/')):
        raise ScopeError('Non-canonical repository path')
    return value


def within(path, allowed):
    safe_path(path)
    safe_path(allowed, prefix=True)
    return path.startswith(allowed) if allowed.endswith('/') else path == allowed


def user_id(value):
    return type(value) is int and value > 0


def validate_policy(policy):
    if policy.get('version') != 1:
        raise ScopeError('Unsupported policy version')
    owner = policy.get('owner', {})
    if not user_id(owner.get('id')) or not re.fullmatch(r'[A-Za-z0-9-]+', owner.get('login', '')):
        raise ScopeError('Invalid owner identity')
    roles, ids, logins = set(), {owner['id']}, {owner['login'].lower()}
    for m in policy.get('members', []):
        role = m.get('role', '')
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)+', role) or role in roles:
            raise ScopeError('Invalid or duplicate role')
        roles.add(role)
        if m.get('plan_path') != f'team/{role}/PLAN.md':
            raise ScopeError('Role plan path does not match')
        if m.get('identity_status') not in ('PENDING', 'VERIFIED'):
            raise ScopeError('Unknown identity status')
        if m['identity_status'] == 'PENDING':
            if m.get('id') is not None or m.get('login') is not None or m.get('implementation_approval') is not None:
                raise ScopeError('Pending identity must not have an account or approval')
        else:
            login = m.get('login', '')
            if not user_id(m.get('id')) or not re.fullmatch(r'[A-Za-z0-9-]+', login):
                raise ScopeError('Verified identity is incomplete')
            if m['id'] in ids or login.lower() in logins:
                raise ScopeError('Duplicate registered identity')
            ids.add(m['id'])
            logins.add(login.lower())
        for path in m.get('module_paths', []):
            safe_path(path, prefix=True)
            if path.split('/')[0] in ('.github', 'scripts', 'contracts', 'team') or path.startswith('tests/governance'):
                raise ScopeError('Member module includes protected governance/shared path')
        approval = m.get('implementation_approval')
        if approval:
            if approval.get('approved_by') != owner['id']:
                raise ScopeError('Approval is not registered by owner')
            if not re.fullmatch(r'[0-9a-f]{40,64}', approval.get('plan_blob_sha', '')):
                raise ScopeError('Invalid approved plan blob')
            if not approval.get('approved_paths'):
                raise ScopeError('Approved paths missing')
            for path in approval['approved_paths']:
                safe_path(path, prefix=True)
                if not any(within(path.rstrip('/') + ('/placeholder' if path.endswith('/') else ''), module) for module in m.get('module_paths', [])):
                    raise ScopeError('Approved scope exceeds role module')
    return policy


def changed_paths(files, expected_count):
    if type(expected_count) is not int or expected_count <= 0 or len(files) != expected_count:
        raise ScopeError('Incomplete or empty changed-file list')
    paths, seen = [], set()
    for file in files:
        name = safe_path(file.get('filename'))
        if name in seen:
            raise ScopeError('Duplicate changed-file entry')
        seen.add(name)
        status = file.get('status')
        if status not in ('added', 'removed', 'modified', 'renamed', 'changed', 'copied'):
            raise ScopeError('Unknown file-change status')
        paths.append(name)
        if status in ('renamed', 'copied'):
            paths.append(safe_path(file.get('previous_filename')))
    return paths


def evaluate(policy, author, files, expected_count, current_plan_sha=None):
    validate_policy(policy)
    paths = changed_paths(files, expected_count)
    owner = policy['owner']
    if author.get('id') == owner['id'] and author.get('login', '').lower() == owner['login'].lower():
        return 'Verified owner integration; final manual merge remains with Yu.Wei'
    member = next((m for m in policy['members'] if m.get('identity_status') == 'VERIFIED' and m.get('id') == author.get('id') and m.get('login', '').lower() == author.get('login', '').lower()), None)
    if member is None:
        raise ScopeError('Author is not a verified registered member')
    if all(p == member['plan_path'] for p in paths):
        return 'Verified member PLAN-only proposal; implementation is not approved by this result'
    approval = member.get('implementation_approval')
    if not approval:
        raise ScopeError('Implementation PLAN and paths have not been approved by owner')
    if member['plan_path'] in paths:
        raise ScopeError('PLAN changes require a separate PLAN-only PR and fresh approval')
    if current_plan_sha != approval['plan_blob_sha']:
        raise ScopeError('Approved PLAN is not the current trusted-base PLAN blob')
    for path in paths:
        if not any(within(path, scope) for scope in approval['approved_paths']):
            raise ScopeError('Changed path exceeds owner-approved scope: '+path)
    return 'Verified member changes are within the exact approved PLAN and paths'


def api(path, token, data=None):
    url = 'https://api.github.com'+path
    headers = {'Accept':'application/vnd.github+json', 'Authorization':'Bearer '+token, 'X-GitHub-Api-Version':'2022-11-28', 'User-Agent':'quant-learning-studio-scope-gate'}
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def publish(repo, sha, token, state, description):
    run = os.environ.get('GITHUB_RUN_ID')
    payload = {'state':state,'context':'trusted-scope','description':description[:140]}
    if run:
        payload['target_url'] = f'https://github.com/{repo}/actions/runs/{run}'
    api(f'/repos/{repo}/statuses/{sha}', token, payload)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--policy', default='.github/team-policy.json')
    args = parser.parse_args()
    token = os.environ.get('GITHUB_TOKEN', '')
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    trusted_sha = os.environ.get('GITHUB_SHA', '')
    if not token or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or not re.fullmatch(r'[0-9a-f]{40}', trusted_sha):
        raise ScopeError('Missing or invalid trusted GitHub execution context')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    event_name = os.environ.get('GITHUB_EVENT_NAME')
    if event_name not in ('pull_request_target', 'push', 'workflow_dispatch'):
        raise ScopeError('This privileged gate cannot run from an untrusted PR workflow')
    policy = validate_policy(json.loads(Path(args.policy).read_text()))
    number = event.get('pull_request', {}).get('number') or event.get('number') or event.get('inputs', {}).get('pull_request')
    if not number:
        if event_name not in ('push', 'workflow_dispatch') or os.environ.get('GITHUB_REF') != 'refs/heads/main':
            raise ScopeError('No PR and not trusted main validation')
        publish(repo,trusted_sha,token,'success','Trusted main policy validated; no member PR evaluated')
        print('Trusted main validation; no member PR was simulated.')
        return
    if not str(number).isdigit() or int(number) < 1:
        raise ScopeError('Invalid pull request number')
    number = int(number)
    pr = api(f'/repos/{repo}/pulls/{number}',token)
    sha = pr['head']['sha']
    if pr['base']['repo']['full_name'] != repo or pr['base']['ref'] != 'main' or pr['state'] != 'open':
        raise ScopeError('PR is not open against this main branch')
    publish(repo,sha,token,'pending','Checking verified identity, trusted PLAN and every changed path')
    try:
        files = []
        # GitHub caps this endpoint at 3,000 files. Count mismatch fails closed.
        for page in range(1,31):
            batch = api(f'/repos/{repo}/pulls/{number}/files?per_page=100&page={page}',token)
            if not isinstance(batch,list):
                raise ScopeError('Malformed GitHub file response')
            files.extend(batch)
            if len(batch) < 100:
                break
        member = next((m for m in policy['members'] if m.get('id') == pr['user']['id'] and m.get('identity_status') == 'VERIFIED'),None)
        plan_sha = None
        if member and member.get('implementation_approval'):
            path = urllib.parse.quote(member['plan_path'],safe='/')
            plan = api(f'/repos/{repo}/contents/{path}?ref={trusted_sha}',token)
            if plan.get('type') != 'file':
                raise ScopeError('Trusted PLAN is not a normal file')
            plan_sha = plan['sha']
        message = evaluate(policy,pr['user'],files,pr['changed_files'],plan_sha)
        latest = api(f'/repos/{repo}/pulls/{number}',token)
        if latest['head']['sha'] != sha:
            raise ScopeError('PR head changed during evaluation; current head must run separately')
        publish(repo,sha,token,'success',message)
        print(message)
    except Exception as exc:
        reason = str(exc) if isinstance(exc,ScopeError) else 'GitHub data/API validation failed; gate closed'
        publish(repo,sha,token,'failure',reason)
        raise ScopeError(reason) from None


if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        print('SCOPE GATE FAILED: '+(str(exc) if isinstance(exc,ScopeError) else type(exc).__name__),file=sys.stderr)
        sys.exit(1)
