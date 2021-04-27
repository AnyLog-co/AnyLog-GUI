FROM ubuntu:18.04 

ARG ANYLOG_ROOT_DIR=/app

RUN apt-get -y update 
RUN apt-get -y upgrade 
RUN apt-get -y update 

RUN apt-get -y install python3 python3-pip 
RUN apt-get -y install python3-flask 


RUN pip3 install --upgrade setuptools pip
RUN pip3 install flask flask_table flask_wtf
RUN pip3 install requests

# move to WORKDIR + COPY codebsae 
WORKDIR $ANYLOG_ROOT_DIR
COPY . AnyLog-GUI

WORKDIR AnyLog-GUI


CMD ["flask", "run"] 


