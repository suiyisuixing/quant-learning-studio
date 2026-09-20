import os, json, io, csv, copy, hashlib, time, secrets
import pytest
from fastapi.testclient import TestClient
from app import engine
from app.main import app, initialize, RATE, db, ph

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('QLAB_DB',str(tmp_path/'test.db'))
    for key in ['QLAB_AI_KEY','QLAB_CN_TOKEN','QLAB_US_KEY']:monkeypatch.delenv(key,raising=False)
    RATE.clear();initialize()
    with TestClient(app) as c:yield c

def signup(c,email='student@example.com'):
    r=c.post('/api/auth/register',json={'email':email,'name':'测试同学','password':'correct-horse-123'})
    assert r.status_code==201,r.text
    c.headers['X-CSRF-Token']=r.json()['csrf'];return r.json()

def config(**kw):
    return {'dataset_id':'sample-cn','name':'测试实验','initial':10000,'cash_pct':20,'fee_bps':10,'top_n':3,'rebalance':10,'stop_pct':0,
      'weights':[.4,.4,.2],'start':'2024-01-02','end':'2024-12-31','reason':'独立测试','client_key':secrets.token_hex(16),**kw}

def experiment(c,**kw):
    r=c.post('/api/experiments',json=config(**kw));assert r.status_code==201,r.text;return r.json()

def sample_csv():
    d=engine.synthetic();s=io.StringIO();w=csv.DictWriter(s,fieldnames=['date','symbol','close','volume','market','currency']);w.writeheader();w.writerows(d['rows']);return s.getvalue()

def import_payload(**kw):return {'name':'明确标记的测试样本','market':'CN','currency':'CNY','source':'自制教学数据','source_url':'','rights':'仅用于软件功能测试','kind':'SYNTHETIC','csv_content':sample_csv(),**kw}

def test_health_and_no_fake_integrations(client):
    j=client.get('/api/status').json();assert not j['ai_configured'];assert not j['market_cn_configured'];assert j['real_user_tests']=='NOT_ESTABLISHED'

def test_html_and_security_headers(client):
    r=client.get('/');assert 'Quant Learning Lab' in r.text;assert r.headers['x-frame-options']=='DENY';assert "script-src 'self'" in r.headers['content-security-policy']

def test_host_protection(client):assert client.get('/',headers={'host':'evil.invalid'}).status_code==400

def test_register_password_hash_and_cookie(client):
    u=signup(client);assert client.get('/api/me').json()['id']==u['id']
    with db() as c:r=c.execute('SELECT password FROM users').fetchone()
    assert r['password'].startswith('$argon2');assert 'httponly' in str(client.cookies).lower() or client.cookies.get('qlab_session')

def test_invalid_email_and_short_password(client):
    for a in [{'email':'not-email','password':'correct-horse-123'},{'email':'a@b.co','password':'short'}]:assert client.post('/api/auth/register',json=a).status_code==422

def test_duplicate_register(client):
    signup(client);assert client.post('/api/auth/register',json={'email':'student@example.com','password':'correct-horse-123'}).status_code==409

def test_wrong_login(client):
    signup(client);assert client.post('/api/auth/login',json={'email':'student@example.com','password':'wrong-pass-123'}).status_code==401

def test_csrf_required(client):
    signup(client);del client.headers['X-CSRF-Token'];assert client.post('/api/experiments',json=config()).status_code==403

def test_cross_origin_rejected(client):
    assert client.post('/api/auth/register',json={'email':'a@b.co','password':'correct-horse-123'},headers={'origin':'https://evil.invalid'}).status_code==403

def test_logout_revokes_session(client):
    signup(client);cookie=client.cookies.get('qlab_session');assert client.post('/api/auth/logout',json={}).status_code==200
    client.cookies.set('qlab_session',cookie);assert client.get('/api/me').status_code==401

def test_expired_session(client):
    signup(client)
    with db() as c:c.execute('UPDATE sessions SET expires=?',(time.time()-10,))
    assert client.get('/api/me').status_code==401

def test_anonymous_cannot_read_dataset(client):assert client.get('/api/datasets').status_code==401

def test_synthetic_source_is_explicit(client):
    signup(client);rs=client.get('/api/datasets').json();assert len(rs)==2;assert all(x['kind']=='SYNTHETIC' for x in rs);assert all('不是真实' in x['source'] for x in rs)

def test_import_and_download(client):
    signup(client);r=client.post('/api/datasets',json=import_payload());assert r.status_code==201,r.text
    csv=client.get('/api/datasets/'+r.json()['id']+'/csv');assert csv.status_code==200;assert 'date,symbol,close,volume' in csv.text

def test_duplicate_csv_rejected(client):
    signup(client);s=sample_csv();s+=s.splitlines()[1]+'\n';assert client.post('/api/datasets',json=import_payload(csv_content=s)).status_code==422

def test_missing_csv_dates_rejected(client):
    signup(client);s=sample_csv().splitlines();s.pop(2);assert client.post('/api/datasets',json=import_payload(csv_content='\n'.join(s))).status_code==422

@pytest.mark.parametrize('p',['NaN','Infinity','-1','0'])
def test_nonfinite_and_negative_prices(client,p):
    signup(client);s=sample_csv().splitlines();r=s[1].split(',');r[2]=p;s[1]=','.join(r)
    assert client.post('/api/datasets',json=import_payload(csv_content='\n'.join(s))).status_code==422

def test_market_currency_mismatch(client):
    signup(client);assert client.post('/api/datasets',json=import_payload(currency='USD')).status_code==422

def test_case_requires_https(client):
    signup(client);r=client.post('/api/cases',json={'name':'测试案例','country':'CN','method':'这是测试方法','risk':'这是测试风险','source_url':'javascript:alert(1)','published':'2024-01-01','limitations':'软件测试不是基金事实'})
    assert r.status_code==422

def test_case_saved_as_unverified(client):
    signup(client);r=client.post('/api/cases',json={'name':'测试案例（虚构，仅测试）','country':'CN','method':'这是测试方法','risk':'这是测试风险','source_url':'https://example.com/source','published':'2024-01-01','limitations':'软件测试不是基金事实'})
    assert r.status_code==201;assert 'NOT_INDEPENDENTLY_VERIFIED' in r.json()['payload']['verification']

def test_real_market_not_faked_when_no_key(client):
    signup(client);r=client.post('/api/data/fetch',json={'market':'CN','symbols':['600000.SH'],'start':'2024-01-01','end':'2024-12-31','rights':'用户授权待测试说明'})
    assert r.status_code==503;assert len(client.get('/api/datasets').json())==2

def test_experiment_actual_computation(client):
    signup(client);r=experiment(client);p=r['payload'];assert len(p['strategies'])==3;assert len(p['strategies'][0]['curve'])==160
    assert len(p['factors'])==3;assert p['data_kind']=='SYNTHETIC';assert float(p['strategies'][2]['ending'])!=10000

def test_idempotent_duplicate(client):
    signup(client);cfg=config();a=client.post('/api/experiments',json=cfg);b=client.post('/api/experiments',json=cfg)
    assert a.json()['id']==b.json()['id'];assert len(client.get('/api/dashboard').json()['experiments'])==1

def test_idempotency_changed_parameters_conflict(client):
    signup(client);cfg=config();client.post('/api/experiments',json=cfg);cfg['cash_pct']=40
    assert client.post('/api/experiments',json=cfg).status_code==409

@pytest.mark.parametrize('kwargs',[{'weights':[.8,.8,.1]},{'initial':-1},{'cash_pct':120},{'top_n':0},{'rebalance':0}])
def test_invalid_strategy_config(client,kwargs):
    signup(client);assert client.post('/api/experiments',json=config(**kwargs)).status_code==422

def test_insufficient_period(client):
    signup(client);assert client.post('/api/experiments',json=config(start='2024-01-02',end='2024-01-05')).status_code==422

def test_cross_user_experiment_report_case_dataset_denied(client):
    signup(client);r=experiment(client);report=client.post('/api/reports',json={'experiment_id':r['id'],'reflection':'test'}).json()
    ds=client.post('/api/datasets',json=import_payload()).json();case=client.post('/api/cases',json={'name':'测试','country':'CN','method':'仅供测试的内容','risk':'仅供测试的内容','source_url':'https://example.com','published':'2024-01-01','limitations':'没有事实结论的测试'}).json()
    signup(client,'other@example.com')
    for route in ['/api/experiments/'+r['id'],'/api/reports/'+report['id'],'/api/reports/'+report['id']+'/download','/api/datasets/'+ds['id']+'/csv']:
        assert client.get(route).status_code==404,route
    assert client.get('/api/cases').json()==[]
    assert client.delete('/api/records/'+case['id']).status_code==404

def test_rule_tutor_not_ai(client):
    signup(client);r=experiment(client);a=client.post('/api/tutor',json={'experiment_id':r['id'],'question':'什么是最大回撤？'}).json()['payload']
    assert a['mode']=='RULE_BASED';assert '不是AI' in a['notice'];assert '合成教学数据' in a['text']

def test_ai_absent_fails_closed(client):
    signup(client);r=experiment(client);res=client.post('/api/tutor',json={'experiment_id':r['id'],'question':'风险？','use_ai':True,'allow_external':True})
    assert res.status_code==503

def test_ai_requires_consent(client,monkeypatch):
    signup(client);r=experiment(client);monkeypatch.setenv('QLAB_AI_KEY','fake-test-key')
    assert client.post('/api/tutor',json={'experiment_id':r['id'],'question':'风险？','use_ai':True}).status_code==422

def test_ai_no_plaintext_endpoint(client,monkeypatch):
    signup(client);r=experiment(client);monkeypatch.setenv('QLAB_AI_KEY','fake-test-key');monkeypatch.setenv('QLAB_AI_URL','http://localhost:1')
    assert client.post('/api/tutor',json={'experiment_id':r['id'],'question':'风险？','use_ai':True,'allow_external':True}).status_code==503

def test_report_persistence_and_escape(client):
    signup(client);r=experiment(client);p=client.post('/api/reports',json={'experiment_id':r['id'],'title':'测试报告','reflection':'<script>alert(1)</script>'})
    assert p.status_code==201;rid=p.json()['id'];assert len(client.get('/api/reports').json())==1
    out=client.get('/api/reports/'+rid+'/download?format=html');assert '<script>' not in out.text;assert '&lt;script&gt;' in out.text
    assert client.get('/api/reports/'+rid+'/download?format=json').json()['payload']['experiment']['id']==r['id']

def test_report_cannot_attach_other_experiment_chat(client):
    signup(client);a=experiment(client);b=experiment(client);ch=client.post('/api/tutor',json={'experiment_id':a['id'],'question':'风险'}).json()
    assert client.post('/api/reports',json={'experiment_id':b['id'],'chat_id':ch['id']}).status_code==422

def test_quiz_progress_truthful(client):
    signup(client);assert client.get('/api/dashboard').json()['passed']==[]
    assert not client.post('/api/lessons/answer',json={'lesson_id':'risk','answer':0}).json()['correct']
    assert client.get('/api/dashboard').json()['passed']==[]
    assert client.post('/api/lessons/answer',json={'lesson_id':'risk','answer':1}).json()['correct']
    assert client.get('/api/dashboard').json()['passed']==['risk']

def test_quiz_definition_does_not_expose_answer(client):
    signup(client);assert all('answer' not in x for x in client.get('/api/lessons').json())

def test_feedback_consent(client):
    signup(client);a={'task':'查找最大回撤','completed':True,'rating':4,'comment':'软件测试，不是真人反馈','consent':False}
    assert client.post('/api/feedback',json=a).status_code==422;a['consent']=True;assert client.post('/api/feedback',json=a).status_code==201

def test_delete_account_and_export(client):
    signup(client);experiment(client);r=client.get('/api/me/export');assert r.status_code==200;assert 'password' not in r.text;assert 'csrf' not in r.text
    assert client.post('/api/me/delete',json={'password':'wrong-password-123'}).status_code==403
    assert client.post('/api/me/delete',json={'password':'correct-horse-123'}).status_code==200
    assert client.get('/api/me').status_code==401
    with db() as c:assert c.execute('SELECT COUNT(*) FROM records').fetchone()[0]==0

def test_engine_repeatable():
    cfg=config();cfg.pop('client_key');assert engine.run(engine.synthetic(),cfg)==engine.run(engine.synthetic(),cfg)

def test_future_data_does_not_change_past_decisions():
    original=engine.synthetic();changed=copy.deepcopy(original);cutoff='2024-05-01'
    for r in changed['rows']:
        if r['date']>cutoff:r['close']=str(float(r['close'])*5)
    cfg=config();cfg.pop('client_key');a,b=engine.run(original,cfg),engine.run(changed,cfg)
    for i in range(3):
        assert [r for r in a['strategies'][i]['curve'] if r['date']<=cutoff]==[r for r in b['strategies'][i]['curve'] if r['date']<=cutoff]
        for signal in a['strategies'][i]['signals']:assert signal['known_through']<signal['date']

def test_balance_and_fee_nonnegative():
    cfg=config();cfg.pop('client_key');p=engine.run(engine.synthetic(),cfg)
    for s in p['strategies']:
        for row in s['curve']:assert float(row['cash'])>=-.000001;assert 0<=row['drawdown']<=1
        final=s['curve'][-1];assets=sum(float(x['value']) for x in s['positions'])
        assert abs(assets+float(final['cash'])-float(s['ending']))<.00001
        assert abs(sum(float(t['fee']) for t in s['trades'])-float(s['fees']))<.0001

def test_flat_market_known_cost():
    ds=engine.synthetic()
    for r in ds['rows']:r['close']='100';r['volume']='100'
    cfg=config(fee_bps=0);cfg.pop('client_key');result=engine.run(ds,cfg)
    for s in result['strategies']:assert float(s['ending'])==10000;assert s['max_drawdown']==0
    assert all(f['train_ic'] is None for f in result['factors'])

def test_higher_fees_reduce_baseline():
    a=config(fee_bps=0);b=config(fee_bps=100);a.pop('client_key');b.pop('client_key')
    assert float(engine.run(engine.synthetic(),a)['strategies'][0]['ending'])>float(engine.run(engine.synthetic(),b)['strategies'][0]['ending'])

def test_stop_exits_without_guaranteeing_threshold():
    c=config(stop_pct=5);c.pop('client_key');r=engine.run(engine.synthetic(),c)['strategies'][2]
    assert r['halted'];assert r['max_drawdown']>.05;assert all(float(p['value'])==0 for p in r['positions'])

def test_ai_success_is_labeled_unverified(client,monkeypatch):
    import app.main as main
    signup(client);r=experiment(client);monkeypatch.setenv('QLAB_AI_KEY','not-a-live-key')
    sent=[]
    class Fake:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,**kw):
            sent.append(kw)
            return __import__('httpx').Response(200,json={'choices':[{'message':{'content':'测试模型正文，并非真实推理。'}}]},request=__import__('httpx').Request('POST',url))
    monkeypatch.setattr(main.httpx,'AsyncClient',lambda **k:Fake())
    out=client.post('/api/tutor',json={'experiment_id':r['id'],'question':'解释结果','use_ai':True,'allow_external':True})
    assert out.status_code==200;assert out.json()['payload']['mode']=='LIVE_AI_UNVERIFIED_TEXT'
    assert 'student@example.com' not in json.dumps(sent)

def test_ai_timeout_retains_original_experiment(client,monkeypatch):
    import app.main as main
    signup(client);r=experiment(client);monkeypatch.setenv('QLAB_AI_KEY','not-a-live-key')
    class Fake:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,*a,**kw):raise __import__('httpx').ReadTimeout('mock timeout')
    monkeypatch.setattr(main.httpx,'AsyncClient',lambda **k:Fake())
    out=client.post('/api/tutor',json={'experiment_id':r['id'],'question':'解释结果','use_ai':True,'allow_external':True})
    assert out.status_code==502;assert client.get('/api/experiments/'+r['id']).status_code==200

def test_market_provider_mock_parses_real_contract_without_claiming_live(client,monkeypatch):
    import app.main as main
    signup(client);monkeypatch.setenv('QLAB_US_KEY','not-a-live-key')
    rows=engine.synthetic('US')['rows'];symbol='US-SAMPLE-01'
    data={r['date']:{'4. close':r['close'],'5. volume':r['volume']} for r in rows if r['symbol']==symbol}
    class Fake:
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def get(self,url,**kw):return __import__('httpx').Response(200,json={'Time Series (Daily)':data},request=__import__('httpx').Request('GET',url))
    monkeypatch.setattr(main.httpx,'AsyncClient',lambda **k:Fake())
    out=client.post('/api/data/fetch',json={'market':'US','symbols':[symbol],'start':'2024-01-01','end':'2024-12-31','rights':'软件协议模拟测试，不是真实API调用'})
    assert out.status_code==201,out.text
    assert out.json()['kind']=='API_REAL_UNADJUSTED'
    assert out.json()['row_count']==180

def test_export_includes_more_than_list_window(client):
    from app.main import save
    u=signup(client)
    for i in range(205):save(u['id'],'feedback','test',{'number':i,'automated':True})
    data=client.get('/api/me/export').json();assert len(data['records']['feedback'])==205

def test_request_size_guard(client):
    assert client.post('/api/auth/login',content=b'x'*6_000_001,headers={'content-type':'application/json'}).status_code==413

def test_malformed_numeric_csv_returns_actionable_error(client):
    signup(client);s=sample_csv().splitlines();row=s[1].split(',');row[2]='abc';s[1]=','.join(row)
    assert client.post('/api/datasets',json=import_payload(csv_content='\n'.join(s))).status_code==422

def test_short_csv_row_is_not_server_error(client):
    signup(client);s=sample_csv().splitlines();s[1]='2024-01-02,CN-SAMPLE-01'
    assert client.post('/api/datasets',json=import_payload(csv_content='\n'.join(s))).status_code==422

def test_tiny_price_is_rejected_before_calculation(client):
    signup(client);s=sample_csv().splitlines();row=s[1].split(',');row[2]='1e-999';s[1]=','.join(row)
    assert client.post('/api/datasets',json=import_payload(csv_content='\n'.join(s))).status_code==422
