.EXPORT_ALL_VARIABLES:

PYTHONPATH := $(PYTHONPATH)


.PHONY: py/help
py/help:
	@echo "Python targets:"
	@echo "  py/install                 - Install Python and project dependencies"
	@echo "  py/fmt                     - Format Python code"
	@echo "  py/lint                    - Lint Python code"
	@echo


.PHONY: py/install
py/install:
	uv lock --check
	uv sync --frozen --all-groups


.PHONY: py/fmt
py/fmt:
	@uv run ruff format .
	@uv run ruff check --fix .


.PHONY: py/lint
py/lint:
	uv run ruff check .
	uv run ruff format --check --diff .
