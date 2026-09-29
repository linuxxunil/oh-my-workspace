# language: zh-CN
@smoke
功能: 核心 smoke（登录→模型→流程运行）
  # API 仅承担准备/清理，被测动作走浏览器（见 e2e/AGENTS.md）。
  # 运行：pnpm -C e2e e2e -- --tags @smoke（需 infra + api + web 直跑，见 docs/release.md）。

  @authenticated
  场景: 超管配置 opencode_go 供应商并连通性检查通过
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建供应商 类型 "opencode_go" 名称以 "E2E" 为前缀 地址 "https://api.example.com/v1"
    那么 供应商出现在列表中
    当 对该供应商执行连通性检查
    那么 显示检查结果
    那么 清理以 "E2E" 为前缀的供应商与用户

  @authenticated
  场景: 编排最小流程并运行成功
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建流程 名称以 "E2E" 为前缀
    当 在画布中连线 start → code → end 并保存为新版本
    当 发布该流程并以输入 '{"n": 21}' 运行
    那么 运行状态为 succeeded 且输出 m 为 42
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 更换供应商 API Key 后连通性检查仍可用
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建供应商 类型 "openai_compatible" 名称以 "E2E" 为前缀 地址 "https://api.example.com/v1"
    当 打开该供应商的编辑并更换 API Key 为 "rotated-key"
    当 对该供应商执行连通性检查
    那么 显示检查结果
    那么 清理以 "E2E" 为前缀的供应商与用户
