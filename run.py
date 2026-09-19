#!/usr/bin/env python3
"""Start the independent local application without changing global packages."""
from pathlib import Path
import argparse, os, subprocess, sys, venv, importlib.util
ROOT=Path(__file__).resolve().parent

def load_env():
    path=ROOT/'.env'
    if not path.exists():return
    for number,line in enumerate(path.read_text().splitlines(),1):
        line=line.strip()
        if not line or line.startswith('#'):continue
        if '=' not in line:raise SystemExit(f'.env第{number}行缺少 =')
        k,v=line.split('=',1);k=k.strip();v=v.strip()
        if not k.startswith('QLAB_'):raise SystemExit(f'.env第{number}行：只支持QLAB_设置')
        if len(v)>1 and v[0]==v[-1] and v[0] in '\"\'':v=v[1:-1]
        os.environ.setdefault(k,v)

def main():
    parser=argparse.ArgumentParser(description='Quant Learning Lab local launcher')
    parser.add_argument('--port',type=int,default=8017)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--use-current-env',action='store_true',help='use already prepared Python environment')
    parser.add_argument('--setup-only',action='store_true')
    args=parser.parse_args()
    if sys.version_info<(3,11):raise SystemExit('需要Python 3.11或更高版本；本次实测3.13。')
    if not 1<=args.port<=65535:raise SystemExit('端口无效')
    load_env()
    if args.use_current_env:python=sys.executable
    else:
        folder=ROOT/'.venv';python=folder/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        if not python.exists():
            print('创建项目专用虚拟环境（不修改全局Python）…',flush=True);venv.create(folder,with_pip=True)
        marker=folder/'qlab-requirements.sha256'
        import hashlib
        digest=hashlib.sha256((ROOT/'requirements.txt').read_bytes()).hexdigest()
        if not marker.exists() or marker.read_text()!=digest:
            print('安装锁定的项目依赖；首次需要联网。失败时不会启动半成品服务。',flush=True)
            subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
            marker.write_text(digest)
    if args.setup_only:return
    if args.host not in ('127.0.0.1','localhost'):
        if not os.environ.get('QLAB_ORIGIN') or not os.environ.get('QLAB_HOSTS'):
            raise SystemExit('对外监听前必须配置QLAB_ORIGIN与QLAB_HOSTS。请先阅读docs/DEPLOYMENT.md。')
    print(f'Quant Learning Lab: http://{args.host}:{args.port}\n仅启动新项目；按Ctrl+C停止。',flush=True)
    subprocess.run([str(python),'-m','uvicorn','app.main:app','--host',args.host,'--port',str(args.port)],cwd=ROOT,check=True)

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:pass
    except subprocess.CalledProcessError as exc:raise SystemExit(f'命令未成功完成（退出码{exc.returncode}），请查看上方错误。')
