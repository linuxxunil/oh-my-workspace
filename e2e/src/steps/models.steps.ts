import { Then, When } from '@cucumber/cucumber'
import { expect } from 'playwright/test'
import { e2eName } from '../support/naming'
import type { AppWorld } from '../support/world'

When(
  '新建供应商 类型 {string} 名称以 {string} 为前缀 地址 {string}',
  async function (this: AppWorld, type: string, prefix: string, url: string) {
    void prefix
    const name = e2eName('provider')
    const { page } = this
    const { gotoSection } = await import('../support/nav')
    await gotoSection(this, '/models')
    await page.getByRole('textbox', { name: '名称' }).fill(name)
    await page.getByRole('combobox', { name: '类型' }).selectOption(type)
    await page.getByRole('textbox', { name: '地址' }).fill(url)
    await page.getByRole('button', { name: '模型供应商' }).click()
    await expect(page.locator('li', { hasText: name })).toBeVisible()
    this.currentProviderName = name

    const { findProviderByName } = await import('../support/api')
    const id = await findProviderByName(name)
    if (id) {
      this.currentProviderId = id
      this.providerIds.push(id)
      this.registerCleanup(async () => {
        const { deleteProvider } = await import('../support/api')
        await deleteProvider(id)
      })
    }
  },
)

Then('供应商出现在列表中', async function (this: AppWorld) {
  await expect(this.page.locator('li', { hasText: this.currentProviderName })).toBeVisible()
})

When('对该供应商执行连通性检查', async function (this: AppWorld) {
  await this.page
    .locator('li', { hasText: this.currentProviderName })
    .getByRole('button', { name: '连通性检查' })
    .click()
})

Then('显示检查结果', async function (this: AppWorld) {
  // 结果形如 ok(N) 或 fail（外网不可达时为 fail，仍是有效结果呈现）。
  await expect(this.page.locator('li', { hasText: this.currentProviderName })).toContainText(
    /(ok\(|fail)/,
  )
})
