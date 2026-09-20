"""Offline Chromium UI integration with real in-process FastAPI TestClient.
The environment blocks browser URL navigation. This harness injects the shipped
HTML/CSS/JS into about:blank, replaces ONLY transport with a test bridge, and
exercises the real backend. Not a network/Safari/real-user acceptance test.
"""
import os,json,uuid,re,base64,tempfile
from pathlib import Path
os.environ['QLAB_DB']=str(Path(tempfile.mkdtemp(prefix='qlab-ui-'))/'ui.db')
from fastapi.testclient import TestClient
from app.main import app,initialize,RATE
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
initialize();RATE.clear();results=[];errors=[]
email='browser-'+uuid.uuid4().hex[:10]+'@example.com';password='Browser-Test-Password-2026'

def check(name,condition,detail=''):
    results.append({'name':name,'pass':bool(condition),'detail':detail});assert condition,(name,detail)

def render_page(page,route,title,filename=None):
    page.evaluate('(r)=>{location.hash="#/"+r}',route)
    page.get_by_role('heading',name=title,exact=False).first.wait_for(timeout=12000)
    page.wait_for_timeout(130)
    width=page.evaluate('({scroll:document.documentElement.scrollWidth, viewport:window.innerWidth})')
    check('no-overflow:'+route,width['scroll']<=width['viewport'],str(width))
    if filename:page.screenshot(path=str(OUT/filename),full_page=True)

def mount(context,client,route='welcome'):
    page=context.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
    def bridge(payload):
        res=client.request(payload['method'],payload['path'],headers=payload.get('headers',{}),content=payload.get('body'))
        return {'status':res.status_code,'body':res.text}
    page.expose_function('backendForTest',bridge)
    source=(ROOT/'web/index.html').read_text();source=re.sub(r'<link[^>]+>|<script.*?</script>','',source)
    page.set_content(source)
    page.add_style_tag(content=(ROOT/'web/style.css').read_text())
    page.evaluate('''()=>{window.fetch=async(url,opt={})=>{const result=await window.backendForTest({path:url,method:opt.method||'GET',headers:opt.headers||{},body:opt.body});return {ok:result.status>=200&&result.status<300,status:result.status,json:async()=>JSON.parse(result.body)};};}''')
    page.evaluate('(r)=>{location.hash="#/"+r}',route)
    js=(ROOT/'web/app.js').read_text();favicon='data:image/svg+xml;base64,'+base64.b64encode((ROOT/'web/favicon.svg').read_bytes()).decode()
    js=js.replace('/assets/favicon.svg',favicon)
    page.add_script_tag(content=js,type='module')
    return page

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
    client=TestClient(app);page=mount(context,client)
    page.get_by_role('heading',name='看懂一次选择，').wait_for();page.screenshot(path=str(OUT/'desktop-welcome.png'),full_page=True)
    page.locator('#landing-risk').fill('50');check('landing-risk-calculation',page.locator('#landing-loss').inner_text()=='500')
    page.get_by_role('link',name='开始我的第一堂实验').click();page.locator('#name').fill('课程体验同学');page.locator('#email').fill(email);page.locator('#password').fill(password)
    page.get_by_role('button',name='创建账户并开始').click();page.get_by_role('heading',name='课程体验同学，今天').wait_for()
    check('real-backend-registration',page.locator('.profile-name').inner_text()=='课程体验同学')
    render_page(page,'home','课程体验同学，今天','desktop-home.png')
    render_page(page,'lab','做一次有依据的比较','desktop-lab.png')
    page.locator('#reason').fill('我想比较多指标和简单分配，也想知道过程中会跌多少。')
    page.get_by_role('button',name='运行三种方法').click();page.get_by_role('heading',name='同一个起点，三条路径').wait_for(timeout=15000)
    check('actual-simulation',page.locator('svg.chart').count()==1)
    expquery=page.url.split('?')[1];check('real-ledger-ui','买卖记录' in page.locator('body').inner_text())
    page.screenshot(path=str(OUT/'desktop-results.png'),full_page=True)
    page.get_by_role('link',name='解释与复盘').click();page.get_by_role('heading',name='这次实验，你想弄懂什么？').wait_for()
    page.locator('#question').fill('最大回撤是什么意思？我这次有什么风险？');page.get_by_role('button',name='发送问题').click()
    page.get_by_text('规则讲解 · 不是AI',exact=True).wait_for(timeout=10000)
    check('no-fake-ai',page.get_by_text('规则讲解 · 不是AI',exact=True).count()==1)
    page.screenshot(path=str(OUT/'desktop-tutor.png'),full_page=True)
    page.locator('#reflection').fill('自动化测试生成的反思，仅验证保存功能，不是学生学习证据。')
    page.get_by_role('button',name='保存学习报告').click();page.get_by_role('heading',name='我的实验结果').wait_for()
    reportquery=page.url.split('?')[1];check('report-saved',page.get_by_text('自动化测试生成的反思，仅验证保存功能，不是学生学习证据。',exact=True).count()==1)
    link=page.get_by_role('link',name='Markdown',exact=True).get_attribute('href');download=client.get(link)
    check('backend-report-download','自动化测试生成的反思' in download.text)
    render_page(page,'learn','一点点，弄明白。','desktop-learning.png')
    page.locator('form[data-lesson=risk] input[value="1"]').check();page.locator('form[data-lesson=risk] button[type=submit]').click()
    page.get_by_text('回答正确。',exact=False).wait_for();check('quiz-calculated', '25%' in page.locator('#answer-risk').inner_text())
    render_page(page,'compare','先分清资料，再比较方法','desktop-compare.png')
    page.get_by_role('button',name='运行两份合成样本').click();page.get_by_text('两份教学实验已完成并保存',exact=True).wait_for(timeout=15000)
    check('cross-market-teaching-runs',page.locator('.case-content').count()==2)
    render_page(page,'data','知道数据从哪里来。','desktop-data.png')
    check('api-disconnected-honest',page.get_by_text('未配置',exact=True).count()>=2)
    render_page(page,'reports','每一次理解，都有迹可循。','desktop-reports.png')
    page.locator('#report-search').fill('不存在的报告');check('search-working',page.locator('#search-empty').is_visible());page.locator('#report-search').fill('')
    render_page(page,'feedback','让下一次体验，更清楚一点。','desktop-feedback.png')
    page.locator('#task').fill('自动化测试任务，不计入真人测试');page.locator('input[name=rating][value="4"]').check();page.locator('#comment').fill('自动化反馈测试，不是真人反馈。');page.locator('input[name=consent]').check()
    page.get_by_role('button',name='提交反馈').click();page.get_by_text('已保存这次真实反馈，感谢说明具体问题').wait_for();check('feedback-write',True)
    context2=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
    client2=TestClient(app);mobile=mount(context2,client2,'auth?mode=login')
    mobile.locator('#email').fill(email);mobile.locator('#password').fill(password)
    mobile.get_by_role('button',name='登录并继续').click();mobile.get_by_role('heading',name='课程体验同学，今天').wait_for()
    check('persistent-second-context-login',mobile.get_by_role('heading',name='课程体验同学，今天').count()==1)
    for route,title,file in [('home','课程体验同学，今天','mobile-home.png'),('lab','做一次有依据的比较','mobile-lab.png'),('results?'+expquery,'我的风险比较','mobile-results.png'),('tutor?'+expquery,'这次实验，你想弄懂什么？','mobile-tutor.png'),('data','知道数据从哪里来。','mobile-data.png')]:
        render_page(mobile,route,title,file)
    mobile.get_by_role('button',name='打开导航').click();check('mobile-nav', 'open' in mobile.locator('#sidebar').get_attribute('class'))
    mobile.get_by_role('button',name='关闭导航').click()
    render_page(mobile,'report?'+reportquery,'我的风险学习报告')
    check('report-persists-after-new-login','自动化测试生成的反思' in mobile.locator('body').inner_text())
    check('browser-page-errors',not errors,str(errors))
    context.close();context2.close();client.close();client2.close();browser.close()
OUT.joinpath('browser-results.json').write_text(json.dumps({'engine':'offline system Chromium + real FastAPI TestClient via test-only transport bridge','network_e2e':'BLOCKED_BY_ENVIRONMENT_POLICY','human_testers':0,'tests':results,'page_errors':errors,'passed':sum(x['pass'] for x in results)},ensure_ascii=False,indent=2))
print(json.dumps({'passed':len(results),'page_errors':errors,'human_testers':0,'transport':'in-process TestClient, not real browser HTTP'},ensure_ascii=False))
