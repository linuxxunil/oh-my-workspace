# language: zh-CN
@smoke
功能: 全站 Layout 与导航交互
  # 被测动作走浏览器，用户准备与清理走 API。

  @authenticated
  场景: 用户菜单进入修改密码页面
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 打开当前用户菜单
    当 通过用户菜单进入修改密码
    那么 页面显示修改密码表单
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 用户菜单登出
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 打开当前用户菜单
    当 通过用户菜单登出
    那么 页面显示登录表单
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 桌面侧栏可收窄并记忆偏好
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 收窄桌面侧栏
    那么 侧栏收窄偏好已保存且导航仍可访问
    那么 清理以 "E2E" 为前缀的流程与用户

  @authenticated
  场景: 手机抽屉导航后自动关闭
    假如 存在用户 "E2E_root@example.com" 角色为 "super_admin"
    当 在浏览器中登录该用户
    当 将浏览器视口设为手机尺寸
    当 打开手机导航抽屉
    当 在抽屉中进入模型页
    那么 导航抽屉已关闭
    那么 清理以 "E2E" 为前缀的流程与用户
