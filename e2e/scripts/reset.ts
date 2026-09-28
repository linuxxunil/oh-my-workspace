import { resetE2EResources } from '../src/support/api'

async function main(): Promise<void> {
  const r = await resetE2EResources()
  console.log(`[e2e:full] reset done: ${JSON.stringify(r)}`)
}

void main()
