# 共用接口 v1 草案（等待 Yu 定稿）

本目录当前为输入输出设计，未伪装成已经实现的 API。所有字段的来源、必填性、空值原因、权限与版本语义，须在认可源码到位后由 Yu 联合各模块负责人定稿。

| 合同 | 生产方 | 使用方 | 内容 |
|---|---|---|---|
| ExperimentSummary | Yu | UI、Tianqi | id、服务端 owner_id、market/currency、as_of、dataset/strategy/rule 版本、参数、确定性 results、费用/风险、来源状态、限制 |
| SourceRecord | Zaixuan；Xingze 审核 | 检索、资料界面 | source_id/version、标题作者年、DOI/原始 URL、地区期间样本、类型、许可/可发送/可展示、审核状态、hash |
| EvidenceChunk | Zaixuan | Tianqi | chunk_id、source/version、获准原文、PDF/印刷页/章节、提取质量、用途；授权后返回 |
| RetrievalResult | Tianqi | 回答流程 | query_id、kb/retrieval 版本、允许引用段落、分数解释、未命中/限制原因 |
| AnswerRecord | Tianqi | UI、报告 | answer_id、experiment_id、实际 model_id、prompt 版本、evidence_ids、答案状态限制、运行时间和必要用量 |
| LearningAttempt | Tianqi | UI、报告 | 服务端用户、task/题目版本、真实回答、反馈、完成状态/时间 |
| ReportRecord | Tianqi | UI/导出 | report_id、服务端 owner、实验/答案引用、个人反思、版本/导出状态 |
| FeedbackRecord | 三位测试成员 | 对应开发者 | 匿名 case_id、系统版本、步骤、实际结果、公开许可、问题/复测关联 |

未知字段返回 unknown 与原因，禁止自行补造。owner_id 不从客户端声明直接信任。不在多个模块重复维护 users/reports 数据模型。变更接口先用 templates/INTERFACE_REQUEST.md 提需求。
