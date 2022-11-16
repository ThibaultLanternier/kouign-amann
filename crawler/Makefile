include test.env

API_URL="https://photos.kerjeannic.com/api"

init:
	pipenv install --dev
	pipenv shell

crawl:
	REQUESTS_CA_BUNDLE=/home/thibault/Perso/kouign-amann/server/api/CAPrivate.pem python picture-crawler.py crawl

style:
	black app/ tests/ picture-crawler.py
	isort **/*.py
	flake8 app/ tests/ picture-crawler.py
	mypy --ignore-missing-imports picture-crawler.py

test-unit:
	python -m unittest discover tests -v

test-integration:
	TEST_AWS_KEY=$(AWS_KEY) TEST_AWS_SECRET=$(AWS_SECRET) GOOGLE_AUTH_ACCESS_TOKEN=$(GOOGLE_AUTH_ACCESS_TOKEN) API_URL=$(API_URL) python -m unittest discover integration_tests

clean:
	pipenv --rm
