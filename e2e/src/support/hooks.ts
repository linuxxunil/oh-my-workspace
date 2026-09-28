import {
  After,
  AfterAll,
  Before,
  BeforeAll,
  setDefaultTimeout,
} from '@cucumber/cucumber'
import { chromium, type Browser } from 'playwright'
import type { AppWorld } from './world'

setDefaultTimeout(30_000)

let browser: Browser | null = null

BeforeAll(async function () {
  browser = await chromium.launch({ headless: true })
})

Before(async function (this: AppWorld) {
  if (!browser) throw new Error('browser 未初始化')
  // 每场景独立 context：状态隔离（见 e2e/AGENTS.md）。
  this.browser = browser
  this.context = await browser.newContext()
  await this.context.tracing.start({ screenshots: true, snapshots: true })
  this.page = await this.context.newPage()
})

After(async function (this: AppWorld, { result, pickle }) {
  if (result?.status === 'FAILED') {
    await this.page.screenshot({ path: `reports/${pickle.name.replace(/[^\w-]+/g, '_')}.png` })
  }
  await this.context.tracing.stop().catch(() => undefined)
  await this.runCleanups()
  await this.context.close()
})

AfterAll(async function () {
  await browser?.close()
  browser = null
})
