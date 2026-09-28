<template>
  <section aria-labelledby="canvas-title">
    <h1 id="canvas-title">{{ t('flows.title') }} / {{ workflowId }}</h1>
    <div class="toolbar" role="toolbar" aria-label="节点面板">
      <button v-for="kind in kinds" :key="kind" type="button" @click="addNode(kind)">
        + {{ kind }}
      </button>
      <button type="button" :disabled="!selectedNode" @click="removeSelected">删除选中</button>
    </div>
    <div class="canvas">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        @connect="onConnect"
        @node-click="onNodeClick"
        fit-view-on-init
      >
      </VueFlow>
    </div>
    <form v-if="selectedNode" @submit.prevent="applyConfig">
      <h2>节点 {{ selectedNode.id }}（{{ nodeTypeOf(selectedNode) }}）</h2>
      <label for="node-config">config JSON</label>
      <textarea id="node-config" v-model="configText" rows="8" cols="60"></textarea>
      <button type="submit">{{ t('flows.save') }}配置</button>
    </form>
    <div class="actions">
      <button type="button" @click="save">{{ t('flows.save') }}版本</button>
      <button type="button" @click="publish">{{ t('flows.publish') }}</button>
      <p v-if="notice" role="status">{{ notice }}</p>
    </div>
    <form @submit.prevent="run">
      <label for="run-inputs">{{ t('flows.inputs') }}</label>
      <textarea id="run-inputs" v-model="inputsText" rows="4" cols="60">{}</textarea>
      <button type="submit">{{ t('flows.run') }}</button>
    </form>
    <pre v-if="outputs" aria-label="outputs">{{ outputs }}</pre>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import {
  VueFlow,
  type Connection,
  type Edge as FlowEdge,
  type Node as FlowNode,
  type NodeMouseEvent,
} from '@vue-flow/core'

// 本地窄类型：@vue-flow/core v1 Node/Edge 联合泛型在 vue-tsc 下实例化过深（TS2589），
// 状态用结构化子集，模板 v-model 处具名压制（运行时结构兼容）；升级 v2/官方修复后移除压制。
interface N {
  id: string
  type?: string
  position: { x: number; y: number }
  label?: string
  data?: { nodeType?: string; config?: Record<string, unknown> }
}
interface E {
  id: string
  source: string
  target: string
  label?: string
  data?: { condition?: 'true' | 'false' | null }
}
import {
  latestVersionWorkflowsWorkflowIdVersionsLatestGet,
  listRunsWorkflowsWorkflowIdRunsGet,
  newVersionWorkflowsWorkflowIdVersionsPost,
  publishWorkflowsWorkflowIdPublishPost,
  runWorkflowWorkflowsWorkflowIdRunPost,
  type Dag,
} from '../service/generated/api'
import { fromVueFlow, newNodeId, toVueFlow } from '../utils/dag'

const { t } = useI18n()
const route = useRoute()
const workflowId = String(route.params.id)

const kinds = ['llm', 'code', 'if', 'retrieval', 'end'] as const
const nodes = ref<N[]>([])
const edges = ref<E[]>([])
const selectedNode = ref<N | null>(null)
const configText = ref('')
const inputsText = ref('{}')
const outputs = ref('')
const notice = ref('')

async function load() {
  const ver = await latestVersionWorkflowsWorkflowIdVersionsLatestGet(workflowId)
  const dag = ver.dag as unknown as Dag
  const vf = toVueFlow(dag)
  nodes.value = vf.nodes as unknown as N[]
  edges.value = vf.edges as unknown as E[]
}
void load()

function nodeTypeOf(n: N): string {
  return String(n.data?.nodeType ?? '')
}

function addNode(kind: (typeof kinds)[number]) {
  const node: N = {
    id: newNodeId(kind),
    type: 'default',
    position: { x: 120 + nodes.value.length * 40, y: 120 },
    label: kind,
    data: { nodeType: kind, config: {} },
  }
  nodes.value = [...nodes.value, node]
}

function onConnect(params: Connection) {
  const edge: E = {
    id: newNodeId('e'),
    source: params.source,
    target: params.target,
    data: { condition: null },
  }
  edges.value = [...edges.value, edge]
}

function onNodeClick(event: NodeMouseEvent) {
  const node = event.node as unknown as N
  selectedNode.value = node
  configText.value = JSON.stringify(node.data?.config ?? {}, null, 2)
}
function removeSelected() {
  if (!selectedNode.value) return
  const id = selectedNode.value.id
  nodes.value = nodes.value.filter((n) => n.id !== id)
  edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
  selectedNode.value = null
}

function applyConfig() {
  if (!selectedNode.value) return
  try {
    selectedNode.value.data = {
      ...selectedNode.value.data,
      config: JSON.parse(configText.value) as Record<string, unknown>,
    }
    notice.value = 'ok'
  } catch {
    notice.value = 'config JSON 非法'
  }
}

watch(
  () => edges.value.length,
  () => {
    // if 出边默认补 condition：第一条 true、第二条 false（可在边上改 label 覆盖）。
    const bySource = new Map<string, E[]>()
    for (const e of edges.value) {
      const list = bySource.get(e.source) ?? []
      list.push(e)
      bySource.set(e.source, list)
    }
    for (const [src, list] of bySource) {
      const from = nodes.value.find((n) => n.id === src)
      if (String(from?.data?.nodeType) !== 'if') continue
      list.forEach((e, i) => {
        e.data = { condition: i === 0 ? 'true' : 'false' }
        e.label = i === 0 ? 'true' : 'false'
      })
    }
  },
)

async function save() {
  const dag = fromVueFlow(nodes.value as unknown as FlowNode[], edges.value as unknown as FlowEdge[])
  const ver = await newVersionWorkflowsWorkflowIdVersionsPost(workflowId, { dag })
  notice.value = `v${ver.version_no} saved`
}

async function publish() {
  await publishWorkflowsWorkflowIdPublishPost(workflowId)
  notice.value = 'published'
}

async function run() {
  let inputs: Record<string, unknown> = {}
  try {
    inputs = JSON.parse(inputsText.value) as Record<string, unknown>
  } catch {
    notice.value = 'inputs JSON 非法'
    return
  }
  const r = await runWorkflowWorkflowsWorkflowIdRunPost(workflowId, { inputs })
  outputs.value = JSON.stringify({ status: r.status, outputs: r.outputs, error: r.error }, null, 2)
  await listRunsWorkflowsWorkflowIdRunsGet(workflowId)
}
</script>

<style>
.canvas {
  height: 480px;
  border: 1px solid #ccc;
}
.toolbar button {
  margin-right: 8px;
}
.actions {
  margin: 12px 0;
}
</style>
