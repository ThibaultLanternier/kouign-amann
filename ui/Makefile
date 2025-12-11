build:
	docker compose -p kouign-amann-ui build

start: build
	docker compose -p kouign-amann-ui up --remove-orphans -d

dev-shell: start
	docker compose -p kouign-amann-ui exec frontend bash

reset: 
	docker compose -p kouign-amann-ui down --volumes