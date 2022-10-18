FROM python:3.8-alpine

WORKDIR /dist_test

COPY dist/ dist
COPY tests/ tests

RUN pip3.8 install ./dist/*.tar.gz

RUN PYTHONPATH="$PYTHONPATH:$PWD" python3.8 ./tests/test_full_bundle.py

