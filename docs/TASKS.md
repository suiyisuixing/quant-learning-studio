# 七人完整任务与执行入口 · R3

一次把全部职责给齐，按依赖连续执行；不按周派工，不在第一份计划、第一条接口或第一份 PR 后结束。每份提示词已有任务清单、输入输出、依赖、路径、验证与完整交付。读 [执行规则](../prompts/EXECUTE_TO_COMPLETION.md)，从自己的提示词开始。

四位开发者保留首次完整 PLAN/精确范围确认，再连续实施；后三人交资料/真人测试/复测文件即可。角色 Issue 保留原编号和讨论。R3 分支仍需 Yu 最终合并后成为可信 main。

|成员|本人完整任务|提示词 / 任务|
|---|---|---|
|Yu.Wei|数据/快照、参数批准、量化沙盘、公共接口、整合与验证（YW-01 至 YW-10）|[完整提示词](../prompts/members/Yu.Wei.md) · [#2](https://github.com/suiyisuixing/quant-learning-studio/issues/2)|
|Zaixuan.Ji|保留 UI、账户、统一存储、论文库基础、四步界面和联调（ZJ-01 至 ZJ-08）|[完整提示词](../prompts/members/Zaixuan.Ji.md) · [#3](https://github.com/suiyisuixing/quant-learning-studio/issues/3)|
|Xiangze.Zhu|案例/学习内容代码、查询比较、来源审核、四项内容接入（XZ-01 至 XZ-07）|[完整提示词](../prompts/members/Xiangze.Zhu.md) · [#4](https://github.com/suiyisuixing/quant-learning-studio/issues/4)|
|Tianqi.Hao|检索与 DeepSeek、F2/F4、学习进度、报告和对照验证（TH-01 至 TH-09）|[完整提示词](../prompts/members/Tianqi.Hao.md) · [#5](https://github.com/suiyisuixing/quant-learning-studio/issues/5)|
|Yifan.Mao|认领资料、原文核对、真人测试、问题与复测、完整文件交接（YM-01 至 YM-08）|[完整提示词](../prompts/members/Yifan.Mao.md) · [#6](https://github.com/suiyisuixing/quant-learning-studio/issues/6)|
|Guanjie.Xue|认领资料、原文核对、真人测试、问题与复测、完整文件交接（GX-01 至 GX-08）|[完整提示词](../prompts/members/Guanjie.Xue.md) · [#7](https://github.com/suiyisuixing/quant-learning-studio/issues/7)|
|Yuntao.Min|认领资料、原文核对、真人测试、问题与复测、完整文件交接（YT-01 至 YT-08）|[完整提示词](../prompts/members/Yuntao.Min.md) · [#8](https://github.com/suiyisuixing/quant-learning-studio/issues/8)|

Yu 的具体实施范围见 [全量任务计划](../plans/yu-wei/PLAN.md)，共享字段提案见 [INTERFACE_PROPOSAL.md](../plans/yu-wei/INTERFACE_PROPOSAL.md)。接口提案未冻结，其余成员的本人事实、PLAN 与完成状态不得代填为已经提交或通过。

## 交接顺序

1. Yu 与三个开发者核对同一 snapshot/plan/run/result/review/source 身份和共享合同；各自 PLAN 一次覆盖全部任务。
2. Zaixuan 提供统一存储/权限/资料位置；Xiangze 提供案例与教学服务；Yu 提供数据/批准/计算；Tianqi 在这些接口上完成两个 AI 阶段。
3. Zaixuan 接入原 UI，Yu 负责公共入口与串联；代码问题由原作者修复。并行做独立模块时只能以明确标注的 fixture 测协议，不能各建替代系统。
4. 三位资料测试成员都完成来源核查、实际操作和复测全流程，按 #18 认领条目去重；Yu 保留作者代录，Xiangze 审核、Zaixuan 入库、Tianqi 检索。
5. 所有成员交本人的完整状态和证据；Yu 核对最新提交和检查，控制最终合并。只有真实四项验收均通过才能宣布整个流程完成。

## 功能与集成任务

- [[R3-BOOT] 源码导入、R3 协作和公开验收](https://github.com/suiyisuixing/quant-learning-studio/issues/10)
- [[R3-UI] 固定认可 UI 并映射四步入口](https://github.com/suiyisuixing/quant-learning-studio/issues/11)
- [[R3-F1] 真实市场显示、来源与 snapshot](https://github.com/suiyisuixing/quant-learning-studio/issues/12)
- [[R3-F2] 论文检索和演练前 AI 策划](https://github.com/suiyisuixing/quant-learning-studio/issues/13)
- [[R3-PLAN] 冻结计划批准和 run 输入合同](https://github.com/suiyisuixing/quant-learning-studio/issues/14)
- [[R3-F3] 可操作虚拟资金沙盘和操作账本](https://github.com/suiyisuixing/quant-learning-studio/issues/15)
- [[R3-F4] 针对本次操作的问题分析与复盘](https://github.com/suiyisuixing/quant-learning-studio/issues/16)
- [[R3-CONTENT-DEV] 案例与教学内容查询比较服务](https://github.com/suiyisuixing/quant-learning-studio/issues/17)
- [[R3-MATERIAL] 论文与真人测试批次认领](https://github.com/suiyisuixing/quant-learning-studio/issues/18)
- [[R3-E2E] 同一练习的四项完整浏览器演示](https://github.com/suiyisuixing/quant-learning-studio/issues/19)

[加入与交接 Issue #1](https://github.com/suiyisuixing/quant-learning-studio/issues/1)。两个已知成员账号已核实 ID，但 GitHub 暂不允许 issue assignment（404）；保持不 assign，不因此邀请 write。Tianqi 账号待提供。没有已建立表单，资料成员可交模板文件。

状态标签已实际建立：status:todo、status:in-progress、status:review、status:done、status:blocked。未另建项目看板或收费服务。
