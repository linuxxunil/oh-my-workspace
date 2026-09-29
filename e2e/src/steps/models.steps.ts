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
    try {
      await page.getByRole('textbox', { name: '名称' }).fill(name)
      await page.getByRole('combobox', { name: '类型' }).selectOption(type)
      await page.getByRole('textbox', { name: '地址' }).fill(url)
      await page.getByRole('button', { name: '模型供应商' }).click()
      await expect(page.locator('li', { hasText: name })).toBeVisible()
    } catch (e) {
      // 建了一半不能留孤儿，按名清掉再抛原错。
      const { deleteProvider, findProviderByName } = await import('../support/api')
      await findProviderByName(name)
        .then((id) => (id ? deleteProvider(id) : undefined))
        .catch(() => undefined)
      throw e
    }
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

When('打开该供应商的编辑并更换 API Key 为 {string}', async function (
  this: AppWorld,
  apiKey: string,
) {
  const row = this.page.locator('li', { hasText: this.currentProviderName })
  await row.getByRole('button', { name: '编辑' }).click()
  await row.getByRole('textbox', { name: 'API Key' }).fill(apiKey)
  await row.getByRole('button', { name: '保存' }).click()
  // 编辑表单收起即保存成功。
  await expect(row.getByRole('button', { name: '编辑' })).toBeVisible()
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

When('删除该供应商', async function (this: AppWorld) {
  const row = this.page.locator('li', { hasText: this.currentProviderName })
  // Playwright 默认 dismiss 原生 confirm，先挂 accept 再点（一次弹窗先建等待）。
  this.page.once('dialog', (d) => void d.accept())
  await row.getByRole('button', { name: '删除', exact: true }).click()
})

Then('供应商从列表中消失', async function (this: AppWorld) {
  await expect(this.page.locator('li', { hasText: this.currentProviderName })).toHaveCount(0)
  this.providerIds = []
  this.currentProviderId = ''
})

When('准备一个引用该供应商的流程', async function (this: AppWorld) {
  const { createWorkflowWithLlm } = await import('../support/api')
  const { e2eName } = await import('../support/naming')
  const { deleteWorkflow } = await import('../support/api')
  const wname = e2eName('bound')
  const wid = await createWorkflowWithLlm(wname, this.currentProviderId)
  this.workflowIds.push(wid)
  this.registerCleanup(() => deleteWorkflow(wid))
})

Then('显示被引用拒绝且供应商仍在', async function (this: AppWorld) {
  const row = this.page.locator('li', { hasText: this.currentProviderName })
  await expect(row.getByRole('alert')).toContainText('引用')
  await expect(row).toBeVisible()
})
