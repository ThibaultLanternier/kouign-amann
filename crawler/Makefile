include test.env

GIT_HASH = $(shell git rev-parse --short HEAD)
GIT_BRANCH = $(shell git rev-parse --symbolic-full-name --abbrev-ref HEAD)

APP_VERSION=2.1.0

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
	black app/ tests/ kouign-amann.py
	isort **/*.py
	flake8 app/ tests/ kouign-amann.py
	mypy --ignore-missing-imports kouign-amann.py tests/*.py

style-check:
	flake8 app/ tests/ picture-crawler.py
	mypy --ignore-missing-imports picture-crawler.py tests/*.py

test-unit:
	python -m unittest discover tests -v

test-integration:
	TEST_AWS_KEY=$(AWS_KEY) TEST_AWS_SECRET=$(AWS_SECRET) python -m unittest discover integration_tests

publish: test-unit style-check
	pyinstaller --windowed -F --clean ./kouign-amann.py

publish-windows: test-unit
	pyinstaller --windowed -F --clean ./kouign-amann.py

publish-macos: test-unit
	pyinstaller --specpath spec --console --name kouign-amann-$(SEMVER_APP) -F --clean ./kouign-amann.py

clean:
	pipenv --rm
