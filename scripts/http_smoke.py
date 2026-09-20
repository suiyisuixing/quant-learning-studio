"""Actual loopback HTTP concurrency smoke; synthetic accounts, not human testing."""
import concurrent.futures, httpx, json, os, socket, subprocess, sys, tempfile, time, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix='qlab-http-') as work:
    env={**os.environ,'QLAB_DB':str(Path(work)/'db.sqlite')}
    for k in ['QLAB_AI_KEY','QLAB_CN_TOKEN','QLAB_US_KEY']:env.pop(k,None)
    log=open(Path(work)/'http.log','w')
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=log,stderr=log)
    base=f'http://127.0.0.1:{port}'
    try:
        for i in range(60):
            try:
                if httpx.get(base+'/api/status',timeout=1).status_code==200:break
            except Exception:time.sleep(.1)
        def task(i):
            with httpx.Client(base_url=base,timeout=30,trust_env=False) as c:
                start=time.perf_counter();a=c.post('/api/auth/register',json={'email':f'http-{i}@example.com','name':'自动化测试账户','password':'http-test-password-123'});a.raise_for_status()
                assert a.cookies.get('qlab_session');assert 'HttpOnly' in a.headers['set-cookie'];c.headers['X-CSRF-Token']=a.json()['csrf']
                r=c.post('/api/experiments',json={'name':'HTTP并发软件测试','client_key':uuid.uuid4().hex});r.raise_for_status()
                assert r.json()['payload']['data_kind']=='SYNTHETIC'
                get=c.get('/api/experiments/'+r.json()['id']);get.raise_for_status();assert get.json()['id']==r.json()['id']
                c.post('/api/auth/logout',json={}).raise_for_status();assert c.get('/api/me').status_code==401
                return {'scenario':i,'ok':True,'seconds':round(time.perf_counter()-start,3)}
        t=time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:results=list(pool.map(task,range(10)))
        out={'kind':'actual loopback HTTP, ten concurrent synthetic accounts','human_testers':0,'passed':sum(r['ok'] for r in results),'wall_seconds':round(time.perf_counter()-t,3),'results':results,'boundary':'Not an Internet deployment, browser cookie acceptance, or production load certification.'}
        (ROOT/'evidence/http-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
        print(json.dumps(out,ensure_ascii=False))
    finally:
        proc.terminate();proc.wait(timeout=10);log.close()
