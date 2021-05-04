#!/bin/bash 
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
docker run -e GUI_VIEW=views/${CONFIG_FILE} -v al-gui-volume:/app/AnyLog-GUI/views:rw -d -p 5000:5000 --name anylog-gui --network host anylog-gui:latest
