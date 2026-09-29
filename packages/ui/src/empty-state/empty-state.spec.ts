import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { EmptyState } from './index'

// 回归说明：空态标题文本即契约（test.md：文本优先），动作文案由调用方插槽拥有。
describe('EmptyState', () => {
  it('标题与描述呈现', () => {
    const w = mount(EmptyState, { props: { title: '暂无流程', description: '先新建一个吧' } })
    expect(w.text()).toContain('暂无流程')
    expect(w.text()).toContain('先新建一个吧')
  })

  it('动作用插槽拥有', () => {
    const w = mount(EmptyState, {
      props: { title: '空' },
      slots: { default: '<button>新建</button>' },
    })
    expect(w.get('button').text()).toBe('新建')
  })
})
