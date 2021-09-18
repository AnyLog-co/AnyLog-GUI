<<COMMENT
  The following deploys' AnyLog GUI directly on the physical machine.
  As such it requires the following installed on the machine:
    * Python3
      * [flask](https://pypi.org/project/Flask/)
      * [flask_nav](https://pypi.org/project/flask-nav/)
      * [flask_table](https://pypi.org/project/Flask-Table/)
      * [flask_wtf](https://pypi.org/project/Flask-WTF/)
      * [requests](https://pypi.org/project/requests/)
      * [uwsgi](https://pypi.org/project/uWSGI/)
    * [nginx](https://nginx.org/en/)
    * Grafana or other BI tool
COMMENT

if [[ $# -eq 2 ]]
then 
    ROOT_DIR=$1
    VIEW=$2 
else 
    ROOT_DIR=$HOME/AnyLog-GUI
    VIEW=testnet.json
    printf "Root Dir is set to: ${ROOT_DIR}\nView file is set to: ${VIEW}\n" 
fi 

if [[ -f ${VIEW} ]] 
then
   cp ${VIEW} ${ROOT_DIR}/view.json 
elif [[ -f ${ROOT_DIR}/views/${VIEW} ]] 
then
   cp ${ROOT_DIR}/views/${VIEW} ${ROOT_DIR}/view.json 
else
   echo "Failed to locate ${VIEW}. Please provide full path or make sure file is in ${ROOT_DIR}/view" 
   exit 1
fi 
VIEW=${ROOT_DIR}/views/demo.json  

export FLASK_APP=${ROOT_DIR}/anylog.py 
export FLASK_ENV=development
export GUI_VIEW=${VIEW} 

flask run 
#uwsgi --socket 0.0.0.0:5000 --protocol=http \
#	--check-static ${ROOT_DIR}/app/static \
#	--static-map2 /static=${ROOT_DIR}/app/static \
#       	-w wsgi:app

