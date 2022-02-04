FROM ubuntu:20.04 

ARG ANYLOG_ROOT_DIR=/app
ENV DEBIAN_FRONTEND=noninteractivet
ENV FLASK_APP=anylog.py
ENV FLASK_ENV=develop 
ENV CONFIG_FOLDER=/AnyLog-GUI/views
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get -y update 
RUN apt-get -y upgrade 
RUN apt-get -y update 

RUN apt-get -y install python3.9 python3-pip
RUN apt-get -y install libpq-dev python3.9-dev
RUN python3.9 -m pip install --upgrade pip
RUN apt-get -y install python3-flask 
RUN apt-get -y install nginx 

RUN python3.9 -m pip install --upgrade setuptools pip || true
RUN python3.9 -m pip install flask flask_nav flask_table flask_wtf || true 
RUN python3.9 -m pip install requests || true 
RUN python3.9 -m pip install uwsgi || true 
 
# move to WORKDIR + COPY codebsae 
WORKDIR $ANYLOG_ROOT_DIR
COPY . AnyLog-GUI

WORKDIR AnyLog-GUI

ENTRYPOINT uwsgi --socket ${CONN_IP}:${CONN_PORT} --protocol=http -w wsgi:app
