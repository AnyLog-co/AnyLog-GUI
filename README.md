# AnyLog-GUI
The following is the GUI interface for AnyLog 

## Requirments
* Python3
  * [flask](https://pypi.org/project/Flask/)
  * [flask_nav](https://pypi.org/project/flask-nav/) 
  * [flask_table](https://pypi.org/project/Flask-Table/) 
  * [flask_wtf](https://pypi.org/project/Flask-WTF/)
  * [requests](https://pypi.org/project/requests/)
  * [uwsgi](https://pypi.org/project/uWSGI/)
* [nginx](https://nginx.org/en/) 
* Grafana or other BI tool 

## Setup
1. Install [Grafana instance](docker_grafana.sh) 
   * Grafana URL `http://${IP}:3000` 
   * Initial Username & Password: `admin | admin`
2. [Configure your Grafana](https://github.com/AnyLog-co/documentation/blob/master/using%20the%20gui.md#configure-grafana) instance to allow for embedding and anonymous option.  
3. Generate an [API Token](https://grafana.com/docs/grafana/latest/http_api/create-api-tokens-for-org/) with admin privileges.   
The API token will be added into the JSON object that the AnyLog GUI reads.  
```
curl -X POST -H "Content-Type: application/json" -d '{"name":"apikeycurl", "role": "Admin"}' http://admin:admin@localhost:3000/api/auth/keys
```
3. Create a new JSON data source connected to your Query Node. 
4. In AnyLog-GUI, create a new JSON object in [views](views/)
   1. Copy one of the existing JSON files in [views](views/) to your a new file in [views](views/)
   2. Update the following: 
      * Company Name ("name" in JSON object)
      * Node IPs & Ports (ex. query_node) 
      * URLs (ex. map and "url_pages" sections)
      * Grafana API token
      * In the first case of "children" tree, update with queries that match your blockchain
   3. Save new JSON object in [views](views/)
5. In Grafana, create a new folder called `AnyLog_${Company Name}` ; where the `${COMPANY NAME}` is the same the one in the newly created JSON. 
6. Within the new folder, there should be  3 files, each containing both a widget and line graph with the connection type set to your Query node. The files should be named as follows: 
   * AnyLog_Base
   * Current Status
   * current_status
7. Deploy AnyLog-GUI
   * **Option 1**: Deploy directly on machine
```
bash $HOME/AnyLo-GUI/local_deployment.sh ${ROOT_DIR} ${JSON_FILE_NAME}

# Example
bash $HOME/AnyLo-GUI/local_deployment.sh $HOME/AnyLog-GUI tstnet.json 
```
   * **Option 2**: Deploy via Docker (this requries only Docker & Grafana installed instead of the requirments list)
```
bash $HOME/AnyLo-GUI/docker_deployment.sh ${JSON_FILE_NAME}

# Example
bash $HOME/AnyLo-GUI/docker_deployment.sh testnet.json 
```
