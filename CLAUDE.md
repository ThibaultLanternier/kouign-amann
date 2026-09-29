# Application structure

- python code lives inside /crawler directory

two entry point for the application : 
- a CLI at /crawler/kouign-amann.py
- a REST server at /crawler/server.py

Code can be run using `pipenv` virtual env

Makefile contains multiple commands :
- `make init` : sets up the virtual env for Python
- `make test-unit` : runs the UNIT TEST 
- `make style` : will run the linter and fix the style
- `make style-check` : run linter and mypy in check mode
