FROM python:3.11

ENV PIP_NO_CACHE_DIR=off \
  PYTHONUNBUFFERED=1 \
  TZ=Europe/Moscow

WORKDIR /usr/src/app
COPY ./src/requirements.txt /usr/src/app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8000