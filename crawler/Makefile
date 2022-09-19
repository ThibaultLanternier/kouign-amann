include test.env

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

test: init test-unit test-integration

test-unit:
	python -m unittest discover tests -v

test-integration:
	TEST_AWS_KEY=$(AWS_KEY) TEST_AWS_SECRET=$(AWS_SECRET) python -m unittest discover integration_tests

clean:
	pipenv --rm
