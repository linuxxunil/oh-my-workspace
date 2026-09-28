import type { Edge, Node } from '@vue-flow/core'
import type { Dag, DagEdge, DagNode } from '../service/generated/api'

// DAG JSON ↔ VueFlow 的纯函数（画布唯一转换 owner，可单测）。
export function toVueFlow(dag: Dag): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = (dag.nodes ?? []).map((n: DagNode, i: number) => ({
    id: n.id,
    type: 'default',
    position: { x: n.position?.x ?? (i % 4) * 220, y: n.position?.y ?? Math.floor(i / 4) * 140 },
    data: { nodeType: n.type, config: n.config ?? {} },
    label: `${n.type}:${n.id}`,
  }))
  const edges: Edge[] = (dag.edges ?? []).map((e: DagEdge) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.condition ?? undefined,
    data: { condition: e.condition ?? null },
  }))
  return { nodes, edges }
}

let counter = 0
export function newNodeId(prefix: string): string {
  counter += 1
  return `${prefix}-${Date.now().toString(36)}-${counter}`
}

export function fromVueFlow(nodes: Node[], edges: Edge[]): Dag {
  return {
    nodes: nodes.map((n) => ({
      id: n.id,
      type: (n.data?.nodeType ?? 'llm') as DagNode['type'],
      config: (n.data?.config ?? {}) as Record<string, unknown>,
      position: { x: n.position.x, y: n.position.y },
    })),
    edges: edges.map((e, i) => ({
      id: e.id ?? `e-${i}`,
      source: e.source,
      target: e.target,
      // VueFlow 默认 label 为空串，空串无业务含义，必须归一为 null，
      // 否则后端 DAG 契约（'true'|'false'|null）422。
      condition: (e.data?.condition || e.label || null) as 'true' | 'false' | null,
    })),
  }
}

export function blankDag(): Dag {
  return {
    nodes: [
      { id: 'start', type: 'start', config: {}, position: { x: 80, y: 200 } },
      { id: 'end', type: 'end', config: {}, position: { x: 480, y: 200 } },
    ],
    edges: [{ id: 'e1', source: 'start', target: 'end', condition: null }],
  }
}
