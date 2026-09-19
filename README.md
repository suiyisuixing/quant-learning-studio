# Quant Learning Studio / QuantLab

面向学生的独立金融学习网站：使用虚拟资金、获准数据或明确标记的教学样本，学习中美量化方法、风险、费用和资料证据。

**状态：协作初始化；认可的网站源码及完整启动提示词尚待提供。没有部署公网网站，尚无可运行产品。**

- 主仓库 owner / 最终合并人：Yu.Wei，GitHub `@suiyisuixing`。
- 其他六位成员使用自己的 Fork 提交 PR；不授予主仓库 Write、Maintain 或 Admin。
- 身份核实 → 登记角色 → 本人填写 PLAN → Yu 确认具体范围 → 实施 → 检查 → Yu 审阅并合并。
- 原前端设计和框架必须保留；不得使用旧 ai-workbench 或过时 starter。

## 开始协作

1. 阅读 [完整软件要求](docs/requirements/01_PRODUCT_MASTER.md) 和 [原始职责](docs/requirements/ORIGINAL_TASKS.md)。
2. 按 [加入方式](docs/ONBOARDING.md) 在成员加入 Issue 留下当前 GitHub 账号与角色，等待 Yu 线下核实本人身份。
3. 阅读 [个人提示词入口](prompts/README.md)，Fork 后只修改自己的 `team/<role>/PLAN.md`，提交计划 PR。
4. Yu 将核实后的数字 GitHub ID、具体路径范围和已批准 PLAN 的 Git blob SHA 登记在主分支规则中，之后才能提交实施 PR。

## 计划与规则

- [项目完整计划](docs/PROJECT_PLAN.md)
- [七人任务 Issue](docs/TASKS.md) 与 [成员加入 Issue](https://github.com/suiyisuixing/quant-learning-studio/issues/1)
- [模块边界](docs/MODULE_BOUNDARIES.md)
- [协作权限与 main 保护](docs/PERMISSIONS.md)
- [共同接口草案](contracts/README.md)
- [填写模板](templates/README.md)
- [验收状态](docs/ACCEPTANCE.md)
- [输入来源与缺口](docs/requirements/PROVENANCE.md)

## 当前可运行检查

仅协作基础使用 Python 标准库，不替应用选择框架：

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/check_repository.py
python3 scripts/publication_scan.py --history HEAD
```

应用安装、启动和测试命令：等待认可源码后按真实项目填写，不推测。

## 数据与费用

不连接券商、不处理真实资金、不承诺收益。DeepSeek 仅计划从后端接入；初始化无真实 API 调用。未获授权不使用付费服务。受限全文、提取片段、向量索引、数据库、密钥、真实用户身份和私人日志不得提交。

公开仓库不自动授予第三方资料再分发权。当前未擅自添加开源许可证；各贡献者和第三方素材的许可需由 owner 明确确认。
