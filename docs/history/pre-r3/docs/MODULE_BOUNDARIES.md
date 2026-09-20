# 模块边界

## 已建立的真实文档与内容目录

| 路径 | 负责人 | 边界 |
|---|---|---|
| team/<role>/PLAN.md | 各人 | 仅本人计划；不自行批准 |
| content/cases/ | Xingze | 中美案例、可比较范围、来源 |
| content/learning/ | Xingze | 学习内容；不实现学习状态服务 |
| content/reviews/ | Xingze | 资料与内容审核记录；不修改服务端批准状态 |
| materials/factors/ | Yifan | 因子与策略资料卡 |
| materials/risk/ | Guanjie | 风险、回撤、回测评价资料卡 |
| materials/markets/ | Yuntao | 中美市场差异及金融学习资料卡 |
| testing/feedback/<role>/ | 三位资料成员各自目录 | 获准匿名真人测试与问题记录 |
| testing/material-evaluation/<role>/ | 三位资料成员各自目录 | 资料与问答评估；与真人测试分开 |
| contracts/ | Yu 协调 | 共同输入输出契约，owner 合并 |
| .github/, scripts/, tests/governance/, 公共根文件 | Yu | 协作控制与集成 |

路径归属只是最大边界；实施 PR 还必须符合已批准 PLAN 的更小范围。

## 应用代码边界：等待认可源码后映射

尚未收到认可源码，所以不虚构真实应用目录、框架或数据库。Zaixuan 与 Tianqi 的代码 `module_paths` 暂为空，实施默认被阻止；收到源码后 Yu 根据实际目录作一次明确映射。

- Yu：数据量化、清洗、单/多指标策略、历史模拟、风险与费用、集成及协调 bug 修复。
- Zaixuan：保留认可 UI；账户、唯一数据库体系、资料解析/存储和 KB 管理；协调数据库迁移版本。
- Tianqi：调用 Zaixuan 的资料接口，负责检索/必要重排、DeepSeek 回答、学习任务、进度与报告。
- Xingze：案例、学习内容与内容审核；不另建量化引擎或 KB 服务。

资料解析/存储只有一套；检索与回答只有一套；金融数值只取 Yu 的确定性结果。公共启动、跨模块 schema、依赖文件及共享测试由 Yu 协调合并。不得分别创建 users 或 reports 表。
