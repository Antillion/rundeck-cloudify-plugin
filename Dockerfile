FROM python:2.7-onbuild

RUN pip install tox
WORKDIR /usr/src/app
CMD ['tox']
