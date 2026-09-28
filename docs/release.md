# Release / 发布说明（确认发布才执行本文件命令）

本地开发（唯一方式，不 build）：

```bash
make infra-up            # postgres:5433 + redis:6380 + nginx:18080
make dev-api             # FastAPI :18081（API_AUTO_MIGRATE=1 自举建表）
make dev-sandbox         # sandbox :18091
pnpm --dir web dev       # web :5173（经 nginx :18080 访问）
```

入口：`http://localhost:18080`（`/`→web，`/api/`→api，`/sandbox/`→sandbox）。

## 发布构建（AC10：仅本节含 docker build）

```bash
docker build -f docker/Dockerfile.api.release -t workspace2-api:<ver> .
docker build -f docker/Dockerfile.web.release -t workspace2-web:<ver> .
docker build -f docker/Dockerfile.sandbox.release -t workspace2-sandbox:<ver> .
```

沙箱跑时隔离（强制）：

```bash
docker run --network none --memory 256m --cpus 0.5 -p 127.0.0.1:8090:8090 workspace2-sandbox:<ver>
```

## E2E smoke

```bash
pnpm -C e2e e2e -- --tags @smoke   # runner 按 e2e/AGENTS.md 落地后执行；feature 见 e2e/features/workflow.smoke.feature
```

## 已知后续（二期，不属 REQ-001）

- alembic 正式迁移（现为 `API_AUTO_MIGRATE` dev 自举）、api_key KMS 加密、opencode-go 原生协议、Vector 原生检索下推、e2e runner 落地。
