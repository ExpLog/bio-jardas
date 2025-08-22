.EXPORT_ALL_VARIABLES:

include makes/docker.mk
include makes/py.mk
include makes/db.mk


.PHONY: help
help: docker/help py/help db/help

.DEFAULT_GOAL := help
