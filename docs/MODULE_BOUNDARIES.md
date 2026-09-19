# 模块边界｜R3四开发、三资料测试

以下是工作分工和建议模块路径，不是已经存在的代码结构或已生效的GitHub规则。执行者先检查实际源码，由Yu冻结最小接口和精确路径表；不要为了目录漂亮重新写一遍产品。

|开发者|模块|负责代码|不接管的部分|
|---|---|---|---|
|Yu.Wei|市场数据、量化、沙盘和集成|数据清洗、金额/风险/费用、快照与计划校验、操作账本、全站公共注册、CI/发布|不包办全部前端和DeepSeek模块|
|Zaixuan.Ji|UI、账户数据库、论文库基础|保留既有设计；账户隔离、存储迁移、上传解析分段/索引、引用显示、前端接口联调|不修改量化公式、不另写AI生成引擎|
|Xiangze.Zhu|案例与教学内容模块|中美案例结构与查询/筛选/比较、来源校验、术语和学习内容读取接口、对应测试；提出匹配原UI的数据展示需求|不重做全站视觉、不接账户/数据库总所有权、不写DeepSeek运行时或量化核心|
|Tianqi.Hao|检索、AI、学习进度、报告|提问检索、DeepSeek、F2草案/F4复盘、提示词、学习任务提交和进度、报告|不另造数据库、不重新计算金额、不大改样式|

## Xiangze的最小首个开发任务
建立一条能返回案例及来源/限制的查询接口（或现有框架中的等价服务），用明确标记的获准开发样例验证：按市场筛选、查询详情、未知字段不补值、不可比字段返回原因、未审核内容不用于正式解释。写输入非法和来源缺失的测试，与Zaixuan接入原比较页。样例可以是合成fixture，但只能计代码开发检查，不能冒充真实基金案例验收。

## 不重复建设
- 论文上传/文件/段落/索引：Zaixuan的统一存储，Tianqi负责检索选择；Xiangze不再建第二个向量库。
- 教学内容：Xiangze负责内容数据、查询和校验；学生作答、进度、AI反馈和报告：Tianqi负责。
- 金融计算：Yu负责；其他模块通过接口取结果，不独立算手续费或收益。
- 数据库迁移：Zaixuan统一编号，Yu整合集成；Xiangze/Tianqi提出schema修改，不各建users或reports表。
- 前端样式/公共导航：Zaixuan；Xiangze仅在明确获准组件路径中配合，不能把一个模块许可扩展成整个web目录可改。

## 路径登记原则
建议检查实际项目中是否能映射到`app/cases/`、`app/content_catalog/`、`tests/cases/`、`content/cases/`、`content/lessons/`。若目前集中在app/main.py和web/app.js，先由Yu/Zaixuan提供小范围适配或拆出模块，不给所有人这两个大文件的常驻全量许可。路径名称只是建议，以核对后的实际表为准。

共享契约、依赖锁、权限/名册、CI、公共入口和部署设置由Yu控制；必要修改用独立接口需求或明确的一次性授权，不在功能PR顺手扩大。

## 后三人不开发
Yifan、Guanjie、Yuntao只提交论文资料卡、原文核查、真实用户操作和问题/复测记录。不得要求编写代码、测试脚本、数据爬虫、CI配置或自行运维。他们发现问题，由对应开发者修复，再由他们按界面步骤复测。

## 四项交接
F1：Yu行情与snapshot＋Xiangze案例/来源＋Zaixuan界面。
F2：Tianqi检索策划＋Xiangze教学依据＋Yu参数校验＋Zaixuan编辑确认。
F3：Yu沙盘计算＋Zaixuan交互＋Xiangze概念/案例查询＋Tianqi接学习状态。
F4：Tianqi复盘＋Yu操作/指标＋Xiangze解释依据＋Zaixuan保存展示。

最终都引用同一snapshot/plan/run/result/version，不用四套独立演示假装集成。

## 本次核实的实际源码与精确落点

原生 JavaScript/CSS + FastAPI + SQLite；没有框架变更。现有 app/main.py 集中了路由、账户、SQLite、AI 和数据接入，是共享入口，仅 Yu 协调整合；tests/test_product.py 是共享回归测试，同样由 Yu 控制。现有代码未因初始化被拆写。

|成员|已有文件|批准本人 PLAN 后可创建的明确模块/测试|公共依赖|
|---|---|---|---|
|Yu|app/engine.py、app/main.py、tests/test_product.py、run.py、contracts 与治理文件|市场快照、计划确认、操作账本按共同接口定稿|统一金额/风险/费用与共享注册|
|Zaixuan|web/app.js、web/style.css、web/index.html、web/favicon.svg|app/accounts.py、app/storage.py、app/knowledge_store.py；对应 tests/test_accounts.py、test_storage.py、test_knowledge_store.py|主入口/迁移编号由 Yu 协调；不把 web 范围扩展到整个仓库|
|Xiangze|app/content.py|app/cases.py、tests/test_cases.py、tests/test_content.py|当前 Case 模型和 cases 路由在 app/main.py，先由 Yu 协调适配/搬移；必须交案例查询/比较代码及测试|
|Tianqi|prompts/runtime/ 四份提示词|app/ai.py、app/retrieval.py、app/learning.py、app/reports.py；对应四份 tests/test_*.py|当前 tutor/lesson/report 路由在 app/main.py，先冻结调用接口与统一存储|

新模块名称是本轮明确的分工落点，不表示它们已经存在或已经实现。本人 PLAN 批准前，scope_active 全为 false；GitHub 不按源码行号授予权限，所以不把 app/main.py 常驻授予三个成员。所有公共注册、依赖锁、共享合同和全局迁移由 Yu 整合。

Xiangze 同时负责 content/cases/、content/lessons/、content/glossary/、content/reviews/；Tianqi 负责 prompts/runtime/。成员证据在 evidence/<role>/。三位非开发成员按批次提交到 research/submissions/<role>/、testing/observations/<role>/，开发者审核后代录，不要求他们写脚本、自动化测试或 PR。
