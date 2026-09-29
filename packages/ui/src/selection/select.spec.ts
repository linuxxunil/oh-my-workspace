import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Select } from './index'

// 回归说明：触发式下拉标签与值分离（selection.md），变更只给最小载荷。
describe('Select', () => {
  const options = [
    { value: 'openai_compatible', label: 'openai_compatible' },
    { value: 'opencode_go', label: 'opencode_go' },
  ]

  it('渲染选项且标签值分离', () => {
    const w = mount(Select, { props: { modelValue: 'openai_compatible', options } })
    const opts = w.findAll('option')
    expect(opts).toHaveLength(2)
    expect(opts[1]?.text()).toBe('opencode_go')
  })

  it('变更透出选中值', async () => {
    const w = mount(Select, { props: { modelValue: 'openai_compatible', options } })
    await w.get('select').setValue('opencode_go')
    expect(w.emitted('update:modelValue')).toEqual([['opencode_go']])
  })
})
