import { Then, When } from '@cucumber/cucumber'
import { expect } from 'playwright/test'
import type { AppWorld } from '../support/world'

When('打开当前用户菜单', async function (this: AppWorld) {
  await this.page.getByRole('button', { name: new RegExp(this.browserEmail) }).click()
  await expect(this.page.getByRole('menu', { name: '当前用户操作' })).toBeVisible()
})

When('通过用户菜单进入修改密码', async function (this: AppWorld) {
  await this.page.getByRole('menuitem', { name: '修改密码' }).click()
  await expect(this.page).toHaveURL(/\/account$/)
})

When('通过用户菜单登出', async function (this: AppWorld) {
  await this.page.getByRole('menuitem', { name: '退出' }).click()
  await expect(this.page).toHaveURL(/\/login$/)
})

Then('页面显示修改密码表单', async function (this: AppWorld) {
  await expect(this.page.getByRole('textbox', { name: '旧密码' })).toBeVisible()
  await expect(this.page.getByRole('textbox', { name: '确认新密码' })).toBeVisible()
})

Then('页面显示登录表单', async function (this: AppWorld) {
  await expect(this.page.getByRole('textbox', { name: '邮箱' })).toBeVisible()
  await expect(this.page.getByRole('textbox', { name: '密码' })).toBeVisible()
})

When('收窄桌面侧栏', async function (this: AppWorld) {
  await this.page.getByRole('button', { name: '收窄侧栏' }).click()
})

Then('侧栏收窄偏好已保存且导航仍可访问', async function (this: AppWorld) {
  await expect(this.page.getByRole('button', { name: '展开侧栏' })).toHaveAttribute(
    'aria-expanded',
    'false',
  )
  await expect(this.page.getByRole('link', { name: '流程' })).toBeVisible()
  const preference = await this.page.evaluate(() => localStorage.getItem('workspace2.navigation.collapsed'))
  expect(preference).toBe('true')
})

When('将浏览器视口设为手机尺寸', async function (this: AppWorld) {
  await this.page.setViewportSize({ width: 390, height: 844 })
})

When('打开手机导航抽屉', async function (this: AppWorld) {
  await this.page.getByRole('button', { name: '打开导航' }).click()
  await expect(this.page.getByRole('dialog', { name: '主导航' })).toBeVisible()
})

When('在抽屉中进入模型页', async function (this: AppWorld) {
  await this.page.getByRole('dialog', { name: '主导航' }).getByRole('link', { name: '模型' }).click()
  await expect(this.page).toHaveURL(/\/models$/)
})

Then('导航抽屉已关闭', async function (this: AppWorld) {
  await expect(this.page.getByRole('dialog', { name: '主导航' })).toHaveCount(0)
})
