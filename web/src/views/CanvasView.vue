<template>
  <section aria-labelledby="canvas-title" class="flex flex-col gap-4">
    <h1 id="canvas-title" class="text-lg font-semibold text-slate-800">
      {{ t('flows.title') }}
      <span class="font-mono text-xs font-normal text-slate-600">/ {{ workflowId }}</span>
    </h1>
    <div class="toolbar" role="toolbar" :aria-label="t('canvas.nodePanel')">
      <Button v-for="kind in kinds" :key="kind" variant="secondary" size="sm" @click="addNode(kind)">
        + {{ kind }}
      </Button>
      <Button variant="secondary" size="sm" :disabled="!selectedNode" @click="removeSelected">
        {{ t('canvas.deleteSelected') }}
      </Button>
    </div>
    <div class="flex items-stretch gap-4">
      <div class="canvas min-w-0 flex-1">
        <VueFlow
          ref="flow"
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          @connect="onConnect"
          @node-click="onNodeClick"
          fit-view-on-init
        >
          <Background pattern-color="#cbd5e1" :gap="24" />
          <MiniMap pannable zoomable />
          <Controls position="bottom-right" />
        </VueFlow>
      </div>
      <aside
        v-if="selectedNode"
        class="flex w-80 shrink-0 flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
        :aria-label="t('canvas.configPanel')"
      >
        <div class="flex items-center gap-2">
          <Badge tone="indigo">{{ selectedKind }}</Badge>
          <p class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">
            {{ t('canvas.nodeConfig', { id: selectedNode.id }) }}
          </p>
          <Button
            variant="secondary"
            size="sm"
            :aria-label="t('canvas.closePanel')"
            @click="selectedNode = null"
          >
            ×
          </Button>
        </div>
        <form class="flex flex-col gap-4" @submit.prevent="applyConfig">
          <p v-if="selectedKind === 'start' || selectedKind === 'end'" class="text-sm text-slate-500">
            {{ t('canvas.noConfig') }}
          </p>
      <template v-if="selectedKind === 'llm'">
        <Field input-id="cfg-provider" :label="t('canvas.provider')">
          <template #default="{ inputId }">
            <Select
              :id="inputId"
              v-model="draft.provider_id"
              :options="providerOptions"
              required
            />
          </template>
        </Field>
        <p v-if="providersPending" class="text-xs text-slate-500">{{ t('canvas.loadingProviders') }}</p>
        <Field input-id="cfg-model" :label="t('canvas.model')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.model" required />
          </template>
        </Field>
        <Field input-id="cfg-prompt" :label="t('canvas.prompt')">
          <template #default="{ inputId }">
            <Textarea :id="inputId" v-model="draft.prompt" :rows="4" required />
          </template>
        </Field>
        <Field input-id="cfg-output" :label="t('canvas.outputKey')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.output_key" required />
          </template>
        </Field>
      </template>
      <template v-if="selectedKind === 'code'">
        <Field input-id="cfg-code" :label="t('canvas.code')">
          <template #default="{ inputId }">
            <Textarea :id="inputId" v-model="draft.code" :rows="8" class="font-mono" required />
          </template>
        </Field>
        <Field input-id="cfg-output" :label="t('canvas.outputKey')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.output_key" required />
          </template>
        </Field>
      </template>
      <template v-if="selectedKind === 'if'">
        <Field input-id="cfg-var" :label="t('canvas.varName')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.var" required />
          </template>
        </Field>
        <Field input-id="cfg-equals" :label="t('canvas.equals')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.equals" required />
          </template>
        </Field>
      </template>
      <template v-if="selectedKind === 'retrieval'">
        <Field input-id="cfg-query" :label="t('canvas.query')">
          <template #default="{ inputId }">
            <Textarea :id="inputId" v-model="draft.query" :rows="3" required />
          </template>
        </Field>
        <Field input-id="cfg-topk" :label="t('canvas.topK')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.top_k" type="number" required />
          </template>
        </Field>
        <Field input-id="cfg-output" :label="t('canvas.outputKey')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="draft.output_key" required />
          </template>
        </Field>
      </template>
          <div>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              :disabled="selectedKind === 'start' || selectedKind === 'end'"
            >
              {{ t('canvas.saveConfig') }}
            </Button>
          </div>
        </form>
      </aside>
    </div>
    <div class="actions flex items-center gap-2">
      <Button variant="secondary" size="sm" @click="save">{{ t('canvas.saveVersion') }}</Button>
      <Button variant="secondary" size="sm" @click="publish">{{ t('flows.publish') }}</Button>
      <p v-if="notice" role="status" class="text-sm text-slate-600">{{ notice }}</p>
    </div>
    <form
      class="flex max-w-xl flex-col gap-3 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="run"
    >
      <Field input-id="run-inputs" :label="t('flows.inputs')">
        <template #default="{ inputId }">
          <Textarea :id="inputId" v-model="inputsText" :rows="3" class="font-mono" />
        </template>
      </Field>
      <div>
        <Button type="submit" variant="primary" size="sm">{{ t('flows.run') }}</Button>
      </div>
    </form>
    <pre
      v-if="outputs"
      aria-label="outputs"
      class="max-w-xl overflow-auto rounded-xl bg-slate-900 p-4 font-mono text-xs text-slate-100"
    >{{ outputs }}</pre>
    <section aria-labelledby="runs-title" class="flex max-w-xl flex-col gap-2">
      <h2 id="runs-title" class="text-sm font-semibold text-slate-800">
        {{ t('canvas.runHistory') }}
      </h2>
      <p v-if="runsLoading" class="text-xs text-slate-600">…</p>
      <p v-else-if="!runs.length" class="text-xs text-slate-600">{{ t('canvas.noRuns') }}</p>
      <ul v-else class="flex flex-col gap-2">
        <li
          v-for="r in runs"
          :key="r.id"
          class="rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
        >
          <div class="flex items-center gap-2">
            <Badge :tone="r.status === 'succeeded' ? 'green' : 'red'">{{ r.status }}</Badge>
            <span class="min-w-0 flex-1 truncate font-mono text-xs text-slate-500">{{ r.id }}</span>
          </div>
          <p v-if="r.error" class="mt-1 truncate text-xs text-red-700">{{ r.error }}</p>
          <details v-if="r.outputs" class="mt-1">
            <summary class="cursor-pointer text-xs text-indigo-700">
              {{ t('canvas.runOutputs') }}
            </summary>
            <pre
              class="mt-1 overflow-auto rounded-lg bg-slate-900 p-3 font-mono text-xs text-slate-100"
            >{{ formatOutputs(r.outputs) }}</pre>
          </details>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import {
  VueFlow,
  type Connection,
  type Edge as FlowEdge,
  type Node as FlowNode,
  type NodeMouseEvent,
} from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { Badge } from '@/packages/ui/badge'
import { Button } from '@/packages/ui/button'
import { Field } from '@/packages/ui/form'
import { Textarea, TextInput } from '@/packages/ui/input'
import { Select } from '@/packages/ui/selection'
import CanvasNode from '../components/CanvasNode.vue'

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
  useListProvidersModelsProvidersGet,
  type Dag,
  type RunResponse,
} from '../service/generated/api'
import { fromVueFlow, newNodeId, toVueFlow } from '../utils/dag'

const { t } = useI18n()
const route = useRoute()
const workflowId = String(route.params.id)
const flowRef = useTemplateRef('flow')

// 库内 Controls 图标按钮无可访问名（axe button-name），产品层挂载后补齐。
onMounted(() => {
  const root = flowRef.value?.$el as HTMLElement | undefined
  const labels: Array<[string, string]> = [
    ['vue-flow__controls-zoomin', t('canvas.zoomIn')],
    ['vue-flow__controls-zoomout', t('canvas.zoomOut')],
    ['vue-flow__controls-fitview', t('canvas.fitView')],
    ['vue-flow__controls-interactive', t('canvas.toggleInteractive')],
  ]
  for (const [cls, label] of labels) {
    root?.querySelector(`.${cls}`)?.setAttribute('aria-label', label)
  }
})

const kinds = ['llm', 'code', 'if', 'retrieval', 'end'] as const
// 自定义节点注册：画布内全部节点走 flowNode（toVueFlow 进来的 'default' 在 load 处归一）。
const nodeTypes = { flowNode: CanvasNode }
const nodes = ref<N[]>([])
const edges = ref<E[]>([])
const selectedNode = ref<N | null>(null)
// 类型表单草稿：全字符串，提交时按 kind 组装（键名对齐 api/src/core/graph.py）。
const draft = ref<Record<string, string>>({})
const inputsText = ref('{}')
const outputs = ref('')
const notice = ref('')
const runs = ref<RunResponse[]>([])
const runsLoading = ref(false)

async function loadRuns() {
  runsLoading.value = true
  try {
    runs.value = await listRunsWorkflowsWorkflowIdRunsGet(workflowId)
  } finally {
    runsLoading.value = false
  }
}
void loadRuns()

function formatOutputs(o: unknown): string {
  try {
    return JSON.stringify(o, null, 2)
  } catch {
    return String(o)
  }
}

const providersQuery = useListProvidersModelsProvidersGet()
const providersPending = computed(() => providersQuery.isPending.value === true)
const providerOptions = computed(() =>
  (providersQuery.data.value ?? []).map((p) => ({ value: p.id, label: p.name })),
)
const selectedKind = computed(() => (selectedNode.value ? nodeTypeOf(selectedNode.value) : ''))

async function load() {
  const ver = await latestVersionWorkflowsWorkflowIdVersionsLatestGet(workflowId)
  const dag = ver.dag as unknown as Dag
  const vf = toVueFlow(dag)
  nodes.value = (vf.nodes as unknown as N[]).map((n) => ({ ...n, type: 'flowNode' }))
  edges.value = vf.edges as unknown as E[]
}
void load()

function nodeTypeOf(n: N): string {
  return String(n.data?.nodeType ?? '')
}

function addNode(kind: (typeof kinds)[number]) {
  const node: N = {
    id: newNodeId(kind),
    type: 'flowNode',
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
  const cfg = node.data?.config ?? {}
  draft.value = {
    provider_id: String(cfg['provider_id'] ?? ''),
    model: String(cfg['model'] ?? ''),
    prompt: String(cfg['prompt'] ?? ''),
    code: String(cfg['code'] ?? ''),
    output_key: String(cfg['output_key'] ?? ''),
    var: String(cfg['var'] ?? ''),
    equals: String(cfg['equals'] ?? ''),
    query: String(cfg['query'] ?? ''),
    top_k: String(cfg['top_k'] ?? '3'),
  }
}
function removeSelected() {
  if (!selectedNode.value) return
  // 原生二次确认（无 dialog 基元）；取消即返回。
  if (!window.confirm(t('canvas.confirmRemoveNode', { id: selectedNode.value.id }))) return
  const id = selectedNode.value.id
  nodes.value = nodes.value.filter((n) => n.id !== id)
  edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
  selectedNode.value = null
}

function applyConfig() {
  if (!selectedNode.value) return
  const d = draft.value
  const kind = nodeTypeOf(selectedNode.value)
  let config: Record<string, unknown> = {}
  if (kind === 'llm') {
    config = { provider_id: d.provider_id, model: d.model, prompt: d.prompt, output_key: d.output_key }
  } else if (kind === 'code') {
    config = { code: d.code, output_key: d.output_key }
  } else if (kind === 'if') {
    config = { var: d.var, equals: d.equals }
  } else if (kind === 'retrieval') {
    config = { query: d.query, top_k: Number(d.top_k) > 0 ? Number(d.top_k) : 3, output_key: d.output_key }
  }
  selectedNode.value.data = { ...selectedNode.value.data, config }
  notice.value = 'ok'
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
    notice.value = t('canvas.invalidInputs')
    return
  }
  const r = await runWorkflowWorkflowsWorkflowIdRunPost(workflowId, { inputs })
  outputs.value = JSON.stringify({ status: r.status, outputs: r.outputs, error: r.error }, null, 2)
  await loadRuns()
}
</script>

<style>
.canvas {
  height: calc(100vh - 340px);
  min-height: 420px;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #fff;
}
.toolbar button {
  margin-right: 8px;
}
.actions {
  margin: 12px 0;
}
/* 边样式（VueFlow 内部类，scoped 穿不透，用非 scoped 块集中覆写）。 */
.vue-flow__edge path.vue-flow__edge-path {
  stroke: #94a3b8;
  stroke-width: 2;
}
.vue-flow__edge.selected path.vue-flow__edge-path {
  stroke: #4f46e5;
}
.vue-flow__connection-path {
  stroke: #4f46e5;
}
</style>
