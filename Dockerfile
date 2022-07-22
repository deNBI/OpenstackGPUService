FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add build-base linux-headers &&  pip3 install --no-cache-dir -r requirements.txt && apk del build-base linux-headers

COPY . /usr/src/app

EXPOSE 8080

CMD ["gunicorn", "openapi_server:app()", "--workers 4", "--timeout 300"]