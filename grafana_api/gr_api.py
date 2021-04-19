


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
    r = requests.get(url = url, headers = headers, verify=False)
    print(r.json())


