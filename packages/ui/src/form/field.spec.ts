import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Field } from './index'

// 回归说明：Field 拥有标签/描述/错误的可访问关系（forms.md），调用方只给 inputId。
describe('Field', () => {
  it('label 关联到插槽输入', () => {
    const w = mount(Field, {
      props: { inputId: 'f-email', label: '邮箱' },
      slots: { default: '<input id="f-email" />' },
    })
    expect(w.get('label[for="f-email"]').text()).toBe('邮箱')
    expect(w.find('#f-email').exists()).toBe(true)
  })

  it('error 走 role=alert 并挂 aria 关系', () => {
    const w = mount(Field, {
      props: { inputId: 'f-x', label: '名称', error: '必填' },
      slots: {
        default: ({ describedBy }: { describedBy?: string }) =>
          `<input id="f-x" aria-describedby="${describedBy ?? ''}" />`,
      },
    })
    const alert = w.get('[role="alert"]')
    expect(alert.text()).toBe('必填')
    expect(alert.attributes('id')).toBe('f-x-error')
  })

  it('无错时 hint 呈现且不抢 alert', () => {
    const w = mount(Field, {
      props: { inputId: 'f-y', label: '地址', hint: 'https 开头' },
      slots: { default: '<input id="f-y" />' },
    })
    expect(w.find('[role="alert"]').exists()).toBe(false)
    expect(w.text()).toContain('https 开头')
  })
})
