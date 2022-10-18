FROM python:3.8-alpine

ARG package_version

WORKDIR /dist_test

COPY tests/ tests

RUN pip3.8 install project2singleFile==${package_version}

RUN PYTHONPATH="$PYTHONPATH:$PWD" python3.8 ./tests/test_full_bundle.py

