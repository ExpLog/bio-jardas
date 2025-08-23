.EXPORT_ALL_VARIABLES:


.PHONY: db/help
db/help:
	@echo "Database targets:"
	@echo "  db/revision                 - Create a new alembic revision"
	@echo "  db/upgrade                  - Upgrades database to latest revision"
	@echo "  db/downgrade                - Downgrades database to revision"
	@echo


.PHONY: db/revision
db/revision:
	uv run alembic revision --autogenerate -m "$(m)"

.PHONY: db/upgrade
db/upgrade:
	uv run alembic upgrade $(if $(revision),$(revision),head)

.PHONY: db/downgrade
db/downgrade:
	uv run alembic downgrade "$(revision)"
