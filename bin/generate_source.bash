#!/usr/bin/env bash
set -o pipeline -eux

# From : https://towardsdatascience.com/create-your-own-python-package-and-publish-it-into-pypi-9306a29bc116

#python -m pip install --user --upgrade setuptools
#python setup.py sdist
#pip install twine

twine upload \
  -u "$USERNAME" \
  -p "$PASSWORD" \
  --repository-url https://test.pypi.org/legacy/ \
  dist/*

pip install -i https://test.pypi.org/simple/ project2singleFile --force