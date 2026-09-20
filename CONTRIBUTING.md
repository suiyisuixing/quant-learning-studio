# 参与项目

先看 [名册](docs/TEAM_ROSTER.md) 和 [加入 Issue](https://github.com/suiyisuixing/quant-learning-studio/issues/1)。开发者使用自己的 Fork；不要申请上游写权限。Yu 使用 owner 任务分支并最终审查合并。

每位成员领取完整个人提示词并按 [全任务执行规则](prompts/EXECUTE_TO_COMPLETION.md) 连续工作；不按周排期，也不把首个 PR 当作本人全部交付。开发顺序：填写覆盖全部任务的本人 plans/<role>/PLAN.md → PLAN-only PR → Yu 合并并记录 PLAN blob SHA/获准路径 → 模块 PR → 检查、人工审阅、Yu 合并。应用路径依赖认可源码；当前没有产品实施批准。共享接口用 [接口需求模板](templates/INTERFACE_REQUEST.md) 协调，不在成员 PR 改权限表。

Yifan、Guanjie、Yuntao 使用 [资料/真人测试计划](templates/RESEARCH_TEST_PLAN.md) 与 [交付记录](templates/RESEARCH_TEST_DELIVERY.md)，交文件或可选 Issue 即可，不要求注册 GitHub 或提交 PR。没有建立表单。开发者核查、匿名化、保留作者后代录；安全问题受限交 Yu，不公开利用细节。

提交前检查当前 diff 和历史、真实测试及资料许可。不要提交数据库、受限全文、个人身份或付费凭据。代码测试在 GitHub 托管临时 runner 使用只读 token；可信范围门禁只处理元数据，不执行 PR 代码。

范围通过不代表代码安全或产品验收。具体配置与 owner 合并安排见 [访问模型](docs/ACCESS_MODEL.md)。
