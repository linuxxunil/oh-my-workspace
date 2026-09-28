import { Then } from '@cucumber/cucumber'
import type { AppWorld } from '../support/world'

Then('清理以 {string} 为前缀的供应商与用户', async function (this: AppWorld, prefix: string) {
  void prefix
  const { deleteProvider, deleteUser } = await import('../support/api')
  for (const id of this.providerIds) await deleteProvider(id)
  this.providerIds = []
  for (const id of this.userIds) await deleteUser(id)
  this.userIds = []
})

Then('清理以 {string} 为前缀的流程与用户', async function (this: AppWorld, prefix: string) {
  void prefix
  const { deleteUser, deleteWorkflow } = await import('../support/api')
  for (const id of this.workflowIds) await deleteWorkflow(id)
  this.workflowIds = []
  for (const id of this.userIds) await deleteUser(id)
  this.userIds = []
})
