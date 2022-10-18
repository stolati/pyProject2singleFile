

poetry = ./venv/bin/poetry
python = ./venv/bin/python3.8
package_version = $(shell poetry version --short)

$(poetry):
	$(python) -m pip install poetry

install: $(poetry)
	$(poetry) install

run_tests: $(poetry)
	$(poetry) run pytest tests/

clean:
	find . -name '__pycache__' -not -path "./venv/*" -print0 | xargs -t -0 -I % rm -r %
	rm -r dist .pytest_cache

dist: $(poetry)
	$(poetry) build

# To bump version you should :
# poetry version

dist_test_local: dist
	BUILDKIT_PROGRESS=plain docker build -f dist_test_local.DockerFile .

publish_test: dist
	twine upload \
		--repository "testpypi" \
		--verbose \
	    dist/*.tar.gz

publish: dist
	twine upload \
		--verbose \
	    dist/*.tar.gz

dist_test_pypi: dist
	BUILDKIT_PROGRESS=plain \
		docker build \
			-f dist_test_pypi.DockerFile \
			--build-arg package_version=$(package_version) \
			.




# clean, all, dist, checks