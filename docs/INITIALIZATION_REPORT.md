# R3 初始化执行记录

记录的是本次执行，不是产品四项完成报告。最终 PR/HEAD 与远端 CI 会记录在 Yu 的角色 Issue #2 和 R3-BOOT 任务中。

- 同一个 public 仓库：https://github.com/suiyisuixing/quant-learning-studio 。main 基线为 57cf025d0a06aff2a936b628b784c8d4975e368f；R3 分支为 bootstrap/r3-collaboration，交 Yu 最终合并。分支内新名册不能冒充已激活的 main。
- 当前认证 suiyisuixing / 245487910；精确用户查询：3165349449-tech / 330387285，trave1er999 / 243565339。本人加入确认未提交，两人的 Issue 可分配性 API 均返回 404，未邀请/扩大权限。Tianqi 为 AWAITING_LOGIN。
- 恰好七人、四开发三非开发。后三人不需要 GitHub，可交资料/真人测试模板文件或 Issue；没有建立表单。
- R3 原件已收到，37 个文件节提取，JSON 为实际 JSON；包 README 写入 docs/prompt-pack，网站根 README 保留实际运行方式。七份完整个人提示词、四份 runtime 提示词、七份本人待填计划已建立；没有代替本人填写成果或批准。
- 认可源码包 SHA256 为 312ebb483389effa68403610f082f8f720dfc342b7adb031fb0add95cec7c6fd，与 R3 完全一致。29 个白名单文件按字节导入，保留 JavaScript/CSS、FastAPI、SQLite。源码、UI、依赖与原有产品测试未改写；两个合成 CSV 以精确 hash 白名单公开。旧包 evidence、日志/截图/测试报告和旧权限规则不导入，原始说明仅作历史来源。
- 已在项目 .venv 安装源码锁定依赖，没有修改全局 Python 或 Conda；凭据清空，测试使用新临时数据库。未读取生产数据，没有真实 API 或付费调用。
- 本次重新执行：源产品的 58 项测试通过；当时治理 48 项通过，共 106；随后新增 2 项 CSV 白名单用例，治理检查已重新运行 50 项通过；最终 PR CI 还会验证合计 108 项。10 个本地 HTTP 并发场景通过，自动账户数不计真人。前端语法检查通过。
- 本次 macOS 安装的 Chrome 真实 loopback HTTP 浏览器检查 30 项通过，page_errors=[]；包含注册、计算、规则讲解、报告重开、桌面和 390px 窄屏。人工查看本轮 desktop-home 与 mobile-results 截图；未重画 UI。窄屏不是物理手机/Safari 测试。旧截图没有当作本轮证据。
- main 当前要求 bootstrap-checks/trusted-scope、strict 更新、讨论解决；enforce_admins=true、禁止强推/删除。审批数为 0、CODEOWNERS 不强制自审，只有 Yu 有合并权；owner 能修改仓库设置这一所有权能力没有被假装取消。此前验证 PR #9 已关闭未合并，真实 BLOCKED→CLEAN 证据只算旧 bootstrap 保护验证，不充当 R3 成员 Fork 测试。
- R3 范围检查新增七人/四开发约束、旧姓名去重、非开发代码拒绝、实际 head/policy 绑定与树元数据模式检查。R3 在合并前只有本地/PR 检查证据；不能声称 main 已运行 R3 特权门禁或真实成员 Fork 已通过。

## F1—F4 真实缺口
|功能|导入基线|R3 验收状态与后续|
|---|---|---|
|F1 市场数据显示|合成数据、CSV 导入与市场 API 适配|NOT_RUN：真实授权数据/快照未验收，snapshot/as_of 链需补齐|
|F2 演练前 AI 策划|当前没有独立前策划/批准流程|NOT_RUN：开发检索、DRAFT、精确版本校验和用户确认；真实 DeepSeek 未调用|
|F3 可操作沙盘|已有三方法批量回测|NOT_RUN：需用户操作、时间推进/暂停、decision 账本与批准计划绑定|
|F4 问题分析与复盘|已有模拟后 tutor、规则讲解和报告|NOT_RUN：需论文检索、同一 plan/run/result、操作/指标定位与真实 AI 复盘|

现有测试只说明导入基线行为，不能将规则回答算 DeepSeek，将批量回测算完成交互沙盘，或将自动账户算真人。

## 待完成与下一步
Yu 审阅并最终合并 R3 治理 PR；四名开发者填写产品 PLAN，Yu 批准后才实施。Tianqi 补本人确切 GitHub login；两个已知成员可在加入 Issue 作本人确认后重新核对可分配性。三名资料成员交简单计划、认领不重复批次。后续真实数据/API 许可与预算另行确认，不需要现在公开密钥。无公网部署、购买服务或协作者邀请。
