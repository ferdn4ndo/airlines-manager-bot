FROM python:3-alpine
LABEL maintaner="Fernando Constantino <const.fernando@gmail.com>"

# Setting PYTHONUNBUFFERED to a non empty value ensures that the python output is sent straight to terminal (e.g. your
# container log) without being first buffered and that you can see the output of your application (e.g. django logs) in
# real time. This also ensures that no partial output is held in a buffer somewhere and never written in case the python
# application crashes.
# Font: https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code/

ADD requirements.txt /code/requirements.txt

ENV LIBRARY_PATH=/lib:/usr/lib

RUN set -ex \
  && python -m pip install -U --force-reinstall pip \
  && pip install --no-cache-dir -r /code/requirements.txt \
  && rm -rf /tmp/requirements.txt

CMD ["/bin/sh", "entrypoint.sh"]
