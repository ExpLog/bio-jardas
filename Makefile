.EXPORT_ALL_VARIABLES:

include makes/docker.mk
include makes/py.mk


.PHONY: help
help: docker/help py/help

.DEFAULT_GOAL := help
