
from app import json_api
from app import rest_api


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


