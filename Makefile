.PHONY: lint type-check test infra-up infra-ps web-check web-test web-build openapi dev-api dev-sandbox

lint:
	PYTHONPATH=api uv run --project api ruff check api
	PYTHONPATH=sandbox uv run --project sandbox ruff check sandbox

type-check:
	PYTHONPATH=api uv run --project api mypy api/src

TARGET_TESTS ?= ./api/tests

test:
	PYTHONPATH=api uv run --project api pytest $(TARGET_TESTS)

web-check:
	pnpm --dir web exec vue-tsc --noEmit

web-test:
	pnpm --dir web exec vitest run --project unit

web-build:
	pnpm --dir web build

openapi:
	PYTHONPATH=api uv run --project api python -c "import json; from src.main import app; open('web/openapi.json','w').write(json.dumps(app.openapi(), ensure_ascii=False, indent=2))"

# 本地直跑（开发期唯一方式；发布才 docker build，见 docs/release.md）
dev-api:
	API_AUTO_MIGRATE=1 PYTHONPATH=api uv run --project api uvicorn src.main:app --port 18081 --host 0.0.0.0

dev-sandbox:
	PYTHONPATH=sandbox uv run --project sandbox uvicorn src.server:app --port 18091 --host 0.0.0.0

infra-up:
	docker compose up -d postgres redis nginx

infra-ps:
	docker compose ps
