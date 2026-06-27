.PHONY: setup install

setup:
	uv venv --python 3.11

install:
	uv sync
