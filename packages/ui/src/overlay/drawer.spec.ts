import { mount } from '@vue/test-utils'
import { h } from 'vue'
import { describe, expect, it } from 'vitest'
import Drawer from './Drawer.vue'
import type { DrawerTriggerProps } from './Drawer.vue'

describe('Drawer', () => {
  it('exposes a modal dialog, locks scrolling, and emits close on Escape', async () => {
    const oldOverflow = document.body.style.overflow
    const wrapper = mount(Drawer, {
      attachTo: document.body,
      props: { open: false, label: 'Navigation' },
      slots: {
        trigger: ({ triggerProps }: { triggerProps: DrawerTriggerProps }) =>
          h('button', triggerProps, 'Open'),
        default: () => h('a', { href: '/workflows' }, 'Workflows'),
      },
    })

    await wrapper.setProps({ open: true })
    await new Promise((resolve) => setTimeout(resolve, 0))
    const dialog = document.querySelector<HTMLElement>('[role="dialog"]')
    expect(dialog?.getAttribute('aria-modal')).toBe('true')
    expect(document.activeElement).toBe(dialog?.querySelector('a'))
    expect(document.body.style.overflow).toBe('hidden')

    dialog?.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }))
    const updates = wrapper.emitted('update:open') ?? []
    expect(updates[updates.length - 1]).toEqual([false])
    await wrapper.setProps({ open: false })

    wrapper.unmount()
    document.body.style.overflow = oldOverflow
  })

  it('cycles Tab focus inside the dialog', async () => {
    const wrapper = mount(Drawer, {
      attachTo: document.body,
      props: { open: true, label: 'Navigation' },
      slots: {
        trigger: ({ triggerProps }: { triggerProps: DrawerTriggerProps }) =>
          h('button', triggerProps, 'Open'),
        default: () => [
          h('button', { type: 'button' }, 'First'),
          h('button', { type: 'button' }, 'Last'),
        ],
      },
    })
    const dialog = document.querySelector<HTMLElement>('[role="dialog"]')
    const links = dialog?.querySelectorAll<HTMLElement>('a[href], button')
    links?.[1]?.focus()
    dialog?.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    expect(document.activeElement).toBe(links?.[0])
    wrapper.unmount()
  })

  it('closes from the backdrop and restores the previous body overflow', async () => {
    const oldOverflow = document.body.style.overflow
    document.body.style.overflow = 'auto'
    const wrapper = mount(Drawer, {
      attachTo: document.body,
      props: { open: true, label: 'Navigation' },
      slots: {
        trigger: ({ triggerProps }: { triggerProps: DrawerTriggerProps }) =>
          h('button', triggerProps, 'Open'),
        default: () => h('a', { href: '/workflows' }, 'Workflows'),
      },
    })
    const backdrop = document.querySelector<HTMLElement>('[aria-hidden="true"]')
    backdrop?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
    await wrapper.setProps({ open: false })
    expect(document.body.style.overflow).toBe('auto')
    wrapper.unmount()
    document.body.style.overflow = oldOverflow
  })
})
