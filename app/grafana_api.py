

# Example - https://avleonov.com/2020/06/10/how-to-list-create-update-and-delete-grafana-dashboards-via-api/


from app import json_api
from app import rest_api

import requests
import json

# -----------------------------------------------------------------------------------
# Connect to Grafana Home dashboard
# -----------------------------------------------------------------------------------
def test_connection( grafana_url:str ):
    '''
    Test connection to Grafana - return True or False
    '''
    server = "%s/grafana" % grafana_url
    
    url = server + "/api/dashboards/home"
    # To get the dashboard by uid
    # url = server + "/api/dashboards/uid/" + uid
    # headers = {"Authorization":"Bearer #####API_KEY#####"}

    headers = {}
    response, error_msg = rest_api.do_get(url, headers)

    if response and response.status_code == 200:
        ret_val = True
    else:
        ret_val = False
    
    return [ret_val, error_msg]

# -----------------------------------------------------------------------------------
# Add a new report
# -----------------------------------------------------------------------------------
def deploy_report(grafana_url:str):

    url = "%s/api/dashboards/db" % grafana_url

    headers = {
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    new_dashboard_data = {
    "dashboard": {
        "id": None,
        "uid": None,
        "title": "Production Overview",
        "tags": [ "templated" ],
        "timezone": "browser",
        "schemaVersion": 16,
        "version": 0
    },
    "folderId": 0,
    "overwrite": False
    }

    r = requests.post(url = url, headers = headers, data = json.dumps(new_dashboard_data), verify=False)
    print(r.json())

