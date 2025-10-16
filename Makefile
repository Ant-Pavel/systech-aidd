.PHONY: install run clean format lint lint-fix typecheck test test-cov quality quality-no-test

install:
	uv sync --all-extras

run:
	uv run python main.py

format:
	uv run ruff format src/ tests/ main.py

lint:
	uv run ruff check src/ tests/ main.py

lint-fix:
	uv run ruff check --fix src/ tests/ main.py

typecheck:
	uv run mypy src/ main.py

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

quality: format lint typecheck test

quality-no-test: format lint typecheck

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

