#!/bin/bash
<<COMMENT
  The following deploys' AnyLog GUI as a Docker instance.
  As such it requires the following installed on the machine:
    * Docker
    * Grafana or other BI tool
COMMENT

if [[ $# -eq 1 ]]
then 
    CONFIG_FILE=$1 
else 
   echo "Missing views file" 
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
docker run  -e CONFIG_FOLDER=views -e CONFIG_FILE=${CONFIG_FILE} -v al-gui-volume:/app/AnyLog-GUI/views:rw -d -p 5000:5000 --name anylog-gui --network host --rm anylog-gui:latest
