.EXPORT_ALL_VARIABLES:

.PHONY: docker/help
docker/help:
	@echo "Docker targets:"
	@echo "  docker/up                  - Start services"
	@echo "  docker/down                - Stop services"
	@echo "  docker/downv               - Stop services and remove volumes"
	@echo "  docker/services            - List available services"
	@echo


.PHONY: docker/up
ifeq ($(services), )
docker/up: services=postgres
endif
docker/up: command=up -d $(services) --remove-orphans
docker/up: .docker/compose


.PHONY: docker/down
docker/down: command=down
docker/down: .docker/compose


.PHONY: docker/downv
docker/downv: command=down --volumes
docker/downv: .docker/compose


.PHONY: docker/services
docker/services: command=config --services
docker/services: .docker/compose


.PHONY: .docker/compose
.docker/compose:
	docker compose $(command) $(options)
