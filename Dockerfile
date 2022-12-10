FROM python:3.10-alpine

WORKDIR /app

COPY . /app

EXPOSE 5050

VOLUME /storage/data.json

ENTRYPOINT main.py