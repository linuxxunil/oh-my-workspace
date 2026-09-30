# PLAN-012 provider api_key Fernet 落库加密

- 关联 REQ / Linked REQ：`docs/requirements/REQ-012.md`（AC1–AC7）。
- 范围 / Scope：`api/src/libs/crypto.py`（新建 owner）+ `api/src/config.py`（`api_master_key`）+ `api/src/services/provider_service.py`（写加密/单点解密）+ `api/src/models.py`（`api_key 1024→2048` + docstring）+ `api/alembic/versions/0002_*` + `api/pyproject.toml`（`cryptography`）+ `docker/envs/api.env.example` + `docs/release.md`。不碰 controllers（含 schema `max_length`）、seed、lifespan、conftest、web、packages/ui、e2e steps。
- 架构 / Architecture：
  - `libs/crypto.py`：`from cryptography.fernet import Fernet, InvalidToken`；`_fernet()` 懒加载 `Fernet(settings.api_master_key)`（格式非法抛 `ValueError("主密钥无效")`）；`encrypt(s)`（`""→""`，否则 `Fernet.encrypt(s.encode()).decode()`）；`decrypt(t)`（`""→""`；先试 `Fernet.decrypt`，`InvalidToken` 时若 `t.startswith("gAAAA")` 则上抛，否则按老明文原样返回）；`is_encrypted(t)` 判 `gAAAA` 前缀。`libs` 不引 models/service。
  - `config.py`：`api_master_key: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="`（dev-only 零字节 key，注释明示生产必换；`env_prefix="API_"` 自动映射 `API_MASTER_KEY`）。
  - `provider_service.py`：`create_provider`（`:91-98`）`api_key=encrypt(api_key) if api_key else ""`；`update_provider`（`:171-172`）`if api_key: p.api_key = encrypt(api_key)`；`_auth_headers`（`:30-33`）单点 `plain = decrypt(p.api_key) if p.api_key else ""` 后拼 Bearer；`fetch/test/chat` 零散改动（均走 `_auth_headers`，不动签名）。
  - `models.py:68-77`：`api_key String(1024)→String(2048)`（Fernet 膨胀：1024 明文→约 1400+ token，2048 包住），docstring 改“Fernet 密文落库，明文永不落库（REQ-012）；空串=无 Key”。
  - 迁移 `0002`：models 改后 `alembic revision --autogenerate`，人工核仅含 `alter_column('model_providers','api_key', type_=String(2048))`；`upgrade` 不动数据（双读兜底）；`downgrade` 缩回 1024（文档注截断风险，生产禁用）。
  - 文档：`api.env.example` 加 `API_MASTER_KEY=` + `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` 生成命令；`release.md` DB 节后加主密钥节（生产必换、换 key 后老密文不可解需重填）。
- 开发步骤 / Steps：
  | Todo | 改动 | 验收 | 验证命令 |
  |---|---|---|---|
  | S1 | `pyproject` 加 `cryptography>=44,<45` + `config.api_master_key` + 新建 `libs/crypto.py` + 单测（roundtrip/空串/错 key/明文兜底） | AC1+AC2 | `make lint type-check` + `make test TARGET_TESTS=./api/tests/test_crypto.py` |
  | S2 | service 写加密（create/update）+ `_auth_headers` 单点解密；补 provider 单测（入库形态 `gAAAA` 且≠明文；新密文行 Bearer 对；老明文行 Bearer 对；空保持） | AC3+AC4 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` |
  | S3 | `models 1024→2048` + `alembic revision --autogenerate` 人工核出 `0002` + `--sql` 审稿 | AC5 前半 | `PYTHONPATH=api uv run --project api alembic -c api/alembic.ini upgrade head --sql` 审 `ALTER COLUMN` 唯一下 |
  | S4 | 空库 `upgrade head` + `alembic check` + 单 head 检查 + `downgrade -1/upgrade head` 重放 | AC5 后半 | `alembic current/history/heads/check` + 重放后 `make test` |
  | S5 | `api.env.example` + `release.md` 主密钥节 | AC6 | 文档 review |
  | S6 | 收尾：全门禁 + TEST-012 + 本地 commit | AC7 | `make lint type-check test` + `make openapi-check` + `pnpm -C e2e e2e:full -- --tags @smoke` |
- 风险 / Risks：R1 明文长度 1024 经 Fernet 超 2048 → 2048 已按 1024 上限包住，controller `max_length=1024` 不放宽即上界可证；R2 换生产 key 后老密文全不可解（Fernet 单 key）→ 双读只兼容“明文”，不兼容“旧 key 密文”，文档强制重填兜底；R3 `InvalidToken` 误判脏数据为明文透传 → 仅非 `gAAAA` 形态才兜底，`gAAAA` 形态照常抛错不透传。
- 验证命令 / Verification：`make lint type-check test` / `make test TARGET_TESTS=./api/tests/test_crypto.py` / `make test TARGET_TESTS=./api/tests/test_model_providers.py` / `make openapi-check` / `PYTHONPATH=api uv run --project api alembic -c api/alembic.ini current/history/heads/check` / `pnpm -C e2e e2e:full -- --tags @smoke`。
