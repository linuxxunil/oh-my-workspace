import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Badge } from './index'

// 回归说明：Badge 只表达语义色，不断言裸 class（styling.md：状态经 data 属性）。
describe('Badge', () => {
  it('默认灰并渲染文本', () => {
    const w = mount(Badge, { slots: { default: 'member' } })
    expect(w.get('span').attributes('data-tone')).toBe('gray')
    expect(w.text()).toBe('member')
  })

  it('tone 经 data 属性表达', () => {
    const w = mount(Badge, { props: { tone: 'indigo' }, slots: { default: 'x' } })
    expect(w.get('span').attributes('data-tone')).toBe('indigo')
  })
})
