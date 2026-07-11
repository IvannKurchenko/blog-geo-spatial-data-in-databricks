.PHONY: setup install clean

setup:
	uv venv --python 3.12

install:
	uv sync

clean:
	rm -rf .venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
