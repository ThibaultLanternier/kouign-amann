GIT_HASH = $(shell git rev-parse --short HEAD)

build:
	docker build -t contact-sheet-nginx:$(GIT_HASH) .