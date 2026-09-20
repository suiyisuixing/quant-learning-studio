# Yu.Wei 提交的 R3 接口提案 v0.1

状态：**PROPOSED，未冻结、未实现**。对应 [#14](https://github.com/suiyisuixing/quant-learning-studio/issues/14)和[本人计划](PLAN.md)。这是对[团队接口草案](../../docs/INTERFACES.md)的具体化，供 Yu、Zaixuan、Xiangze、Tianqi 核对；定稿后写回唯一的 `contracts/r3.schema.json` 与团队说明，本文保留为提案历史，不作为第二份运行时权威。

## 1. 公共约定

- 沿用当前 FastAPI、会话/CSRF 和 SQLite；所有私有资源以服务端会话决定 `owner_id`。浏览器只传资源 ID 和用户意图，不能提交可信 owner、approved、余额或计算结果。
- 合同初版版本号拟为 `r3-1`。金额/价格/数量使用十进制字符串，货币只在独立市场 run 中使用 `CNY` 或 `USD`；时间用带时区 ISO 8601，交易日期另设 session_date。标的键是市场＋symbol，不能只凭一个跨市场可能重名的 symbol。
- snapshot、计划内容、结果为不可变版本；run 的活动状态用 `state_version` 乐观并发控制，事件追加保存。模型解释更新不能修改历史交易和指标。
- 共享存储方法由 Zaixuan 实现：按 owner 读取资源、保存版本、在同一事务内比较 state_version/检查幂等键/追加事件/更新状态。Yu 消费此接口，不再建第二个 records/users 库。
- 外部输出不得把整个行情文件、内部用户标识、令牌或任意数据库字段直塞到模型上下文。专门组装只读 PRE_PLAN / POST_RUN_REVIEW 数据对象。

## 2. 实体、字段与权威来源

|实体|最少字段|生成者及校验|
|---|---|---|
|MarketSnapshot|`snapshot_id, owner_id, dataset_id, dataset_version, source_id/version, source_kind, market, currency, symbols, interval, analysis_as_of, visible_range, data_hash, price_basis, calendar_note, rights_status, created_at, limitations`|Yu 创建；数据来源/许可由审核记录支撑；F1/F2 只返回截至可得时点的行和元数据，完整后续数据留在受控后端|
|PlanDraft|`plan_id, version, snapshot_id, schema_version, execution_mode, execution_config, comparison_config, learning_goal, allowed_actions, action_bounds, citations, model_version, prompt_version, kb_version, generation_status`|Tianqi 生成内容；Yu 校验可执行参数；只有模型调用成功且身份/资料有效才标真实 AI，MANUAL/mock 分开|
|PlanApproval|`approval_id, plan_id/version, execution_hash, snapshot_id, dataset_version, rule_version, approved_by, approved_at`|仅用户明确确认触发、服务端创建；版本或影响执行字段变化后旧批准不能开启新 run|
|SandboxRun|`run_id, owner_id, approval_id, plan_id/version/hash, snapshot_id, dataset_version, rule_version, engine_version, status, state_version, cursor, cash, positions, pending_actions, cumulative_fees`|Yu 业务逻辑＋Zaixuan 事务存储；余额/持仓来自计算；首次创建校验全部绑定；不是由前端恢复资金|
|DecisionEvent|`decision_id, run_id, sequence, idempotency_key, requested_at, decision_time, execution_time, action, validated_input, result, fee, before/after_state_version, rule_version`|服务端顺序追加；用户意图和实际成交分开；拒绝记录不能修改资金；尚未成交不填虚构价格|
|SimulationResult|`result_id, version, run_id, end_state_version, plan_ref, dataset_version, engine_version, metrics, ledger_refs, benchmark, factor_effects, limitations`|Yu 确定性计算；指标有值/单位/状态和不可用原因；F4 只读引用；旧结果不被重跑覆盖|
|ReviewReport 交接|`review_id, plan_ref, run_id, result_id/version, decision_refs, metric_refs, evidence_refs, model/prompt/kb_version, generation_status, reflection`|Tianqi 主责；服务端核对所有引用属于该用户/该轮；学生自己填写 reflection，模型不冒充学生|

执行摘要采用稳定序列化的白名单：snapshot/data_version、计划版本、execution_mode、两组 execution/comparison_config、金额、期间、策略、权重、费用、风险、允许动作及其边界、schema/rule_version。Decimal 表达先统一规范，禁止将任意前端对象直接 hash；忽略键顺序不能忽略值变化。展示标题/模型措辞不作为资金权威，计划内容有变仍保存新版本。

## 3. 参数边界与第一版动作

继承 `app/main.py::Config` 的实际参数上限，避免 AI 提出后端不能执行的方案：

|参数|初版合同边界|
|---|---|
|`initial`|虚拟资金 100–1,000,000；不收集真实账户资金|
|`cash_pct`|0–90；明确为百分数，不与 0–1 比例混用|
|`fee_bps`|0–200；按成交金额收取的教学比例费用，不代表所有实际成本|
|`top_n`|1–50，并且不能超过实际可选标的数|
|`rebalance`|1–60 个可用观测日；不把自然日当交易日|
|`stop_pct`|0–50；0 表示关闭，止损不保证亏损上限|
|`weights`|固定顺序 momentum / low_volatility / liquidity；三项非负，合计 1；服务端明确容差|
|期间|必须有足够指标准备日和计算日；日期有序、位于绑定数据版本；既有 CSV 最少 45 个观测日，不以小例子冒充可导入集成数据|

初版沙盘采用用户操作驱动：允许 `BUY` / `SELL`、`ADVANCE`、`PAUSE`、`RESUME`、`FINISH`。策略输出可提供参考配置，执行必须来自已确认计划下的实际用户动作；不在用户不知情时用下一次自动调仓覆盖其持仓。批量基准、单指标、多指标继续由原引擎在研究详情计算，不伪造为用户曾做的操作。

为避免“参数显示了却没有执行”，初版明确 `execution_mode=GUIDED_MANUAL`：`execution_config` 管理实际资金、期间、费用和动作约束；`comparison_config` 沿用上表的因子权重、top_n、rebalance、cash_pct、stop_pct，用于确定性研究比较。后五项不被描述成手动账户已自动执行的调仓/止损。手动账户若设现金下限，使用单独的 `action_bounds.min_cash_pct` 并在实际成交时验证，不暗中改变原 cash_pct 的含义。UI 和 AI 均区分“实际操作规则”“策略参考/研究参数”；不支持的自动策略执行模式直接拒绝。两组配置一起固定在批准版本中，研究结果与实际 run 结果分别命名。

BUY/SELL 只作用于批准的标的和动作边界。输入是数量/意图，下一提供的观测日收盘才决定成交价；现金不足则拒绝该笔，不能用已知的未来价反推“当时刚好能买多少”。第一版不做部分成交、做空、杠杆或跨币种交易。费用/价格口径以批准版本为准。

批准规则内的一次买卖属于 DecisionEvent。改数据、初始金额、策略/费用/风险规则或动作边界属于改计划，须新版本与明确批准，初版开启新 run 保留旧 run；不回写过去的规则。更复杂的中途规则分段仅在后续明确评估后新增。

## 4. 拟定 HTTP 边界

下面路径均为提案，不是当前已经存在的 API。旧 `/api/experiments` 与报告读取继续兼容，并标识旧版记录；没有 F2 的旧实验不得计作完整 R3 链路。

|接口提案|输入|输出/关键检查|负责人|
|---|---|---|---|
|`POST /api/snapshots`|dataset_id、选择的市场/标的/区间、analysis_as_of|snapshot 引用、允许视图；服务端来源/权限/时点检查|Yu；Zaixuan 调用|
|`GET /api/snapshots/{id}`|会话、snapshot_id|当前用途可见的元数据/历史行；不得从 CSV 导出或详情旁路把未来行送入 F2|Yu|
|`POST /api/plans`|snapshot_id、学习目标、允许的初始参数、外发同意|DRAFT 或明确失败；模型/检索真实状态|Tianqi，Yu 校验，Zaixuan 存储|
|`PATCH /api/plans/{id}`|expected_version、候选参数|新 DRAFT 版本；不沿用旧批准|Tianqi/Zaixuan，Yu 校验|
|`POST /api/plans/{id}/approve`|expected_version、execution_hash、client_key|服务端 approval；明确确认、当前版本及所有权|Yu；Zaixuan 确认 UI|
|`POST /api/runs`|approval_id、client_key|READY run；从服务端加载精确计划与资金|Yu|
|`GET /api/runs/{id}`|run_id|状态、当前可见价格、持仓、操作及 next_actions；不预泄后续数据|Yu|
|`POST /api/runs/{id}/actions`|action、允许的参数、expected_state_version、client_key|记录用户意图/控制动作；结果状态和已产生的事件|Yu；Zaixuan UI/存储|
|`GET /api/runs/{id}/result`|run_id|只读 result；未结束时明确未就绪，不拼接另一个实验结果|Yu|
|`POST /api/runs/{id}/reviews`|result_id/version、问题、外发同意|该轮复盘或明确失败，不能用旧回答充当本次成功|Tianqi，Yu 提供上下文|

API 最终命名由四名开发者确认，公共路由只由 Yu 在 `app/main.py` 注册。契约固定后各模块用它做联调，不另造一套 URL/字段来绕开依赖。

## 5. 时间、状态与幂等

1. F1/F2 的 `analysis_as_of` 不可变；价格和证据同时按可获得时间裁切。缺可获得时间的资料不用于“当时已知”，可明确标为事后学习。拥有完整历史文件或重试过历史的用户可能已看过后续结果，要标记限制，不能宣称界面过滤证明人或模型完全未见未来。
2. run 初始 cursor 从该时点开始。BUY/SELL 在当前可见时点提交，ADVANCE 移到下一可用观测日，在规则允许时执行排队动作并计算费用/持仓；缺价不自动填充。事件区分下单时点与成交时点。
3. READY 允许登记首批操作，首次 ADVANCE 转为 RUNNING；PAUSE 从 RUNNING 转为 PAUSED，RESUME 恢复，PAUSED 不接受推进或新交易。控制动作不重复成交；FINISH 只在排队动作已处理或明确取消后生成 COMPLETED 结果，不能偷偷推进未知日期。错误写入回滚后保留原状态或明确 FAILED。
4. 同一用户/资源/动作的相同 client_key＋相同规范化请求返回同一结果；相同 key 不同内容返回 409。重复请求核对幂等结果应先于旧 state_version 拒绝，否则成功请求的网络重试会错误失败。
5. 不同 key 但相同过期 state_version 返回 409；实际事务中比较版本，防止两次 ADVANCE 同时通过。记录幂等结果、事件和账户状态一次提交，进程中断不能只写费用不写持仓。
6. 当前状态能由初始状态＋有序事件重建；服务重启从统一 SQLite 读取。删除/导出账户遵守现有隔离规则；公共仓库不保存真实运行数据库。

建议错误约定：401 未登录，404 资源不存在或不属于本人，409 版本/状态/幂等冲突，422 输入或执行参数不合法，503 必要服务未配置，502/504 外部服务失败/超时。错误返回可定位 code、字段和是否可重试，不包含密钥、他人身份或受限原文。

## 6. F2 与 F4 的不同上下文

|用途|允许输入|禁止混入|
|---|---|---|
|PRE_PLAN|snapshot 的当时视图、学习目标、参数白名单、当时可得且获准的案例/论文、能力限制|未来价格/收益、F3 结果、测评答案、其他用户数据；模型生成的 arbitrary code/SQL 不执行|
|POST_RUN_REVIEW|同一批准计划、实际 DecisionEvent、SimulationResult、基准/费用/风险、获准论文/案例；事后资料带 POST_RUN_LEARNING 标签|另一轮结果、不获准原文、模型自行重算的权威收益、虚构学生心得|

指标引用建议 `result_id + version + metric_path`，操作引用使用真实 decision_id；引用表由后端生成和验证。案例/论文的 source/version/evidence_id 来自 Xiangze/Zaixuan 的统一登记，Tianqi 不自行补标题/页码，也不新建独立来源库。

## 7. 定稿所需交接与完成条件

|负责人|需要对本提案确认的部分|当前状态|
|---|---|---|
|Yu|参数、时序、账本、摘要字段、精确路径和公共注册|本提案由助手按授权编制；实施确认尚未记录|
|Zaixuan|统一存储事务/迁移、旧数据兼容、UI 所需状态及错误字段|待本人核对，未代为同意|
|Xiangze|source/case/content 身份、许可/审核和可得时间、不可比原因|待本人核对，未代为同意|
|Tianqi|PRE_PLAN / POST_RUN_REVIEW 的结构、调用状态、草案/报告版本与引用|待本人核对，已核实账号 tianqih649-glitch；接口意见与实施批准分别记录|

定稿时：在 #14 留明确意见与差异，Yu 更新唯一共享 schema/示例；用同一组合成输入让四个模块各做输入输出校验；再以获准真实数据/模型走演示。schema、数据库和 API 均未因本提案存在而自动完成。
