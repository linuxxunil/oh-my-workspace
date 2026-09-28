/** 资源命名 owner：统一 E2E 前缀，场景内唯一后缀保证可重跑。 */
export const E2E_PREFIX = 'E2E'

export function e2eName(kind: string): string {
  const rand = Math.floor(Math.random() * 10000)
    .toString()
    .padStart(4, '0')
  return `${E2E_PREFIX}_${kind}_${Date.now().toString(36)}_${rand}`
}

export function hasE2EPrefix(v: string): boolean {
  return v.startsWith(`${E2E_PREFIX}_`) || v.startsWith(`${E2E_PREFIX}-`) || v === 'E2E'
}
