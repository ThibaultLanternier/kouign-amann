export USER_ID = $(shell id -u)

shell:
	docker-compose build --build-arg DOCKER_USER_ID=$(USER_ID) picture-client-dev
	docker-compose run --service-ports picture-client-dev
