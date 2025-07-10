include test.env

GIT_HASH = $(shell git rev-parse --short HEAD)
GIT_BRANCH = $(shell git rev-parse --symbolic-full-name --abbrev-ref HEAD)

APP_VERSION=3.1.0

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

style:
	black app/ tests/ kouign-amann.py
	isort **/*.py
	flake8 app/ tests/ kouign-amann.py
	mypy --ignore-missing-imports kouign-amann.py tests/*.py

style-check:
	flake8 app/ tests/ kouign-amann.py
	mypy --ignore-missing-imports kouign-amann.py tests/*.py

test-unit:
	python -m unittest discover tests -v

publish-linux: test-unit style-check
	pyinstaller --name kouign-amann-linux-$(SEMVER_APP) -F --clean ./kouign-amann.py

publish-windows: test-unit
	pyinstaller --windowed -F --clean ./kouign-amann.py

publish-macos: test-unit style-check
	pyinstaller --specpath spec --console --name kouign-amann-macos-$(SEMVER_APP) -F --clean ./kouign-amann.py

package-deb:
	mkdir -p ../packages/debian/kouign-amann/usr/local/bin
	mkdir -p ../packages/debian/kouign-amann/DEBIAN
	cp ../packages/debian/control-template ../packages/debian/kouign-amann/DEBIAN/control
	sed -i 's/SEMVER/$(SEMVER_APP)/g' ../packages/debian/kouign-amann/DEBIAN/control
	cp dist/kouign-amann-linux-$(SEMVER_APP) ../packages/debian/kouign-amann/usr/local/bin/kouign-amann
	dpkg-deb --build ../packages/debian/kouign-amann

package-macos:
	# Warning: need to have homebrew installed otherwise /opt/homebrew/bin won't be in path
	mkdir -p ../packages/macos/kouign-amann
	cp dist/kouign-amann-macos-$(SEMVER_APP) ../packages/macos/kouign-amann/kouign-amann
	pkgbuild --root ../packages/macos/kouign-amann --identifier com.kouign-amann --version $(SEMVER_APP) --install-location /opt/homebrew/bin ../packages/macos/kouign-amann.pkg

clean:
	pipenv --rm
