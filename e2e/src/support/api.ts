import { getWorkspace2Api, type Role } from '../generated/api'
import { setApiToken } from './http'

const api = getWorkspace2Api()

export const ROOT_EMAIL = 'root@example.com'
const ROOT_PASSWORD = 'Root12345'
export const E2E_PASSWORD = 'E2e12345'

async function asRoot<T>(fn: () => Promise<T>): Promise<T> {
  const token = await api.loginAuthLoginPost({ email: ROOT_EMAIL, password: ROOT_PASSWORD })
  setApiToken(token.access_token)
  try {
    return await fn()
  } finally {
    setApiToken(null)
  }
}

async function ignoreMissing(fn: () => Promise<unknown>): Promise<void> {
  try {
    await fn()
  } catch (e) {
    const status = (e as { response?: { status?: number } }).response?.status
    if (status !== 404 && status !== 409) throw e
  }
}

/** 存在则复用（可重跑），否则创建；返回用户 id。 */
export async function ensureUser(email: string, role: Role): Promise<string> {
  return asRoot(async () => {
    const users = await api.listUsersUsersGet()
    const found = users.find((u) => u.email === email)
    if (found) return found.id
    const created = await api.createUserUsersPost({ email, password: E2E_PASSWORD, role })
    return created.id
  })
}

export async function deleteUser(id: string): Promise<void> {
  await asRoot(() => ignoreMissing(() => api.deleteUserUsersUserIdDelete(id)))
}

export async function deleteProvider(id: string): Promise<void> {
  await asRoot(() => ignoreMissing(() => api.deleteProviderModelsProvidersProviderIdDelete(id)))
}

export async function deleteWorkflow(id: string): Promise<void> {
  await asRoot(() => ignoreMissing(() => api.deleteWorkflowWorkflowsWorkflowIdDelete(id)))
}

/** 按名定位（浏览器建完资源后，准备层读回 id 供清理）。 */
export async function findProviderByName(name: string): Promise<string | null> {
  return asRoot(async () => {
    const list = await api.listProvidersModelsProvidersGet()
    return list.find((p) => p.name === name)?.id ?? null
  })
}

export async function findWorkflowByName(name: string): Promise<string | null> {
  return asRoot(async () => {
    const list = await api.listWorkflowsWorkflowsGet()
    return list.find((w) => w.name === name)?.id ?? null
  })
}

/** 建一个 llm 引用指定供应商的流程（删除拒绝场景的准备层）。 */
export async function createWorkflowWithLlm(name: string, providerId: string): Promise<string> {
  return asRoot(async () => {
    const wf = await api.createWorkflowWorkflowsPost({
      name,
      description: '',
      dag: {
        nodes: [
          { id: 'start', type: 'start', config: {} },
          {
            id: 'l',
            type: 'llm',
            config: { provider_id: providerId, model: 'm', prompt: 'hi', output_key: 'a' },
          },
          { id: 'end', type: 'end', config: {} },
        ],
        edges: [
          { id: 'e1', source: 'start', target: 'l' },
          { id: 'e2', source: 'l', target: 'end' },
        ],
      },
    })
    return wf.id
  })
}

/** e2e:full 重置用：删掉所有 E2E 前缀资源（先子后主：流程→供应商→用户）。 */
export async function resetE2EResources(): Promise<{ workflows: number; providers: number; users: number }> {
  return asRoot(async () => {
    const [workflows, providers, users] = await Promise.all([
      api.listWorkflowsWorkflowsGet(),
      api.listProvidersModelsProvidersGet(),
      api.listUsersUsersGet(),
    ])
    const { hasE2EPrefix } = await import('./naming')
    let w = 0
    let p = 0
    let u = 0
    for (const wf of workflows.filter((x) => hasE2EPrefix(x.name))) {
      await ignoreMissing(() => api.deleteWorkflowWorkflowsWorkflowIdDelete(wf.id))
      w += 1
    }
    for (const pr of providers.filter((x) => hasE2EPrefix(x.name))) {
      await ignoreMissing(() => api.deleteProviderModelsProvidersProviderIdDelete(pr.id))
      p += 1
    }
    const { E2E_PREFIX } = await import('./naming')
    for (const usr of users.filter((x) => x.email.startsWith(`${E2E_PREFIX}_`) || x.email.startsWith('E2E'))) {
      await ignoreMissing(() => api.deleteUserUsersUserIdDelete(usr.id))
      u += 1
    }
    return { workflows: w, providers: p, users: u }
  })
}
