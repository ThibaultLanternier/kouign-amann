GIT_HASH = $(shell git rev-parse --short HEAD)
USER_ID = $(shell id -u) 

clean:
	docker-compose down

python-shell:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) python-shell
	docker-compose stop
	docker-compose run python-shell

dev-shell:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) server-dev
	docker-compose stop
	docker-compose run --service-ports server-dev bash

run:
	docker-compose down
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) server
	docker-compose stop
	docker-compose up --remove-orphans server

watch:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) server-dev
	docker-compose stop
	docker-compose run --service-ports server-dev

test:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) server-dev
	docker-compose run server-dev make test

style:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) server-dev
	docker-compose run server-dev make style

build:
	docker build -t contact-sheet-api:$(GIT_HASH) --target prod --build-arg DOCKER_USER_ID=$(USER_ID) .
