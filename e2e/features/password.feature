# language: zh-CN
@smoke
功能: 密码管理（管理员重置 + 本人自改）
  # 被测动作走浏览器，准备/清理走 API（见 e2e/AGENTS.md）。

  @authenticated
  场景: 管理员重置成员密码后新密码可登录
    假如 存在用户 "E2E_pwd_admin@example.com" 角色为 "admin"
    假如 存在用户 "E2E_pwd_member@example.com" 角色为 "member"
    当 在浏览器中以 "E2E_pwd_admin@example.com" 用密码 "E2e12345" 登录
    当 将用户 "E2E_pwd_member@example.com" 的密码重置为 "Reset12345"
    当 退出登录
    当 在浏览器中以 "E2E_pwd_member@example.com" 用密码 "Reset12345" 登录
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 成员自改密码后新密码可登录
    假如 存在用户 "E2E_self_member@example.com" 角色为 "member"
    当 在浏览器中以 "E2E_self_member@example.com" 用密码 "E2e12345" 登录
    当 在账号页将密码从 "E2e12345" 改为 "Self12345"
    当 退出登录
    当 在浏览器中以 "E2E_self_member@example.com" 用密码 "Self12345" 登录
    那么 清理以 "E2E" 为前缀的流程与用户
