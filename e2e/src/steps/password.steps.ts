import { When } from '@cucumber/cucumber'
import { expect } from 'playwright/test'
import type { AppWorld } from '../support/world'

When('在浏览器中以 {string} 用密码 {string} 登录', async function (
  this: AppWorld,
  email: string,
  password: string,
) {
  const { loginAs } = await import('../support/nav')
  await loginAs(this, email, password)
})

When('退出登录', async function (this: AppWorld) {
  const { logoutViaUI } = await import('../support/nav')
  await logoutViaUI(this)
})

When('将用户 {string} 的密码重置为 {string}', async function (
  this: AppWorld,
  email: string,
  password: string,
) {
  const { page } = this
  const { gotoSection } = await import('../support/nav')
  await gotoSection(this, '/users')
  const row = page.locator('li', { hasText: email })
  await row.getByRole('button', { name: '重置密码' }).click()
  await row.getByRole('textbox', { name: '新密码' }).fill(password)
  await row.getByRole('button', { name: '保存' }).click()
  // 表单收起（重置按钮重新可见）即保存成功。
  await expect(row.getByRole('button', { name: '重置密码' })).toBeVisible()
})

When('在账号页将密码从 {string} 改为 {string}', async function (
  this: AppWorld,
  oldPassword: string,
  newPassword: string,
) {
  const { page } = this
  const { gotoSection } = await import('../support/nav')
  await gotoSection(this, '/account')
  await page.getByRole('textbox', { name: '旧密码', exact: true }).fill(oldPassword)
  await page.getByRole('textbox', { name: '新密码', exact: true }).fill(newPassword)
  await page.getByRole('textbox', { name: '确认新密码', exact: true }).fill(newPassword)
  await page.getByRole('button', { name: '修改密码' }).click()
  await expect(page.getByRole('status')).toContainText('密码已更新')
})
