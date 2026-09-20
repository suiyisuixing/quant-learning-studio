# QuantLab｜R3：四人开发、三人资料与真人测试

本页保留原始提示词包编写时点的说明。2026-09-20 用户已补充 Tianqi 的账号；当前账号与执行状态见 [实际名册](../TEAM_ROSTER.md)，成员执行入口见 [START_HERE](../../prompts/START_HERE.md)。下文的“待提供”不覆盖后续已核实记录。

本包整体替代R2中的活跃人员安排、加入方式与个人提示词；产品四项功能、演示标准和已认可UI不变。本包是执行提示词与计划，不代表GitHub建库、成员验证、邀请、权限设置或网站测试已经发生。

## 先用哪份
- 给ChatGPTwork：先读 `prompts/START_HERE.md`，执行 `prompts/00_CHATGPTWORK_BOOTSTRAP.md`。
- 统一身份与角色：`docs/TEAM_ROSTER.md` 和 `templates/MEMBER_ROSTER.example.json`。
- 四位开发者：各读 `prompts/members/` 对应文件，按 `templates/MEMBER_PLAN.md` 填写开发计划。
- 三位非开发成员：各读自己的资料与测试提示词，按 `templates/RESEARCH_TEST_PLAN.md` 填写；可通过文件、Issue或获准表单交付，不强制Fork、PR或安装开发环境。
- 实现要求：`prompts/01_PRODUCT_MASTER.md`、`docs/FOUR_FEATURES.md`、`docs/INTERFACES.md`、`docs/MODULE_BOUNDARIES.md`。
- 演示：`docs/DEMO_SCRIPT.md` 和 `templates/DEMO_EVIDENCE.md`。

## 当前七人
|成员|是否开发|GitHub login登记|工作|
|---|---|---|---|
|Yu.Wei|是，组长|suiyisuixing，沿用预期owner，执行时核对登录|数据、量化、沙盘、费用风险、公共接口、整合|
|Zaixuan.Ji|是|3165349449-tech，用户提供截图并确认对应关系|保留UI、账户数据库、论文库基础与前后端联调|
|Xiangze.Zhu|是|trave1er999，用户明确提供，字符为数字1|中美案例与学习内容模块的代码、数据结构、查询比较、内容校验与测试|
|Tianqi.Hao|是|待提供|DeepSeek、查询检索、F2前策划、F4复盘、进度与报告|
|Yifan.Mao|否|不要求先提供GitHub|找论文、资料卡、真人测试、问题与复测|
|Guanjie.Xue|否|不要求先提供GitHub|找论文、资料卡、真人测试、问题与复测|
|Yuntao.Min|否|不要求先提供GitHub|找论文、资料卡、真人测试、问题与复测|

用户给出的姓名/账号对应关系已登记，但没有查询或伪造GitHub用户ID，也没有认定成员已加入。Xiangze.Zhu是当前显示名，旧任务文件写作Xingze.Zhu；按同一人保留别名，不新增第八人。确切迁移见TEAM_ROSTER。

## 产品不变
**F1 市场数据的显示 → F2 人工智能的策划和分析 → 用户确认 → F3 模拟经营的沙盘演练 → F4 最后的人工智能分析问题与复盘。**

四项都要实际实现并演示；F2是演练前，F4是演练后，不能合并。保留认可的QuantLab独立网站UI，不重新设计、不换框架、不回旧ai-workbench。

## 协作与公开
沿用公开上游、开发者在Fork/任务分支提交PR、Yu.Wei审核并最终合并。资料成员不参与代码开发，提交资料/反馈后由开发者核查和入库；本人贡献与代录操作分开记录。不得因此给后三人布置写代码、自动化测试、服务器部署或CI维护。

不授予组员上游直接写入/管理权限；也不声称能够阻止任何人修改自己的副本。真正保护的是正式仓库接纳哪些修改。公开GitHub和公开Fork不存密钥、个人数据库、受限论文全文/切片/索引、私密用户资料或无许可行情。

本包README是提示词包说明，不可覆盖实际网站根README中的启动方式。已有仓库应增量更新活跃文件与Issue，保留有效代码、历史提交和真实证据。

## 修订范围
本次只更正人员类型、已提供账号及协作流程。`docs/FOUR_FEATURES.md`、UI基线、完整演示脚本和四份网站AI提示词沿用R2原文；AI文件内部R2-draft是其内容版本，不是过时的人员指令。它们未重新运行或验证。
