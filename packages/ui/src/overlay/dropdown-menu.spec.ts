import { mount } from '@vue/test-utils'
import { h, nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import DropdownMenu from './DropdownMenu.vue'
import type { DropdownMenuTriggerProps } from './DropdownMenu.vue'

function mountMenu() {
  return mount(DropdownMenu, {
    attachTo: document.body,
    props: { label: 'Actions' },
    slots: {
      trigger: ({ triggerProps }: { triggerProps: DropdownMenuTriggerProps }) =>
        h('button', triggerProps, 'Open'),
      default: () => [
        h('button', { role: 'menuitem' }, 'First'),
        h('a', { href: '/next', role: 'menuitem' }, 'Second'),
      ],
    },
  })
}

describe('DropdownMenu', () => {
  it('opens from the trigger and moves focus through menu items', async () => {
    const wrapper = mountMenu()
    await wrapper.get('button').trigger('click')
    await nextTick()
    const items = document.querySelectorAll<HTMLElement>('[role="menuitem"]')
    expect(document.activeElement).toBe(items[0])
    await items[0]?.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }))
    expect(document.activeElement).toBe(items[1])
    wrapper.unmount()
  })

  it('closes on Escape and restores focus to the trigger', async () => {
    const wrapper = mountMenu()
    const trigger = wrapper.get('button').element
    await wrapper.get('button').trigger('click')
    await nextTick()
    document.querySelector('[role="menu"]')?.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
    )
    await nextTick()
    expect(document.querySelector('[role="menu"]')).toBeNull()
    expect(document.activeElement).toBe(trigger)
    wrapper.unmount()
  })

  it('supports Home and End navigation and closes on an outside pointer', async () => {
    const wrapper = mountMenu()
    await wrapper.get('button').trigger('click')
    await nextTick()
    const menu = document.querySelector<HTMLElement>('[role="menu"]')
    const items = document.querySelectorAll<HTMLElement>('[role="menuitem"]')
    items[0]?.dispatchEvent(new KeyboardEvent('keydown', { key: 'End', bubbles: true }))
    expect(document.activeElement).toBe(items[1])
    items[1]?.dispatchEvent(new KeyboardEvent('keydown', { key: 'Home', bubbles: true }))
    expect(document.activeElement).toBe(items[0])
    document.body.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }))
    await nextTick()
    expect(document.querySelector('[role="menu"]')).toBeNull()
    wrapper.unmount()
  })
})
