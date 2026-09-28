import { expect } from 'playwright/test'
import { E2E_PASSWORD } from './api'
import type { AppWorld } from './world'

const LINKS = { '/workflows': '流程', '/models': '模型', '/users': '用户' } as const
export type SectionPath = keyof typeof LINKS

/** 经 UI 登录（首个 goto，整页加载无妨）。 */
export async function loginViaUI(world: AppWorld): Promise<void> {
  const { page } = world
  await page.goto(`${world.base}/login`)
  await page.getByLabel('邮箱').fill(world.browserEmail)
  await page.getByLabel('密码').fill(E2E_PASSWORD)
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).toHaveURL(/\/workflows$/)
}

/** 站内导航：点主导航 RouterLink，不整页重载（pinia token 纯内存，重载会掉登录）。
 * 若已在 /login（重载发生过），先补一次登录再导航。 */
export async function gotoSection(world: AppWorld, path: SectionPath): Promise<void> {
  const { page } = world
  if (/\/login$/.test(page.url())) await loginViaUI(world)
  await page
    .getByRole('navigation', { name: '主导航' })
    .getByRole('link', { name: LINKS[path] })
    .click()
  await expect(page).toHaveURL(new RegExp(`${path}$`))
}
