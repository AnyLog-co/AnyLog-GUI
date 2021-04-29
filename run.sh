if [[ $# -eq 2 ]] 
then 
    ROOT_DIR=$1
    VIEW=$2 
else 
    ROOT_DIR=$HOME/AnyLog-GUI
    VIEW=machines.json
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
VIEW=${ROOT_DIR}/view.json 

export FLASK_APP=${ROOT_DIR}/anylog.py 
export FLASK_ENV=development
export GUI_VIEW=${VIEW} 

# flask run 
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app

#uwsgi --wsgi-file main.py --http :5000
