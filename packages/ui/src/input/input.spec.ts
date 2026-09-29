import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { Textarea, TextInput } from './index'

// 回归说明：输入基元拥有 v-model 回环与 invalid 表达，不拥有校验判定。
describe('TextInput', () => {
  it('v-model 回环', async () => {
    const w = mount(TextInput, { props: { modelValue: 'a', 'onUpdate:modelValue': () => {} } })
    await w.get('input').setValue('ab')
    expect(w.emitted('update:modelValue')).toEqual([['ab']])
  })

  it('invalid 同时表达 data 与 aria', () => {
    const ok = mount(TextInput, { props: { modelValue: '' } })
    expect(ok.get('input').attributes('data-invalid')).toBeUndefined()
    const bad = mount(TextInput, { props: { modelValue: '', invalid: true } })
    expect(bad.get('input').attributes('data-invalid')).toBeDefined()
    expect(bad.get('input').attributes('aria-invalid')).toBe('true')
  })
})

describe('Textarea', () => {
  it('v-model 回环与 rows 透传', async () => {
    const w = mount(Textarea, { props: { modelValue: '', rows: 4 } })
    expect(w.get('textarea').attributes('rows')).toBe('4')
    await w.get('textarea').setValue('hi')
    expect(w.emitted('update:modelValue')).toEqual([['hi']])
  })
})
