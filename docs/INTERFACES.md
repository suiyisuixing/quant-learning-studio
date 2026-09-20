# F1—F4统一接口与状态：实施合同草案

先由4名开发者Yu.Wei、Zaixuan.Ji、Xiangze.Zhu、Tianqi.Hao结合现有代码定稿。这里是最少概念，不要求另造一套重量级系统或每个概念一张新表。沿用已有可靠实体可适配，版本和绑定语义不能丢。

|记录|最少包含|关键约束|
|---|---|---|
|MarketSnapshot|snapshot_id、owner、对象/市场/币种、来源类型、dataset_version、数据区间、analysis_as_of、可见行范围、抓取/更新时刻、口径/限制|数据身份及时间边界来自服务端；F2不能读取后续行情或收益|
|CaseRecord / LearningContent|case_id/content_id、version、市场/对象/期间、来源ID、资料类型、适用限制、许可/审核状态、原文或原创说明|Xiangze开发结构/查询/校验；公开基金资料与自建教学模拟不混淆；只取获准内容，不重复造论文库|
|EvidenceChunk|evidence_id、source_id/version、原文与locator、发布时间/可获得时间、用途、审核/许可状态|缺时间不能擅自用于“当时已知证据”；停用和权限检查贯穿访问|
|PlanDraft|plan_id、version、snapshot_id、学习目标、允许策略/指标/参数草案、理由、citations、model/prompt/kb版本、生成状态|F2出DRAFT；草案不直接写入模拟账户|
|PlanApproval|plan_id/version/hash、用户确认的精确参数、批准者/时刻、校验结果|服务器产生；改变影响执行的输入就新版本，不能继承旧批准|
|SandboxRun|run_id、owner、approved_plan引用、dataset/rule版本、初始资金、模拟时钟、状态|先验证身份/批准；不接真实资金；支持暂停/继续、重试幂等|
|DecisionEvent|decision_id、run_id、sequence、simulation_time、用户动作/参数、校验/执行结果、费用|顺序、时间单调；重复请求不重复记账；改变规则只影响后续|
|SimulationResult|result_id/version、run_id、指标引用、资金/持仓/费用账本、基准、方法/因子效果、限制|数字由确定性引擎；不可混入其他run；修改参数重跑不覆盖原结果|
|ReviewReport|review_id、run_id、result_id/version、原始plan、decision/metric引用、发现、证据、下一练习建议、模型/提示词/资料版本、用户反思|F4事后生成且可回看；不反写原计划，不虚构个人反思|

## 状态转换
数据选择完成 → 生成草案DRAFT → 用户编辑/服务器校验 → 用户批准APPROVED → 创建READY沙盘 → RUNNING/PAUSED → COMPLETED或明确FAILED/CANCELLED → REVIEW_READY → REVIEWED。

AI请求另有QUEUED/RUNNING/SUCCEEDED/FAILED/CANCELLED等状态，由实际适配器定名；“写了报告标题”不算成功。需要资料但未命中时返回证据不足，不偷换为无检索成功。

F3允许手动练习但须标MANUAL_PLAN；没有F2的run不能作为本轮完整演示通过。计划回滚/再次练习建立新分支记录而不是更改历史。一个plan可以创建多个独立run；一个报告只绑定明确run/result版本。

## 最少接口行为（URL沿用实际项目，不强制照抄）
- 读取/筛选中美案例与教学内容、返回来源和不可比原因（Xiangze）；读取/选择市场数据并保存snapshot（Yu）；使用原UI展示（Zaixuan）。
- 基于snapshot请求F2草案、读取草案、更新候选参数、明确批准精确版本。
- 从批准计划创建沙盘、提交操作、推进/暂停/恢复、结束、读取结果。
- 从run请求F4复盘、读取引用、保存用户心得、导出、重新读取。

每个写入接口做身份检查、输入校验、必要幂等；客户端提供的审批状态/金额结果/quote字符串不是权威。时间裁切和文件权限在服务端，不只藏前端字段。

## 记录示例的使用原则
开发fixture可用合成输入，但注明来源类型、用途和时间。不能把示例中的plan_id、model输出或PASS复制为实际证据。DeepSeek输出schema由Tianqi与Yu商定，设置固定字段与枚举，证据标题等由真实登记表渲染。

一次跨模块对接至少验证：F1的snapshot与F2引用相同；F3读到的是用户批准版本；F3操作可在F4定位；报告保存重开仍指向该次运行。
