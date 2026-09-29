import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Button } from './index'

// 回归说明：按钮是全站动作唯一入口；loading 必须阻断激活但保留焦点（button.md 契约）。
// 增量证据：默认/禁用/加载三态 + spinner 纯装饰（aria-hidden）不断言裸 class。
describe('Button', () => {
  it('默认渲染原生 button，插槽文本命名', () => {
    const w = mount(Button, { slots: { default: '保存' } })
    const btn = w.get('button')
    expect(btn.attributes('type')).toBe('button')
    expect(btn.text()).toBe('保存')
  })

  it('type=submit 透传（表单提交边界）', () => {
    const w = mount(Button, { props: { type: 'submit' }, slots: { default: '提交' } })
    expect(w.get('button').attributes('type')).toBe('submit')
  })

  it('disabled 原生禁用并移出激活', async () => {
    const w = mount(Button, { props: { disabled: true }, slots: { default: '删' } })
    expect(w.get('button').attributes('disabled')).toBeDefined()
    await w.get('button').trigger('click')
    expect(w.emitted('click')).toBeUndefined()
  })

  it('loading 阻断激活但保留焦点与标签', async () => {
    const w = mount(Button, { props: { loading: true }, slots: { default: '保存' } })
    const btn = w.get('button')
    expect(btn.attributes('aria-disabled')).toBe('true')
    expect(btn.attributes('disabled')).toBeUndefined()
    await btn.trigger('click')
    expect(w.emitted('click')).toBeUndefined()
    expect(btn.text()).toBe('保存')
    expect(w.find('[aria-hidden="true"]').exists()).toBe(true)
  })

  it('非 loading 点击透出', async () => {
    const w = mount(Button, { slots: { default: '走' } })
    await w.get('button').trigger('click')
    expect(w.emitted('click')).toHaveLength(1)
  })
})
