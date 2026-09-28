import { describe, expect, it } from 'vitest'
import { blankDag, fromVueFlow, toVueFlow } from './dag'
import type { DagEdge, DagNode } from '../service/generated/api'

// 回归说明：画布存取是 workflow 核心链路；fromVueFlow 把 if 出边 condition 丢了会导致后端 422。
// 增量证据：往返 blankDag 并断言边 condition 保留 null，if 双边保留 true/false。
describe('dag vue-flow 转换', () => {
  it('blankDag 往返保持结构', () => {
    const dag = blankDag()
    const { nodes, edges } = toVueFlow(dag)
    expect(nodes).toHaveLength(2)
    const back = fromVueFlow(nodes, edges)
    expect(back.nodes.map((n: DagNode) => n.id).sort()).toEqual(['end', 'start'])
    expect(back.edges[0]?.condition).toBeNull()
  })

  it('if 双边 condition 往返保留', () => {
    const { nodes, edges } = toVueFlow({
      nodes: [
        { id: 's', type: 'start', config: {} },
        { id: 'i', type: 'if', config: { var: 'b', equals: 'yes' } },
        { id: 'a', type: 'end', config: {} },
        { id: 'b', type: 'end', config: {} },
      ],
      edges: [
        { id: 'e1', source: 's', target: 'i', condition: null },
        { id: 'e2', source: 'i', target: 'a', condition: 'true' },
        { id: 'e3', source: 'i', target: 'b', condition: 'false' },
      ],
    })
    const back = fromVueFlow(nodes, edges)
    const conds = back.edges
      .filter((e: DagEdge) => e.source === 'i')
      .map((e: DagEdge) => e.condition)
      .sort()
    expect(conds).toEqual(['false', 'true'])
  })

  it('拖拽新边 label 空串归一为 null（否则后端 422）', () => {
    // 回归说明：VueFlow 拖拽连线产生的边 label 默认为 ''，透出会导致保存版本 422。
    // 增量证据：构造 label '' 且 data.condition null 的边，断言输出 condition 为 null。
    const { nodes } = toVueFlow(blankDag())
    const codeNode = {
      id: 'code-x',
      type: 'default',
      position: { x: 0, y: 0 },
      label: 'code',
      data: { nodeType: 'code', config: {} },
    }
    const edges = [
      { id: 'e1', source: 'start', target: 'end', label: '', data: { condition: null } },
      { id: 'e2', source: 'start', target: 'code-x', label: '', data: { condition: null } },
      { id: 'e3', source: 'code-x', target: 'end', label: '', data: { condition: null } },
    ]
    const back = fromVueFlow(
      [...nodes, codeNode] as unknown as Parameters<typeof fromVueFlow>[0],
      edges as unknown as Parameters<typeof fromVueFlow>[1],
    )
    expect(back.edges.map((e: DagEdge) => e.condition)).toEqual([null, null, null])
  })
})
