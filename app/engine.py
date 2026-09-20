"""Teaching-only causal daily-close portfolio engine; not a broker simulator.

Signals use bars strictly before execution. Orders execute at the next supplied
close, with fractional units and user-declared proportional turnover costs.
Cash has zero yield. No leverage/shorting/tax calendar/queue guarantees.
"""
from __future__ import annotations
import csv, io, math, random, hashlib, json, statistics
from datetime import date, timedelta
from decimal import Decimal, localcontext, InvalidOperation

VERSION = 'qlab-teaching-close-1.0'
FACTORS = ['momentum', 'low_volatility', 'liquidity']
D = lambda v: Decimal(str(v))

def money(v):
    return str(D(v).quantize(Decimal('0.000001')))

def synthetic(market='CN'):
    rng = random.Random(20260917 + (market == 'US'))
    days, cursor = [], date(2024, 1, 2)
    while len(days) < 180:
        if cursor.weekday() < 5: days.append(cursor.isoformat())
        cursor += timedelta(days=1)
    rows=[]
    for s in range(6):
        p=30+s*15
        for t, day in enumerate(days):
            shared = .002*math.sin(t/11) - (.014 if 65<t<85 else 0)
            p=max(1,p*(1+shared+.0003*(s-2)+rng.gauss(0,.009+.002*s)))
            rows.append({'date':day,'symbol':f'{market}-SAMPLE-{s+1:02}', 'close':f'{p:.4f}',
                         'volume':str(rng.randrange(10000,200000)), 'market':market,
                         'currency':'CNY' if market=='CN' else 'USD'})
    return {'id':f'sample-{market.lower()}', 'name':f'{"中国" if market=="CN" else "美国"}组教学样本（合成）',
            'kind':'SYNTHETIC','market':market,'currency':'CNY' if market=='CN' else 'USD',
            'source':'程序按固定随机种子生成，不是真实公司、行情或基金业绩',
            'source_url':None,'rights':'项目自制教学样本', 'rows':rows,
            'calendar_note':'工作日示例，不对应真实交易所休市日', 'created_at':'2026-09-17'}

def normalize_csv(content:str, market:str, currency:str):
    if len(content.encode('utf-8'))>5_000_000: raise ValueError('CSV超过5 MB限制')
    reader=csv.DictReader(io.StringIO(content.lstrip('\ufeff')))
    needed={'date','symbol','close','volume'}
    if not reader.fieldnames or not needed<=set(reader.fieldnames):
        raise ValueError('CSV需要 date,symbol,close,volume 四列')
    rows,seen=[],set()
    for raw in reader:
        if len(rows)>=50000: raise ValueError('最多导入50,000行')
        if any(not isinstance(raw.get(k),str) or not raw[k].strip() for k in needed):raise ValueError('CSV存在空字段或缺少列值')
        day=date.fromisoformat(raw['date']).isoformat()
        if day>date.today().isoformat(): raise ValueError('行情日期不能在未来')
        symbol=raw['symbol'].strip().upper()
        if not symbol or len(symbol)>32 or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._' for c in symbol):
            raise ValueError('代码只接受32位以内的字母、数字、点、横线或下划线')
        try:p,v=D(raw['close']),D(raw['volume'])
        except (InvalidOperation,ValueError):raise ValueError('价格和成交量必须为有效数字')
        if not p.is_finite() or not v.is_finite() or p<D('0.000001') or v<0 or p>10**9 or v>10**18:
            raise ValueError('价格须在0.000001至10亿之间、成交量非负，且不能是NaN或无限值')
        if (day,symbol) in seen: raise ValueError(f'重复记录：{day} / {symbol}')
        seen.add((day,symbol))
        if raw.get('market') and raw['market']!=market: raise ValueError('CSV市场不一致')
        if raw.get('currency') and raw['currency']!=currency: raise ValueError('CSV币种不一致')
        rows.append({'date':day,'symbol':symbol,'close':str(p),'volume':str(v), 'market':market,'currency':currency})
    symbols=sorted({r['symbol'] for r in rows})
    if not rows or len(symbols)>50: raise ValueError('需要非空数据，最多50个标的')
    counts={s:{r['date'] for r in rows if r['symbol']==s} for s in symbols}
    days=counts[symbols[0]]
    if any(d!=days for d in counts.values()):
        raise ValueError('本教学引擎要求所有标的日期一致；请补充真实缺失记录或缩小样本，不会自动填充')
    if len(days)<45: raise ValueError('至少45个完整观测日，前20日用于指标准备')
    return sorted(rows,key=lambda r:(r['date'],r['symbol']))

def ranks(values):
    ordered=sorted(values)
    return [(sum(v<x for v in ordered)+(sum(v==x for v in ordered)-1)/2) for x in values]

def correlation(a,b):
    if len(a)<3:return None
    a,b=ranks(a),ranks(b)
    ma,mb=statistics.mean(a),statistics.mean(b)
    va=sum((v-ma)**2 for v in a);vb=sum((v-mb)**2 for v in b)
    if va<1e-15 or vb<1e-15:return None
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)

def features(series, index):
    # index is execution day: not allowed to read this day's data for signals.
    history=series[index-20:index]
    prices=[float(r['close']) for r in history]
    rs=[prices[i]/prices[i-1]-1 for i in range(1,len(prices))]
    return [prices[-1]/prices[0]-1,-statistics.stdev(rs),statistics.mean(float(r['volume']) for r in history)]

def prepare(dataset):
    symbols=sorted({r['symbol'] for r in dataset['rows']})
    series={s:sorted([r for r in dataset['rows'] if r['symbol']==s],key=lambda r:r['date']) for s in symbols}
    days=[r['date'] for r in series[symbols[0]]]
    if any([r['date'] for r in rs]!=days for rs in series.values()):raise ValueError('数据日期不完整')
    return symbols,series,days

def simulation(series,days,symbols,start,end,config,method,weights):
    initial=D(config['initial']); cash=initial; qty={s:D(0) for s in symbols}
    fee_rate=D(config['fee_bps'])/10000; reserve=D(config['cash_pct'])/100
    peak=initial; prev=initial; previous_dd=D(0); halted=False; totalfees=D(0); trades=[]; curve=[];signals=[]
    top=min(config['top_n'],len(symbols)); last_targets={}
    for i in range(start,end+1):
        prices={s:D(series[s][i]['close']) for s in symbols}
        value=cash+sum(qty[s]*prices[s] for s in symbols)
        trigger=(method!='baseline' and config['stop_pct']>0 and previous_dd>=D(config['stop_pct'])/100 and not halted)
        if trigger:halted=True
        if (i-start)%config['rebalance']==0 or trigger:
            if method=='baseline': chosen=symbols; scores={s:0 for s in symbols}
            else:
                fs={s:features(series[s],i) for s in symbols}
                normalized={}
                for k in range(3):
                    rr=ranks([fs[s][k] for s in symbols]);scale=max(1,len(symbols)-1)
                    for s,r in zip(symbols,rr):normalized.setdefault(s,[]).append(r/scale)
                w=[1,0,0] if method=='single' else weights
                scores={s:sum(w[k]*normalized[s][k] for k in range(3)) for s in symbols}
                chosen=sorted(symbols,key=lambda s:(-scores[s],s))[:top]
            targets={s:(D(1)-reserve)/len(chosen) if s in chosen and not halted else D(0) for s in symbols}
            # Solve proportional turnover fee for net investable equity; no hidden fee cash deficit.
            lo,hi=D(0),value
            for _ in range(70):
                net=(lo+hi)/2
                costs=sum(abs(net*targets[s]-qty[s]*prices[s]) for s in symbols)*fee_rate
                if net+costs>value:hi=net
                else:lo=net
            net=lo; newqty={s:net*targets[s]/prices[s] for s in symbols}
            fee=sum(abs((newqty[s]-qty[s])*prices[s]) for s in symbols)*fee_rate
            for s in symbols:
                delta=newqty[s]-qty[s]
                if abs(delta*prices[s])>D('.000001'):
                    trades.append({'date':days[i],'symbol':s,'side':'买入' if delta>0 else '卖出',
                                   'quantity':money(abs(delta)), 'price':money(prices[s]),
                                   'notional':money(abs(delta*prices[s])), 'fee':money(abs(delta*prices[s])*fee_rate)})
            cash=value-fee-sum(newqty[s]*prices[s] for s in symbols);qty=newqty
            totalfees+=fee; value=cash+sum(qty[s]*prices[s] for s in symbols)
            last_targets={s:float(targets[s]) for s in symbols}
            signals.append({'date':days[i],'known_through':days[i-1], 'selected':[] if halted else chosen,
                            'scores':{s:round(scores[s],6) for s in symbols}, 'halted':halted})
        peak=max(peak,value);dd=(peak-value)/peak;previous_dd=dd
        curve.append({'date':days[i], 'equity':money(value),'cash':money(cash),'drawdown':float(dd),
                      'return':float(value/prev-1)})
        prev=value
    maxdd=max(r['drawdown'] for r in curve)
    returns=[r['return'] for r in curve]; vol=statistics.stdev(returns)*math.sqrt(252) if len(returns)>1 else 0
    split=max(1,int(len(curve)*.7));teststart=D(curve[split-1]['equity']);testend=D(curve[-1]['equity'])
    return {'method':method,'ending':money(prev),'profit':money(prev-initial),'total_return':float(prev/initial-1),
            'max_drawdown':maxdd,'fees':money(totalfees),'volatility':vol,'trades':trades,'curve':curve,
            'signals':signals,'trade_count':len(trades), 'train_end':curve[split-1]['date'],
            'test_start':curve[split]['date'] if split<len(curve) else None,'test_return':float(testend/teststart-1),
            'positions':[{'symbol':s,'quantity':money(qty[s]),'value':money(qty[s]*D(series[s][end]['close']))} for s in symbols],
            'halted':halted,'target_weights':last_targets}

def run(dataset,config):
    symbols,series,days=prepare(dataset)
    start=max(20,next((i for i,d in enumerate(days) if d>=config.get('start',days[0])),len(days)))
    end=max((i for i,d in enumerate(days) if d<=config.get('end',days[-1])),default=-1)
    if end-start<19:raise ValueError('需要至少20个计算日，以及之前20个完整准备日；请扩大时间范围')
    weights=[float(v) for v in config['weights']]
    if not math.isclose(sum(weights),1,abs_tol=1e-8):raise ValueError('三个指标权重之和必须是100%')
    with localcontext() as ctx:
        ctx.prec=36
        outputs=[simulation(series,days,symbols,start,end,config,m,weights) for m in ['baseline','single','multi']]
    per_factor=[]
    split=start+int((end-start+1)*.7)
    for k,f in enumerate(FACTORS):
        train,test=[],[]
        for i in range(start,end):
            fs=[features(series[s],i)[k] for s in symbols]
            # label is future return only used here for evaluation, never in features.
            labels=[float(D(series[s][i+1]['close'])/D(series[s][i]['close'])-1) for s in symbols]
            c=correlation(fs,labels)
            if c is not None:
                if i+1<split:train.append(c)
                elif i>=split:test.append(c)  # exclude the label crossing the train/test boundary
        per_factor.append({'id':f,'train_ic':statistics.mean(train) if train else None,
                           'test_ic':statistics.mean(test) if test else None,'train_count':len(train),'test_count':len(test),
                           'meaning':'排名与下一观测日收益的相关性；不代表因果或显著性'})
    sha=hashlib.sha256(json.dumps(dataset['rows'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {'engine':VERSION,'dataset_id':dataset['id'],'dataset_name':dataset['name'],'data_kind':dataset['kind'],
            'market':dataset['market'],'currency':dataset['currency'],'source':dataset['source'],
            'source_url':dataset.get('source_url'),'data_sha256':sha,'config':config,'start':days[start],'end':days[end],
            'observations':end-start+1,'symbols':symbols,'strategies':outputs,'factors':per_factor,
            'limitations':['教学模型，非真实基金业绩、投资建议或未来预测',
                '按前一观测日及更早信息决策，下一观测日收盘参考成交；使用小数份额',
                '费用按每笔换手金额收取；不模拟真实涨跌停、停牌队列、税费、融资与交易所节假日',
                '现金收益设为0；止损由上一日回撤触发、下一日收盘退出且本轮不再入场，不保证亏损上限',
                '按70%/30%作时间分段展示，参数未自动训练；反复看后段改参数会污染检验',
                '收益按各数据集本币报告；跨市场图表仅归一化，不含汇率，不作国家优劣结论',
                '当前样本选择可能包含幸存者偏差；数据授权与真实私募代表性需另外验证']}
