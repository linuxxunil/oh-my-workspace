# language: zh-CN
@smoke
功能: 供应商删除（正常删 + 被引用拒绝）
  # 被测动作走浏览器，准备/清理走 API（见 e2e/AGENTS.md）。

  @authenticated
  场景: 删除无引用供应商后列表消失
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建供应商 类型 "openai_compatible" 名称以 "E2E" 为前缀 地址 "https://api.example.com/v1"
    当 删除该供应商
    那么 供应商从列表中消失
    那么 清理以 "E2E" 为前缀的供应商与用户

  @authenticated
  场景: 删除被流程引用的供应商被拒绝
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建供应商 类型 "openai_compatible" 名称以 "E2E" 为前缀 地址 "https://api.example.com/v1"
    当 准备一个引用该供应商的流程
    当 删除该供应商
    那么 显示被引用拒绝且供应商仍在
    那么 清理以 "E2E" 为前缀的流程与用户
    那么 清理以 "E2E" 为前缀的供应商与用户
