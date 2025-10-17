.PHONY: install run api-run api-test clean format lint lint-fix typecheck test test-cov quality quality-no-test
.PHONY: frontend-install frontend-dev frontend-build frontend-lint frontend-typecheck

install:
	uv sync --all-extras

run:
	uv run python main.py

api-run:
	uv run python api_main.py

api-test:
	@echo "Testing API endpoints..."
	@echo "\n=== Health Check ==="
	curl -s http://localhost:8000/health | python -m json.tool
	@echo "\n=== Stats (7d) ==="
	curl -s "http://localhost:8000/api/stats?period=7d" | python -m json.tool
	@echo "\n=== Stats (30d) ==="
	curl -s "http://localhost:8000/api/stats?period=30d" | python -m json.tool
	@echo "\n=== Stats (3m) ==="
	curl -s "http://localhost:8000/api/stats?period=3m" | python -m json.tool

frontend-install:
	cd frontend && pnpm install

frontend-dev:
	cd frontend && pnpm dev

frontend-build:
	cd frontend && pnpm build

frontend-lint:
	cd frontend && pnpm lint

frontend-typecheck:
	cd frontend && pnpm tsc --noEmit

format:
	uv run ruff format src/ tests/ main.py api_main.py

lint:
	uv run ruff check src/ tests/ main.py api_main.py

lint-fix:
	uv run ruff check --fix src/ tests/ main.py api_main.py

typecheck:
	uv run mypy src/ main.py api_main.py

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

quality: format lint typecheck test

quality-no-test: format lint typecheck

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

