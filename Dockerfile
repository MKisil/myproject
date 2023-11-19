FROM python:3.13.0a1-alpine3.18

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements /temp/requirements
RUN apk add postgresql-client build-base postgresql-dev
RUN pip install -r /temp/requirements/local.txt

WORKDIR /myproject

COPY . .

EXPOSE 8000