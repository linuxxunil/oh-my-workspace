import { createRequire } from 'node:module'
import { Then, When } from '@cucumber/cucumber'
import { expect } from 'playwright/test'
import type { AxeResults } from 'axe-core'
import type { AppWorld } from '../support/world'

const require = createRequire(`${process.cwd()}/package.json`)

interface AxeWindow {
  axe: { run: (doc: Document, opts: unknown) => Promise<AxeResults> }
}

When('在浏览器中打开登录页', async function (this: AppWorld) {
  await this.page.goto(`${this.base}/login`)
})

When('打开当前流程的画布页', async function (this: AppWorld) {
  const { page } = this
  const { currentWorkflowName: name, currentWorkflowId: wid } = this
  const { gotoSection } = await import('../support/nav')
  await gotoSection(this, '/workflows')
  await page.locator('li', { hasText: name }).getByRole('link', { name: '打开画布' }).click()
  await expect(page).toHaveURL(new RegExp(`/workflows/${wid}`))
  await expect(page.locator('.vue-flow')).toBeVisible()
})

Then('当前页无障碍扫描零 critical 与 serious', async function (this: AppWorld) {
  const { page } = this
  await page.addScriptTag({ path: require.resolve('axe-core/axe.min.js') })
  const results = await page.evaluate(async (): Promise<AxeResults> => {
    const w = window as unknown as AxeWindow
    return w.axe.run(document, { resultTypes: ['violations'] })
  })
  const bad = results.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious')
  if (bad.length > 0) {
    const summary = bad
      .map((v) => `${v.id}(${v.impact}): ${v.help} nodes=${v.nodes.length}`)
      .join('\n')
    throw new Error(`a11y 违规:\n${summary}`)
  }
})
