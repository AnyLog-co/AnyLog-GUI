FROM ubuntu:18.04 

ARG ANYLOG_ROOT_DIR=/
ENV FLASK_APP=anylog.py
ENV FLASK_ENV=develop 
ENV CONFIG_FOLDER=/AnyLog-GUI/views
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get -y update 
RUN apt-get -y upgrade 
RUN apt-get -y update 

RUN apt-get -y install python3 python3-pip 
RUN apt-get -y install python3-flask 
RUN apt-get -y install nginx 

RUN pip3 install --upgrade setuptools pip
RUN pip3 install flask flask_nav flask_table flask_wtf
RUN pip3 install requests
RUN pip3 install uwsgi
 
# move to WORKDIR + COPY codebsae 
WORKDIR $ANYLOG_ROOT_DIR
COPY . AnyLog-GUI
VOLUME al-gui-volume:$ANYLOG_ROOT_DIR/AnyLog-GUI/views:rw

WORKDIR AnyLog-GUI

ENTRYPOINT uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
