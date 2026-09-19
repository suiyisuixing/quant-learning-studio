# 实际权限模型

## GitHub 与应用权限分离

主仓库 owner 为已核实的 `suiyisuixing`（数字 ID 245487910）。主仓库成员邀请为零；其他人通过 Fork 提交 PR。公开仓库的读取和 Fork 无法也不应伪装为按目录读取限制。学生应用中的账户隔离与资料审核由未来服务端独立实现。

## 可信路径检查

`.github/team-policy.json`、检查脚本与 workflow 均读取主仓库默认分支的受信任版本，不能取 PR 修改版。根据 PR 作者数字 ID 和登录名共同匹配登记；不知道的账号失败。检查所有变更路径，重命名同时检查旧路径和新路径；文件列表不完整、异常状态、API 失败均关闭放行。

已核实成员可以提交本人 PLAN-only PR。实施需要 owner 在主分支记录：确切 PLAN blob SHA、批准路径、确认人和依据。批准路径必须落在该角色模块路径以内。变更 PLAN 必须单独提交并重新批准。公共规则、接口和共享文件默认仅 owner 修改。

受信任 workflow 只读取 PR 文件元数据与 Git blob 身份，不执行 PR 程序。以 `statuses: write` 发布 `trusted-scope`，所需状态绑定 GitHub Actions App；普通 Fork 的只读 token 不能伪造这个状态。

## main

目标配置：要求 PR、`trusted-scope` 与 `bootstrap-checks` 通过、分支更新、禁止强推与删除、管理员同样受保护。原生 required approvals 设置为 0，避免唯一 owner 被迫批准自己的 PR。唯一有合并权限的人仍是 Yu；他通过手动审查和合并作最终决定。CODEOWNERS 指向 Yu，只负责审查路由，不是目录权限。

owner 能调整仓库管理规则，这是仓库所有权的固有限制；不得声称规则能约束 owner 不修改配置。正常合并路径必须满足所需检查。

## 状态

此文描述实现目标与机制；已生效配置、检查运行和限制以 `docs/ACCEPTANCE.md` 及 GitHub 当前状态为准。六名成员身份及所有产品实施计划初始均为 PENDING。没有制造已完成的真人跨账号测试。
