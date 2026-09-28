import { Given, When } from '@cucumber/cucumber'
import type { Role } from '../generated/api'
import { ensureUser } from '../support/api'
import type { AppWorld } from '../support/world'

Given('存在用户 {string} 角色为 {string}', async function (this: AppWorld, email: string, role: string) {
  const id = await ensureUser(email, role as Role)
  if (!this.userIds.includes(id)) this.userIds.push(id)
  // 用户最后删（子资源先注册清理，LIFO 保证顺序）。
  this.registerCleanup(async () => {
    const { deleteUser } = await import('../support/api')
    await deleteUser(id)
  })
  this.browserEmail = email
})

When('在浏览器中登录该用户', async function (this: AppWorld) {
  const { loginViaUI } = await import('../support/nav')
  await loginViaUI(this)
})
