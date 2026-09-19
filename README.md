# QuantLab · quant-learning-studio

面向金融入门者与策略练习者，沿用中美量化比较方向，使用用户认可的独立网站设计。

**F1 市场数据的显示 → F2 演练前 AI 策划和分析 → 用户确认 → F3 模拟经营沙盘 → F4 演练后问题分析与复盘。**

已按白名单导入哈希一致的认可独立网站源码，应用与 UI 文件逐字节保留。现有 0.2.0 基线提供账户、合成样本回测、规则讲解、学习与报告；**它尚未实现并通过 R3 的 F1–F4 完整链路**。R3 更新通过独立 PR 交 Yu 最终合并；分支中的配置不能冒充 main 已激活。

## 开始协作
- [启动入口](prompts/START_HERE.md) · [完整 Bootstrap](prompts/00_CHATGPTWORK_BOOTSTRAP.md) · [产品总要求](prompts/01_PRODUCT_MASTER.md)
- [七人名册](docs/TEAM_ROSTER.md) · [七个角色与首批任务](docs/TASKS.md) · [完整阶段计划](docs/PROJECT_PLAN.md)
- [加入 Issue #1](https://github.com/suiyisuixing/quant-learning-studio/issues/1) · [实际访问模型](docs/ACCESS_MODEL.md) · [模块边界](docs/MODULE_BOUNDARIES.md)
- [七份个人提示词](prompts/members/) · [四份网站 AI 提示词](prompts/runtime/) · [填写模板](templates/)
- [四项验收](docs/FOUR_FEATURES.md) · [统一接口](docs/INTERFACES.md) · [UI 基线](docs/UI_BASELINE.md) · [完整演示](docs/DEMO_SCRIPT.md)
- [本次初始化状态](docs/INITIALIZATION_REPORT.md) · [输入来源](docs/requirements/PROVENANCE.md) · [许可状态](LICENSE_STATUS.md)

开发者仅 Yu、Zaixuan、Xiangze、Tianqi：先本人 PLAN，范围确认后从 Fork/任务分支提 PR，Yu 最终合并。三位资料成员 Yifan、Guanjie、Yuntao 不写代码，不要求 Fork；按批次交资料、真人测试和复测记录，由开发者保留原作者代录。

## 当前可运行的检查
治理检查需要 Python 3.11+，使用标准库：
```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/check_repository.py
python3 scripts/publication_scan.py --history HEAD
```
这些检查只验证协作规则、输入清单和公开扫描，不能证明网站、真实 DeepSeek 或真人测试已通过。网站的实际启动方法见下方；初始化没有为成员实现 R3 新功能。

公开仓库不等于公开部署。没有购买服务、调用付费 API、启用 Pages 或发送协作者邀请。CODEOWNERS 用于审查，不是文件夹权限。历史来源保留在 docs/history，活跃安排以 R3 为准。

## 本地运行网站

技术栈保持原生 ES 模块/CSS、FastAPI、SQLite；不需要 npm、CDN 或前端构建。Python 3.11+：
```sh
python3 run.py
```
原启动器首次会在本项目创建 .venv 并安装 requirements.txt，不修改全局 Python。打开 http://127.0.0.1:8017，自行注册本地账户；数据保存在 var/qlab.db，不提交 Git。已有项目依赖环境可用：
```sh
.venv/bin/python run.py --use-current-env
```
Windows 使用 py -3 run.py 或 start.bat；本次是否实测以初始化报告为准。未提供默认管理员密码或真实 API 密钥。默认只用明确标注的合成样本、规则讲解，不冒充真实市场或 DeepSeek。

现有基线流程：注册 → 风险实验 → 三方法回测 → 规则讲解 → 反思/报告 → 概念题 → 重开记录。这不是 R3 的完整演示流程；演练前方案批准、分阶段用户操作、论文检索与操作级复盘仍是团队任务。

开发检查（使用项目隔离环境，测试数据不计真人）：
```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/http_smoke.py
```
运行测试前清除真实 QLAB API 凭据，并设置 QLAB_DB 到临时隔离位置。不要对任何真实数据库测试。发布使用 [精确导入清单](docs/SOURCE_IMPORT.json)；旧包内测试证据未上传或算成本次结果。
