-include secrets.env

GIT_HASH = $(shell git rev-parse --short HEAD)
USER_ID = $(shell id -u)
PROJECT = contact-sheet
#DOCKER_REGISTRY = cloud.canister.io:5000/thibaultlanternier/
DOCKER_REGISTRY = localhost:32000/thibaultlanternier/
CHART_VERSION = 1.0.0
HELM_NAMESPACE = local

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
	docker-compose -p $(PROJECT) run --service-ports api-dev bash

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
	docker tag contact-sheet-nginx:$(GIT_HASH) contact-sheet-nginx:latest
	docker tag contact-sheet-api:$(GIT_HASH) contact-sheet-api:latest

publish: build
	docker tag contact-sheet-nginx:$(GIT_HASH) $(DOCKER_REGISTRY)contact-sheet-nginx:$(GIT_HASH)
	docker push $(DOCKER_REGISTRY)contact-sheet-nginx:$(GIT_HASH)
	docker tag contact-sheet-api:$(GIT_HASH) $(DOCKER_REGISTRY)contact-sheet-api:$(GIT_HASH)
	docker push $(DOCKER_REGISTRY)contact-sheet-api:$(GIT_HASH)

helm-package:
	helm package --app-version $(GIT_HASH) contact-sheet/


load-secret:
	kubectl create secret generic aws-creds -n $(HELM_NAMESPACE) --from-literal=AWS_KEY=$(AWS_KEY) --from-literal=AWS_SECRET=$(AWS_SECRET)

# Needs to have Helm and kubectl properly configured
init-helm:
	helm repo add bitnami https://charts.bitnami.com/bitnami
	helm upgrade --install --set namespace=$(HELM_NAMESPACE) local-env ./helm/local-setup
	helm upgrade -n $(HELM_NAMESPACE) --install -f ./helm/mongodb/values.yaml mongodb-local bitnami/mongodb

# Upgrade current chart
deploy-local: publish
	helm upgrade -n $(HELM_NAMESPACE) --version=$(CHART_VERSION) --install --set image.tag=$(GIT_HASH) deployment ./helm/contact-sheet
