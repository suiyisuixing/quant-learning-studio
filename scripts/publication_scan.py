#!/usr/bin/env python3
"""Publication preflight for tracked files and every reachable historical blob.

This is a bounded pattern/file-policy check, not a guarantee of legal permission
or absence of all personal data. Human review of imported source is still needed.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

FORBIDDEN_SUFFIXES = {'.pdf','.docx','.db','.sqlite','.sqlite3','.pem','.key','.p12','.pfx','.log','.csv','.parquet','.faiss','.index','.npy','.npz','.zip'}
FORBIDDEN_PARTS = {'node_modules','.venv','venv','__pycache__','private','local','uploads','recordings'}
PATTERNS = [
    ('private key',re.compile(rb'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----')),
    ('GitHub token',re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}')),
    ('service secret',re.compile(rb'\bsk-[A-Za-z0-9_-]{24,}\b')),
    ('AWS access key',re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('credential URL',re.compile(rb'https?://[^\s/:]+:[^\s/@]+@')),
    ('private application email',re.compile(rb'[A-Za-z0-9._%+-]+@(?:student\.)?xjtlu\.edu\.cn')),
]


def git(*args):
    return subprocess.check_output(['git',*args])


def scan_blob(data):
    return [name for name,pattern in PATTERNS if pattern.search(data)]


def scan_name(name):
    p=Path(name)
    reasons=[]
    if p.suffix.lower() in FORBIDDEN_SUFFIXES:
        reasons.append('restricted data/binary extension')
    if any(part in FORBIDDEN_PARTS for part in p.parts):
        reasons.append('private/generated directory')
    if p.name.startswith('.env') and p.name != '.env.example':
        reasons.append('environment secrets file')
    return reasons


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--history',help='Scan all reachable historical blobs/trees for this ref')
    args=parser.parse_args()
    failures=[]
    names=[s.decode() for s in git('ls-files','-z').split(b'\0') if s]
    if not names:
        raise SystemExit('No tracked files to inspect; refusing an empty preflight')
    for name in names:
        p=Path(name)
        failures.extend((name,r) for r in scan_name(name))
        if p.is_symlink():
            failures.append((name,'symlink not permitted in bootstrap publication'))
            continue
        if not p.is_file():
            failures.append((name,'tracked file missing'))
            continue
        failures.extend((name,r) for r in scan_blob(p.read_bytes()))
    blobs=set()
    if args.history:
        # Every commit tree is checked, including removed names and symlinks.
        for commit in git('rev-list',args.history).decode().splitlines():
            for record in git('ls-tree','-rz',commit).split(b'\0'):
                if not record: continue
                meta,raw_name=record.split(b'\t',1)
                mode,kind,oid=meta.decode().split()
                name=raw_name.decode()
                failures.extend(('history:'+name,r) for r in scan_name(name))
                if mode not in ('100644','100755'):
                    failures.append(('history:'+name,'non-regular file mode'))
                if kind == 'blob': blobs.add(oid)
        for oid in blobs:
            failures.extend(('historical-blob:'+oid,r) for r in scan_blob(git('cat-file','blob',oid)))
    for path,reason in sorted(set(failures)):
        print(f'FAIL {path}: {reason}')  # Never print matched values.
    print(f'Inspected {len(names)} tracked files and {len(blobs)} unique historical blobs.')
    print('Pattern checks do not establish source/data licensing or semantic privacy review.')
    return bool(failures)


if __name__=='__main__':
    sys.exit(main())
