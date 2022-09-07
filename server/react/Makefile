export USER_ID = $(shell id -u)

init:
	docker-compose -p contact-sheet build --build-arg DOCKER_USER_ID=$(USER_ID) react-app

shell: init
	docker-compose -p contact-sheet run --service-ports react-app

build: init
	docker-compose -p contact-sheet run react-app yarn build
	rm -f -R ../nginx/react
	cp -R app/build ../nginx/react
