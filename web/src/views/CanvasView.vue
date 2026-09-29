<template>
  <section aria-labelledby="canvas-title">
    <h1 id="canvas-title">{{ t('flows.title') }} / {{ workflowId }}</h1>
    <div class="toolbar" role="toolbar" aria-label="节点面板">
      <Button v-for="kind in kinds" :key="kind" variant="secondary" size="sm" @click="addNode(kind)">
        + {{ kind }}
      </Button>
      <Button variant="secondary" size="sm" :disabled="!selectedNode" @click="removeSelected">
        删除选中
      </Button>
    </div>
    <div class="canvas">
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
    <form
      v-if="selectedNode"
      class="flex max-w-xl flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="applyConfig"
    >
      <h2 class="text-sm font-semibold text-slate-800">
        节点 {{ selectedNode.id }}（{{ nodeTypeOf(selectedNode) }}）
      </h2>
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
          {{ t('flows.save') }}配置
        </Button>
      </div>
    </form>
    <div class="actions">
      <Button variant="secondary" size="sm" @click="save">{{ t('flows.save') }}版本</Button>
      <Button variant="secondary" size="sm" @click="publish">{{ t('flows.publish') }}</Button>
      <p v-if="notice" role="status">{{ notice }}</p>
    </div>
    <form @submit.prevent="run">
      <label for="run-inputs">{{ t('flows.inputs') }}</label>
      <textarea id="run-inputs" v-model="inputsText" rows="4" cols="60">{}</textarea>
      <Button type="submit" variant="primary" size="sm">{{ t('flows.run') }}</Button>
    </form>
    <pre v-if="outputs" aria-label="outputs">{{ outputs }}</pre>
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
