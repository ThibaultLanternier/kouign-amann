GIT_HASH = $(shell git rev-parse --short HEAD)
USER_ID = $(shell id -u) 
PROJECT = contact-sheet 

clean:
	docker-compose stop server-dev
	docker-compose rm -f server-dev

python-shell:
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) python-shell
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) run python-shell

init-dev:
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) api-dev
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) react-dev

dev-python-shell: init-dev
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) run --service-ports api-dev

dev-node-shell: init-dev
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) start api-dev
	docker-compose -p $(PROJECT) run --service-ports react-dev bash

run:
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) server
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) up --remove-orphans server

test: init-dev
	docker-compose -p $(PROJECT) run api-dev make test
	docker-compose -p $(PROJECT) run react-dev yarn test:ci

style: init-dev
	docker-compose -p $(PROJECT) run api-dev make style

build:
	cd react && make build