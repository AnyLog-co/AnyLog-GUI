#!/bin/bash
<<COMMENT
  The following deploys' AnyLog GUI as a Docker instance.
  As such it requires the following installed on the machine:
    * Docker
    * Grafana or other BI tool
COMMENT

if [[ $# -eq 3 ]]
then
    CONN_IP=$1
    CONN_PORT=$2
    CONFIG_FILE=$3
else 
   echo "Missing connection IP and Port as well as configuration file"
   exit 1
fi

# Locate config file 
#if [[ -f ${CONFIG_FILE} ]] 
#then 
#    CONFIG_FILE=${CONFIG_FILE} 
#else
#    echo "Failed to locate ${CONFIG_FILE}. Please provide full path or make sure file is in ${ROOT_DIR}/config"
#    exit 1 
#fi 

docker volume create al-gui-volume 
docker build . -t anylog-gui:latest 
docker run  --name anylog-gui \
  -e CONFIG_FOLDER=views \
  -e CONN_IP=${CONN_IP} \
  -e CONN_PORT=${CONN_PORT} \
  -e CONFIG_FILE=${CONFIG_FILE} \
  -v al-gui-volume:/app/AnyLog-GUI/views:rw \
  -d -it --detach-keys="ctrl-d" -p ${CONN_PORT}:${CONN_PORT} --rm anylog-gui:latest
