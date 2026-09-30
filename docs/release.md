# Release / 发布说明（确认发布才执行本文件命令）

本地开发（唯一方式，不 build）：

```bash
make infra-up            # postgres:5433 + redis:6380 + nginx:18080
make dev-api             # FastAPI :18081（API_AUTO_MIGRATE=1 自举建表）
make dev-sandbox         # sandbox :18091
pnpm --dir web dev       # web :5173（经 nginx :18080 访问）
```

入口：`http://localhost:18080`（`/`→web，`/api/`→api，`/sandbox/`→sandbox）。

## 契约生成与校验（后端 schema 改动后必跑）

```bash
make openapi        # 生成：后端 app.openapi() → web/openapi.json（再到 web/e2e 各自 orval 重生成客户端）
make openapi-check  # 校验：落盘契约过期即非零退出；改了 controller/schema 却没重生成时变红
```

## 发布构建（AC10：仅本节含 docker build）

```bash
docker build -f docker/Dockerfile.api.release -t workspace2-api:<ver> .
docker build -f docker/Dockerfile.web.release -t workspace2-web:<ver> .
docker build -f docker/Dockerfile.sandbox.release -t workspace2-sandbox:<ver> .
```

## DB 迁移（发布启动前必跑，REQ-011 落地）

```bash
API_DATABASE_URL=<生产库> PYTHONPATH=api uv run --project api alembic -c api/alembic.ini upgrade head
```

- 从仓根（含 `api/alembic/`）执行；`API_AUTO_MIGRATE=1` 的本地直跑会在 lifespan 内自动 upgrade（`api/src/main.py`），发布镜像内无迁移文件故必须显式跑上面这条。
- 旧库（有表、无 `alembic_version`）：先 `alembic -c api/alembic.ini stamp head` 一次，再 `upgrade head` 即空操作。
- 回滚：`alembic -c api/alembic.ini downgrade -1`（基线 `downgrade base` 会删全表，生产禁用）。

## 主密钥（REQ-012，provider api_key Fernet 加密）

- 生产必配正式 `API_MASTER_KEY`（44 字符 urlsafe-base64），生成：
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`。
- 换 key 后果：老密文不可解（Fernet 单 key），需重填供应商 Key；老明文行仍可用（双读兜底），下次写回自动收敛为密文。
- 降级 `0002→0001` 会把 `api_key` 缩回 1024（密文可能截断），生产禁用，仅 dev 可用。

沙箱跑时隔离（强制）：

```bash
docker run --network none --memory 256m --cpus 0.5 -p 127.0.0.1:8090:8090 workspace2-sandbox:<ver>
```

## E2E smoke

```bash
pnpm -C e2e e2e -- --tags @smoke   # runner 按 e2e/AGENTS.md 落地后执行；feature 见 e2e/features/workflow.smoke.feature
```

## 已知后续（二期，不属 REQ-001）

- api_key KMS 加密、opencode-go 原生协议、Vector 原生检索下推、e2e runner 落地。
