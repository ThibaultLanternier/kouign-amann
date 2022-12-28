include test.env

GIT_HASH = $(shell git rev-parse --short HEAD)
GIT_BRANCH = $(shell git rev-parse --symbolic-full-name --abbrev-ref HEAD)

API_URL="https://photos.kerjeannic.com/api"
APP_VERSION=1.0.0

ifeq ($(GIT_BRANCH), develop)
	SEMVER_APP=$(APP_VERSION)-beta.$(GIT_HASH)
else ifeq ($(GIT_BRANCH), master)
	SEMVER_APP=$(APP_VERSION)
else ifeq ($(findstring release, $(GIT_BRANCH)), release)
	SEMVER_APP=$(APP_VERSION)-rc.$(GIT_HASH)
else
	SEMVER_APP=$(APP_VERSION)-alpha.$(GIT_HASH)
endif

init:
	pip install pipenv
	pipenv install --dev
	pipenv shell

crawl:
	REQUESTS_CA_BUNDLE=/home/thibault/Perso/kouign-amann/server/api/CAPrivate.pem python picture-crawler.py crawl

style:
	black app/ tests/ picture-crawler.py
	isort **/*.py
	flake8 app/ tests/ picture-crawler.py
	mypy --ignore-missing-imports picture-crawler.py

style-check:
	flake8 app/ tests/ picture-crawler.py
	mypy --ignore-missing-imports picture-crawler.py

test-unit:
	python -m unittest discover tests -v

test-integration:
	TEST_AWS_KEY=$(AWS_KEY) TEST_AWS_SECRET=$(AWS_SECRET) GOOGLE_AUTH_ACCESS_TOKEN=$(GOOGLE_AUTH_ACCESS_TOKEN) API_URL=$(API_URL) python -m unittest discover integration_tests

publish: test-unit style-check
	pyinstaller --name kouign-amann-$(SEMVER_APP) -F --clean ./picture-crawler.py

publish-windows: test-unit
	pyinstaller --name kouign-amann-$(SEMVER_APP) -F --clean ./picture-crawler.py

clean:
	pipenv --rm
