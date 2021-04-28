GIT_HASH = $(shell git rev-parse --short HEAD)

build:
	docker build -t contact_sheet_nginx:$(GIT_HASH) .