import { Then, When } from '@cucumber/cucumber'
import { expect, type Locator, type Page } from 'playwright/test'
import { e2eName } from '../support/naming'
import type { AppWorld } from '../support/world'

async function dragHandle(page: Page, from: Locator, to: Locator): Promise<void> {
  await from.hover()
  await page.mouse.down()
  await to.hover()
  await page.mouse.up()
}

/** 删边（模板自带的 start→end 直连必须删：与 start→code→end 扇出会并发写 vars，
 * LangGraph 无 reducer 即 INVALID_CONCURRENT_GRAPH_UPDATE）。带重试，删不掉即失败。 */
async function deleteEdge(page: Page, edgeId: string): Promise<void> {
  const edge = page.locator(`.vue-flow__edge[data-id="${edgeId}"]`)
  for (let i = 0; i < 3; i += 1) {
    if ((await edge.count()) === 0) return
    await edge.first().click({ timeout: 8000 })
    await page.keyboard.press('Backspace')
    try {
      await expect(edge).toHaveCount(0, { timeout: 3000 })
      return
    } catch {
      // 未选中或动画期，重试。
    }
  }
  await expect(edge).toHaveCount(0, { timeout: 3000 })
}

/** 选中节点（fit-view 动画期间点击可能落空，带重试）。 */
async function selectNode(node: Locator): Promise<void> {
  for (let i = 0; i < 3; i += 1) {
    await node.click({ timeout: 10_000 })
    try {
      await expect(node).toHaveClass(/selected/, { timeout: 3000 })
      return
    } catch {
      // 动画期点空，重试。
    }
  }
  await expect(node).toHaveClass(/selected/, { timeout: 3000 })
}

When('新建流程 名称以 {string} 为前缀', async function (this: AppWorld, prefix: string) {
  void prefix
  const name = e2eName('flow')
  const { page } = this
  const { gotoSection } = await import('../support/nav')
  await gotoSection(this, '/workflows')
  // 注：section 经 aria-labelledby 亦被命名，getByLabel 会命中 section+input 两个，
  // 故表单控件一律用 textbox/combobox role 加名称定位。
  try {
    await page.getByRole('textbox', { name: '流程' }).fill(name)
    await page.getByRole('button', { name: '新建流程' }).click()
    await expect(page.locator('li', { hasText: name })).toBeVisible()
  } catch (e) {
    // 建了一半（POST 已成功但列表未刷出）不能留孤儿，按名清掉再抛原错。
    const { deleteWorkflow, findWorkflowByName } = await import('../support/api')
    await findWorkflowByName(name)
      .then((id) => (id ? deleteWorkflow(id) : undefined))
      .catch(() => undefined)
    throw e
  }
  this.currentWorkflowName = name

  const { findWorkflowByName } = await import('../support/api')
  await expect.poll(() => findWorkflowByName(name), { timeout: 10_000 }).not.toBeNull()
  const wid = (await findWorkflowByName(name)) as string
  this.currentWorkflowId = wid
  this.workflowIds.push(wid)
  this.registerCleanup(async () => {
    const { deleteWorkflow } = await import('../support/api')
    await deleteWorkflow(wid)
  })
})

When(
  '在画布中连线 start → code → end 并保存为新版本',
  { timeout: 60_000 },
  async function (this: AppWorld) {
  const { page } = this
  const { currentWorkflowName: name, currentWorkflowId: wid } = this
  const { gotoSection } = await import('../support/nav')
  await gotoSection(this, '/workflows')
  await page.locator('li', { hasText: name }).getByRole('link', { name: '打开画布' }).click()
  await expect(page).toHaveURL(new RegExp(`/workflows/${wid}`))

  await expect(page.locator('.vue-flow__node[data-id="start"]')).toBeVisible()
  await page.getByRole('toolbar').getByRole('button', { name: '+ code' }).click()
  const codeNode = page.locator('.vue-flow__node[data-id^="code-"]')
  await expect(codeNode).toBeVisible()

  // 配 code 节点：m = n * 2（类型表单：代码 + 输出键）。
  await selectNode(codeNode)
  await page.getByRole('textbox', { name: '代码' }).fill('result = data["n"] * 2')
  await page.getByRole('textbox', { name: '输出键', exact: true }).fill('m')
  await page.getByRole('button', { name: '保存配置' }).click()
  await expect(page.getByRole('status')).toHaveText('ok')
  // 右侧面板收起后再连线（展开的面板会遮挡节点 handle，真实操作亦如此）。
  await page.getByRole('button', { name: '关闭配置面板' }).click()
  await expect(page.locator('aside[aria-label="节点配置"]')).toHaveCount(0)

  // 连线 start→code→end。
  const startNode = page.locator('.vue-flow__node[data-id="start"]')
  const endNode = page.locator('.vue-flow__node[data-id="end"]')
  await dragHandle(
    page,
    startNode.locator('.vue-flow__handle.source'),
    codeNode.locator('.vue-flow__handle.target'),
  )
  await dragHandle(
    page,
    codeNode.locator('.vue-flow__handle.source'),
    endNode.locator('.vue-flow__handle.target'),
  )
  await expect(page.locator('.vue-flow__edge')).toHaveCount(3)

  // 模板自带的 start→end 直连必须删（见 deleteEdge 注释），硬断言。
  await deleteEdge(page, 'e1')

  await page.getByRole('button', { name: '保存版本' }).click()
  await expect(page.getByRole('status')).toContainText('saved')
  },
)

When('发布该流程并以输入 {string} 运行', async function (this: AppWorld, inputsJson: string) {
  const { page } = this
  await page.getByRole('button', { name: '发布' }).click()
  await expect(page.getByRole('status')).toHaveText('published')
  await page.getByRole('textbox', { name: '输入 JSON' }).fill(inputsJson)
  await page.getByRole('button', { name: '运行' }).click()
})

Then('运行历史中出现 {word} 记录', async function (this: AppWorld, status: string) {
  // 页内运行历史区（S3 新增）：Badge 文本与状态精确一致。
  const history = this.page.locator('section', {
    has: this.page.getByRole('heading', { name: '运行历史' }),
  })
  await expect(history.getByText(status, { exact: true }).first()).toBeVisible()
})

Then('运行状态为 {word} 且输出 {word} 为 {int}', async function (
  this: AppWorld,
  status: string,
  key: string,
  value: number,
) {
  const outputs = this.page.getByLabel('outputs')
  await expect(outputs).toContainText(`"status": "${status}"`)
  await expect(outputs).toContainText(`"${key}": ${value}`)
})
