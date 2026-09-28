# language: zh-CN
@a11y
功能: 无障碍冒烟（登录页与画布页零 critical/serious）
  # axe 注入式扫描；违规先修产品 markup。运行：pnpm -C e2e e2e -- --tags @a11y。

  @authenticated
  场景: 登录页无障碍扫描通过
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中打开登录页
    那么 当前页无障碍扫描零 critical 与 serious
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 画布页无障碍扫描通过
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 新建流程 名称以 "E2E" 为前缀
    当 打开当前流程的画布页
    那么 当前页无障碍扫描零 critical 与 serious
    那么 清理以 "E2E" 为前缀的流程与用户
