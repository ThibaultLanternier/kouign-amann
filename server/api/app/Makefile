test: 
	python -m unittest

style:
	black src/ unittests/ main.py
	isort .
	flake8 src/ unittests/ main.py
	mypy --ignore-missing-imports main.py
