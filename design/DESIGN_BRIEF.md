# 先设计，再实现 · 页面和交互规范

建立时间：2026-09-17。本文先于应用代码编写。

## Skill来源与实际使用
本环境未安装用户本机的 Design / Product Design / Impeccable 插件。读取并采用公开 Impeccable Skill 的 new-work、craft-floor 指南；通过网页读取的 SKILL.md 显示版本4.0.4（搜索索引版本可能不同）。容器下载失败，未运行 context/seed/插件命令，不伪造独立设计师/插件审查回执。
来源： https://raw.githubusercontent.com/pbakaus/impeccable/main/plugin/skills/impeccable/SKILL.md
新建指引： https://raw.githubusercontent.com/pbakaus/impeccable/main/plugin/skills/impeccable/reference/new-work.md
质量指引： https://raw.githubusercontent.com/pbakaus/impeccable/main/plugin/skills/impeccable/reference/craft-floor.md
用户已授权直接实施，产品与目标明确；不再让用户重复选择风格。

## 设计方向：明亮的学习工作台
用户在教室、图书馆使用笔记本，界面以浅色和清楚层次为主。左侧深青导航建立空间感；内容区以白色、浅灰绿承托信息，青色主操作，暖金色提示不确定性。拒绝满屏K线、炫光、涨跌排行榜、虚构收益数字、过多卡片嵌套。
字体用操作系统中文/拉丁字体，不附带字体文件，不依赖Google字体或CDN。数字使用tabular-nums，常用术语旁提供简单解释。图表必须有表格或数字解释，不能只靠颜色。

## 页面规划
1. /welcome 产品介绍：真实能力、学习入口、数据/AI状态、隐私说明，无假用户数。
2. /auth 登录注册：真正的服务端认证，错误提示、密码显示、退出、CSRF保护。
3. /home 学习首页：继续上一实验、循序任务、知识点、真实完成进度；初始为0。
4. /compare 中美比较：可核验基金资料导入、选择两条案例并对照，空库明确说明；下半部比较两国教学实验，不冒充基金实绩。
5. /lab 实验设置：数据来源在前；市场、日期、基准/单指标/多指标、资金/现金/调仓；高级参数折叠；运行状态可见。
6. /results 实验结果：三方案同轴归一化资金曲线、最大回撤、费用、因子效果、样本外切分、交易记录；深入信息渐进展开。
7. /tutor 学习助手：绑定所选实验，数字先由程序计算；在线AI与本地规则讲解分开标记；报告保存和学习反思。
8. /learn 学习计划：短讲解、题目反馈、服务端真实进度，不奖励投机收益。
9. /reports 我的报告：搜索、读取、HTML/Markdown/JSON下载、删除确认。
10. /data 数据与资料：CSV导入、用途声明、真实/合成标识、来源、基金案例录入；AI未配置状态可见。
11. /feedback 试用反馈：同意后提交真实反馈；不自动把账户/机器人算作10名测试者。

## 通用组件
Sidebar / Topbar / DataBadge / StepPath / MetricDefinition / FormField / SourceList / StatusBanner / Chart / EmptyState / Toast / Confirm。
每个页面覆盖：有数据、空数据、加载、错误、无权限/登录过期；按钮有禁用/忙碌/成功反馈。标题和操作唯一突出，表格仅在自身区域横向滚动。
响应式：宽屏左侧固定导航；<=900px可收起；<=600px单列、44px触控、无页面横向溢出。键盘可访问，焦点清楚，尊重prefers-reduced-motion。

## 核心流程与异常
注册→首页→进入实验→选择明确合成或授权数据→真实计算→结果→规则讲解或实际AI→反思→保存报告→刷新/退出再登录可重开。
数据不够不生成结果；API失败不替换成假行情；模型未配不显示假AI；重复请求幂等；别人的实验/报告不可读取；导出不执行用户输入HTML。

## 验收
先完成整体页面，再一次批量桌面/手机截图检查；集中修复，最多一轮视觉复查。功能和安全测试单独执行，不能以视觉合格代替计算/权限合格。
