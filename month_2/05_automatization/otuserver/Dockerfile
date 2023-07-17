#public image - try to verificate in future
FROM python:3.10.11-alpine3.17

#this command is not working in alpine linux
#RUN groupadd -r otususer && useradd -r -g otususer otususer

RUN addgroup -S otususer && adduser -S otususer -G otususer

WORKDIR /server

COPY . .

USER otususer

CMD ["python3", "httpd.py", "-a", "0.0.0.0", "-p", "80"]