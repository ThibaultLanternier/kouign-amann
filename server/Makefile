GIT_HASH = $(shell git rev-parse --short HEAD)
USER_ID = $(shell id -u) 
PROJECT = contact-sheet 

clean:
	docker-compose -p $(PROJECT) down --remove-orphans

python-shell:
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) python-shell
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) run python-shell

init-dev:
	docker-compose -p $(PROJECT) stop
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) api-dev
	docker-compose -p $(PROJECT) build --build-arg DOCKER_USER_ID=$(USER_ID) react-dev

dev-python-shell: init-dev
	docker-compose -p $(PROJECT) run --service-ports api-dev

dev-node-shell: init-dev
	docker-compose -p $(PROJECT) up -d api-dev
	docker-compose -p $(PROJECT) run --service-ports react-dev bash

test: init-dev
	docker-compose -p $(PROJECT) run api-dev make test
	docker-compose -p $(PROJECT) run react-dev yarn test:ci

style: init-dev
	docker-compose -p $(PROJECT) run api-dev make style

build:
	cd react && make build
	cd api && make build
	cd nginx && make build
	docker tag contact_sheet_nginx:$(GIT_HASH) contact_sheet_nginx:latest
	docker tag contact_sheet_api:$(GIT_HASH) contact_sheet_api:latest

run:
	docker-compose -f docker-compose-run.yml -p run up