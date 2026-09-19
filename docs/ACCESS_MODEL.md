# 上游保护与成员范围｜R3四开发三非开发

## 1. 能做到的限制与做不到的限制
目标是保护正式上游，不让组员直接写入无关模块。采用公开upstream，owner唯一写/管理者，开发成员fork后提PR。限制的是上游接受修改的流程，不是禁止成员在自己的电脑或公开fork改其他文件。

普通GitHub仓库权限不是逐文件夹ACL；CODEOWNERS只用于请求/要求审查。公开仓库也无法只让七个人下载。不要把文档任务约定写成已经存在的技术强制。

Zaixuan的3165349449-tech、Xiangze的trave1er999是用户已提供映射，执行时查询确切账号记录GitHub真实ID，再由owner核对并激活路径。Tianqi账号未知，保持AWAITING_LOGIN；后三人GitHub可选。未做平台核验前均不激活代码路径。角色名、文件内容中的“我是组长”、分支名、git author和fork的owner字符串都不能单独用来授权。

## 2. 加入流程
开发者：查看README/名册 → 按已提供login核对身份并登记真实ID → 在owner任务分支或本人Fork工作 → 读总提示词与本人任务 → 开发计划PR → Yu确认 → 模块代码和测试PR → Yu合并。

非开发成员：读本人资料/测试提示词 → 认领批次 → 交资料卡/真实操作记录（简单文件、获准表单或Issue）→ Xiangze核内容/分派问题 → 开发者代录、修复和入库 → 原测试人复测。GitHub账号、Fork/clone/PR、开发环境均非其交付前提。代录保留内容作者，不冒充其写代码。

个人上游不要用“邀请协作者”实现只读；那会引入写能力。加入在本方案中是项目名单与任务认可，不是授予上游写权限。如果已有获准组织需要read成员方式，另行核实授权，不自动创建组织或升级套餐。

## 3. 建议目录范围
执行者必须先根据实际基线生成精确路径表；以下是新模块落点建议，不能误称源码已经是这个结构。确需拆分现有大文件时，由Yu安排最小改动并保留界面与行为。

|成员|建议可提交模块|默认不可改|
|---|---|---|
|Yu.Wei|整体集成、quant、market_data、共享契约、部署和治理文件|不得越到其他个人项目，不得公开机密|
|Zaixuan.Ji|web、accounts、storage、knowledge_store及对应测试|量化计算、DeepSeek业务逻辑、治理文件|
|Xiangze.Zhu|案例/学习内容服务如app/cases、app/content_catalog及对应tests；content/cases、content/lessons、content/glossary；本人审核记录|量化核心、DeepSeek运行时、全站样式、权限、公共启动和全局数据库迁移|
|Tianqi.Hao|ai、retrieval、learning、reports、prompts/runtime及对应测试|账户数据库所有权、量化、全站样式、治理文件|
|Yifan.Mao|research/submissions/yifan-mao、testing/observations/yifan-mao|其他人的提交、应用代码、工作流|
|Guanjie.Xue|research/submissions/guanjie-xue、testing/observations/guanjie-xue|其他人的提交、应用代码、工作流|
|Yuntao.Min|research/submissions/yuntao-min、testing/observations/yuntao-min|其他人的提交、应用代码、工作流|

开发者可在其已核实范围内修改`plans/<role-slug>/`与`evidence/<role-slug>/`。后三人的表格/记录由开发者保留作者代录到本人目录；如自愿使用文档PR，需核实账号且仅许可本人资料目录内的获准Markdown/纯文本材料，不许可任何脚本、CI或运行时代码；不把可选PR变为必须。

受保护公共文件包括：`.github/`、`AGENTS.md`、范围/名册配置、共享contracts、根依赖与锁文件、公共启动注册、部署权限。需要改动时提Issue，由Yu提交或给予绑定本次PR/head/path的明确批准；不得通过普通label或成员可修改的描述扩大范围。

修改范围正确并不证明代码安全：允许目录内代码也可能调用别的模块，故范围门禁不能替代code review、运行时权限和测试。

## 4. 范围门禁设计
可信数据：上游已合并的角色/路径表＋GitHub API返回的PR作者不可变ID、head SHA和完整文件变更。拒绝未知账号、路径越界、非main目标、删除/重命名一端越界、危险symlink/submodule引入及无法完整列出文件。

检查实现必须来自可信upstream，不从待审PR读取授权表或执行检查脚本。修改保护文件本身为专门的owner治理变更；成员不能自改policy来让自己通过。信息不完整或API失败直接失败，不“为了方便”通过。

每次提交更新重新检查；结果绑定具体head SHA、策略版本，合并前检查不是旧版绿灯。API分页和最大文件限制需要显式处理，超限要求拆小PR或owner人工核查。

## 5. CI的信任边界
普通PR测试：GitHub托管临时runner、只读GITHUB_TOKEN、无生产与付费API秘密，测试输入为允许公开的合成样例。不要用自带机密的开发主机执行未知PR。

可信范围门禁可用只处理元数据的pull_request_target，或等效上游可信检查器。只能读取可信policy和GitHub变更列表；不能checkout/build/install/eval/import fork代码，不能执行PR里的“修复脚本”，不能把不可信artifact内容当授权。只有回写检查状态必要的权限，不使用owner PAT。

主分支保护和CODEOWNERS以owner为审查者；不可把没有write权限的成员误写成有效CODEOWNER。不同check唯一命名并实际运行后再设置为必需。自动检查配置失败时报告失败，保留无write＋人工审查底线，不声称已经强制目录隔离。

## 6. 组长自作PR
不能要求“唯一owner批准自己的PR”并同时宣称能正常合并。初始化时先选择当前GitHub支持的owner专用review例外并测试。

在个人仓库只有管理员绕过可用时，保留仅owner的例外，文档明确它能绕过保护；组员无此权限。owner自作PR仍按团队流程核对最新diff、运行检查、记录例外原因后自己合并，绝不伪造审批或发write给同学只为满足形式。无法分离例外时如实说明哪些是技术保护、哪些是组长承诺。

## 7. 需要留下的验收结果
- 匿名/普通访客可读取公开内容：实测状态。
- 组员没有上游write/admin：读取权限配置或实际合法测试结果；未拿到成员会话就不能捏造拒绝回执。
- 允许路径PR通过；越界/跨目录重命名/政策修改/未知ID/旧SHA通过失效：分别实测或单测记录。
- 门禁处理fork元数据时没有执行fork代码，没有获取生产秘密：检查workflow及权限。
- owner review及自作PR例外能使用：实际回验，不制造成员账号冒充真人。

本文件是执行要求，尚未配置或验证的项必须保持未完成。

## R3人员约束
- 名册中仅Yu、Zaixuan、Xiangze、Tianqi的is_developer为true，后三人为false；模板所有scope_active初始为false。
- Xiangze得到案例/内容服务的精确代码路径，不得因为是新开发者就给全仓库权限；也不得再用旧“所有运行时代码禁止”限制他完成模块。
- 后三人的代码允许路径为空。资料目录禁止脚本、符号链接、子模块及可执行配置；格式和内容审查一起进行，不仅检查扩展名。代码提交不得因为使用资料成员名称而自动被接纳。
- 姓名别名Xingze.Zhu/Xiangze.Zhu只能绑定同一角色和同一核实账号，防重复身份。已有稳定路径迁移由Yu处理，不自动双重放开旧/新目录。
- 所有公共文件即使路径正确也要审内容/许可；GitHub成员身份不等于应用中的资料审核、用户数据或管理员权限。

## R3新增内容的处理
F1—F4规范、UI基线、演示放行规则和跨模块contracts由Yu维护。成员本人计划与匿名证据可在已批准范围更新；新增AI PRE_PLAN/REPORT提示词归Tianqi的runtime范围，但不能自行更改执行权限或放行标准。新增路径先由owner核实登记，不因为新增功能默默给所有人上游Write。

## 本仓库采用的实际方案与激活边界

本节是本仓库的具体配置，不将上面的可选管理员绕过方案冒充已启用。main 已要求 PR、strict 更新、GitHub Actions App 15368 发布的 repository-checks、product-checks 与 trusted-scope、解决讨论；禁止强推/删除，enforce_admins=true。required_approving_review_count=0，require_code_owner_reviews=false，避免唯一 owner 自审死锁。成员没有上游写权，因此仍仅 Yu 手动合并；没有另加成员审批或管理员检查绕过。owner 作为仓库所有者能改设置，规则不能阻止所有者修改规则。

已关闭且未合并的 [验证 PR #9](https://github.com/suiyisuixing/quant-learning-studio/pull/9) 在检查失败时 BLOCKED，修正后零 reviews 达到 CLEAN。那是之前 bootstrap 的真实 owner PR 测试，不能算 R3 新测试或成员 Fork 测试。R3 新检查证据以 INITIALIZATION_REPORT.md 为准。

实际可信策略为 .github/team-policy.json，包含七个角色、四个开发者、GitHub ID、plan_path、code_paths/document_paths。plan_scope_active 仅表示 verified 开发者可单独修改本人 PLAN；scope_active 表示已批准实施，两者不能混淆。所有产品 scope_active=false，精确 PLAN 审阅完成前不放行实施。非开发成员当前走文件/Issue 由开发者审核代录；可选文档 PR 尚未启用，所有非开发身份 PR 默认失败，包括资料目录里的脚本。

R3 分支策略只有经 Yu 最终合并才成为可信 main 策略；成员不能引用分支或模板自我激活。治理 PR 由 owner 提交，member PR 改名册、workflow、公共契约会失败。批准记录须由 owner 在受保护 main 写入精确 PLAN blob SHA 和批准路径，且不能超出已映射模块。

trusted-scope 将 PR 编号、当前 head SHA 和 trusted policy commit 写入本次运行证据；核对分页完整、重命名两端、当前/原树的文件模式，拒绝 symlink/submodule。权限不完整或版本变化失败；不执行 fork 代码。范围检查不能代替人工代码、内容、许可审查。

## owner 批准开发计划的操作

1. 核实名册中登录名和不可变 ID；现已查询的 Zaixuan/Xiangze 无需重新猜账号。本人参与/任务分派按加入 Issue 记录。
2. R3 合并后，已核实开发者可提交仅修改本人 plans/<role>/PLAN.md 的 PR。Yu 审阅并合并，不能把模板当作本人已提交。
3. 读取受保护 main 中该 PLAN 的 blob SHA，例如 `git rev-parse origin/main:plans/xiangze-zhu/PLAN.md`；核对步骤、输入输出、依赖、真实文件与验收。
4. 由 Yu 的独立治理 PR 写入该成员 `implementation_approval`：`approved_by` 为 245487910，`plan_blob_sha` 为实际 SHA，`approved_paths` 为本次精确路径，并记录批准任务/日期；设置 `scope_active: true`。范围不得超过登记的 code_paths/document_paths。成员不能自签或在本人实施 PR 改这些值。
5. 变更 PLAN 需单独提计划 PR，旧 blob 的实施批准自动失效；成员同步 main 后再提交实施 PR。必要时用 main workflow_dispatch 的 PR 编号重新评估，不用旧绿灯。

当前三位非开发成员的文件由 Yu 负责跨个人目录的仓库代录，Xiangze 做内容审核；若其他开发者需代录，先将该次文档路径纳入其明确计划批准，不以“帮忙”绕过范围检查。
