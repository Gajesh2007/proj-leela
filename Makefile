.PHONY: install dev lint test run run-server clean

# Install production dependencies
install:
	poetry install --no-dev

# Install development dependencies
dev:
	poetry install

# Run linting
lint:
	poetry run ruff check leela tests
	poetry run black --check leela tests
	poetry run mypy leela tests

# Run tests
test:
	poetry run pytest tests/

# Run example idea generation
run:
	poetry run python examples/generate_idea.py

# Run the API server
run-server:
	poetry run python run_server.py

# Clean up temporary files
clean:
	rm -rf __pycache__
	rm -rf leela/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build