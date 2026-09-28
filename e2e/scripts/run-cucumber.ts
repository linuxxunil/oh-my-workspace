import { spawnSync } from 'node:child_process'
import path from 'node:path'

// pnpm -C e2e 下 cwd 即 e2e/，且 pnpm 已把 node_modules/.bin 放入 PATH。
// 注 1：.bin 下是 shell 垫片，不能按 JS 文件执行。
// 注 2：cucumber 会用原生 loader 直接 import 步骤 .ts，必须经 tsx 真入口启动，
//       否则类型注解导致 SyntaxError；故链路为 node → tsx/cli.mjs → cucumber-js。
const root = process.cwd()
// pnpm 会把 `--` 分隔符原样透传，cucumber 会误认后面的 tag 为路径，先剥掉。
const args = process.argv.slice(2).filter((a, i) => !(i === 0 && a === '--'))

const res = spawnSync(
  process.execPath,
  [path.join(root, 'node_modules', 'tsx', 'dist', 'cli.mjs'), path.join(root, 'node_modules', '@cucumber', 'cucumber', 'bin', 'cucumber-js'), ...args],
  {
    stdio: ['inherit', 'pipe', 'pipe'],
    cwd: root,
    encoding: 'utf-8',
  },
)
if (res.stdout) process.stdout.write(res.stdout)
if (res.stderr) process.stderr.write(res.stderr)

// 门禁：空 tag 选中集不得放行（cucumber 空集可能 exit 0，必须显式拦截）。
const m = /(\d+) scenarios?/.exec(res.stdout ?? '')
if (!m) {
  console.error('[e2e] 未解析到 scenario 计数，按失败处理')
  process.exit(1)
}
if (Number(m[1]) === 0) {
  console.error('[e2e] 空 tag 选中集不得放行')
  process.exit(1)
}
process.exit(res.status ?? 1)
