import { World, type IWorldOptions, setWorldConstructor } from '@cucumber/cucumber'
import type { Browser, BrowserContext, Page } from 'playwright'

export type CleanupFn = () => Promise<void>

/** 场景世界：浏览器身份与 API 身份分开管理，状态只活在场景内。 */
export class AppWorld extends World {
  browser!: Browser
  context!: BrowserContext
  page!: Page

  /** 浏览器当前登录用户邮箱（用户边界层）。 */
  browserEmail = ''
  /** 本场景新建的资源 id（清理用，子资源在前）。 */
  providerIds: string[] = []
  workflowIds: string[] = []
  userIds: string[] = []
  currentProviderId = ''
  currentProviderName = ''
  currentWorkflowId = ''
  currentWorkflowName = ''

  private cleanups: CleanupFn[] = []

  constructor(options: IWorldOptions) {
    super(options)
  }

  get base(): string {
    return process.env.E2E_BASE ?? 'http://localhost:18080'
  }

  registerCleanup(fn: CleanupFn): void {
    this.cleanups.push(fn)
  }

  /** LIFO：后注册的先执行；调用方保证子资源先于主资源注册。 */
  async runCleanups(): Promise<void> {
    while (this.cleanups.length > 0) {
      const fn = this.cleanups.pop() as CleanupFn
      try {
        await fn()
      } catch {
        // 清理尽力而为，不掩盖场景结果。
      }
    }
  }
}

setWorldConstructor(AppWorld)
