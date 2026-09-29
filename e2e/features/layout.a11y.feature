# language: zh-CN
@a11y
功能: Layout 浮层无障碍
  @authenticated
  场景: 用户菜单展开态扫描通过
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 打开当前用户菜单
    那么 当前页无障碍扫描零 critical 与 serious
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 手机导航抽屉展开态扫描通过
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 将浏览器视口设为手机尺寸
    当 打开手机导航抽屉
    那么 当前页无障碍扫描零 critical 与 serious
    那么 清理以 "E2E" 为前缀的流程与用户
