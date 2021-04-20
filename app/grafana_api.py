

# Example - https://avleonov.com/2020/06/10/how-to-list-create-update-and-delete-grafana-dashboards-via-api/


from app import json_api
from app import rest_api

import requests
import json
import copy

# -----------------------------------------------------------------------------------
# Connect to Grafana Home dashboard
# -----------------------------------------------------------------------------------
def test_connection( grafana_url:str, token:str ):
    '''
    Test connection to Grafana - return True or False
    '''
    server = "%s/grafana" % grafana_url
    
    url = server + "/api/dashboards/home"

    headers = {}
    if token:
        headers["Authorization"] = "Bearer %s" % token

    response, error_msg = rest_api.do_get(url, headers)

    if response and response.status_code == 200:
        ret_val = True
    else:
        ret_val = False
    
    return [ret_val, error_msg]

# -----------------------------------------------------------------------------------
# Deploy a report
# If the report is new - add the report
# If the report exists - make an update
# -----------------------------------------------------------------------------------
def deploy_report(grafana_url:str, token:str, report_name:str, tables_list:list):

    url = None
    # Get the list of reports
    reply, err_msg = get_dashboards( grafana_url, token )
    
    if reply:
        try:
            dashboards = reply.json()
        except:
            err_msg = "Failed to retrieve info from Grafana" 
        else:
            if reply.status_code == 200:
                report_id = 0
                report_uid = ""
                # test if the report is in the list
                for entry in dashboards:
                    # every entry is a report
                    if "type" in entry and entry["type"] == 'dash-db':
                        # this is a dashboard entry
                        if "title" in entry and entry["title"] == report_name:
                            # reports exists
                            if "uid" in entry:
                                report_uid = entry["uid"]
                            if "id" in entry:
                                report_id = entry["id"]
                            if report_uid and report_id:
                                break       # report found
            else:
                err_msg = "Failed to retrieve info from Grafana. Grafana returned code: %u" % reply.status_code



    if not err_msg:
        if not report_id:
            # deploy a new report
            add_dashboard(grafana_url, token)
        else:
            gr_struct, err_msg = get_single_dashboard( grafana_url, token, report_uid )
            if gr_struct.status_code == 200:
                try:
                    report_struct = gr_struct.json()
                except:
                    err_msg = "Failed to retrieve info from Grafana" 
                else:
                    first_panel = report_struct["dashboard"]["panels"][0]
                    report_struct["dashboard"]["panels"].append(first_panel)
            
            if not err_msg:
                # update report
                update_dashboard(grafana_url, token, gr_struct, report_uid)
    

    return [url, err_msg]
# -----------------------------------------------------------------------------------
# Get a report
# If the report is new - add the report
# If the report exists - make an update
# -----------------------------------------------------------------------------------
def get_single_dashboard(grafana_url, token, report_uid):

    import copy
    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    

    # get the content of dashboard from the example above
    url = grafana_url + "/api/dashboards/uid/" + report_uid
    response, err_msg = rest_api.do_get(url, headers)
    return [response, err_msg]

# -----------------------------------------------------------------------------------
# Add a new report
# -----------------------------------------------------------------------------------
def add_dashboard(grafana_url:str, token:str):

    url = "%s/api/dashboards/db" % grafana_url

    headers_data = {
        "Authorization":"Bearer %s" %token,
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


    reply_url = None
    report_data, err_msg = json_api.json_to_string(new_dashboard_data)

    if report_data:
        response, err_msg = rest_api.do_post(url, headers_data, json.dumps(new_dashboard_data))

        if response:
            if response.status_code != 200:
                err_msg = "Failed to update Grafana report"
            else:
                reply_url = grafana_url
    
    return [reply_url, err_msg]
# -----------------------------------------------------------------------------------
# Get dasboards IDs
# There is no method to list dashboards, - do an empty search request and get dashboards from the results.
# -----------------------------------------------------------------------------------
def get_dashboards( grafana_url, token ):

    url = grafana_url + "/api/search?query=%"
    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }

    response, err_msg = rest_api.do_get(url, headers)

    return [response, err_msg]

# -----------------------------------------------------------------------------------
# Delete a dashboard
# -----------------------------------------------------------------------------------
def delete_dashboard(grafana_url):

    uid = "DoZVWjzGz"
    url = grafana_url + "/api/dashboards/uid/" + uid
    headers = {
        "Authorization":"Bearer #####API_KEY#####",
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    r = requests.delete(url = url, headers = headers, verify=False)
    print(r.json())

# -----------------------------------------------------------------------------------
# update an existing dashboard. 
# delete and create generates a new ID - this new one will have new UID and the UID is in the dashboard’s URL. 
# The update operation:
# * get data for an existing dashboard by UID, extract it’s id and version. 
# * set id, uid, incremented version and set overwrite parameter to true. 
# * make the same request as creating a new dashboard.dashboard
# -----------------------------------------------------------------------------------
def update_dashboard(grafana_url, token, dashboard_data, report_uid):

    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    

    dashboard_data["overwrite"] = "True"

    
    reply = requests.post(url=grafana_url, headers=headers, data=json.dumps(dashboard_data), verify=False)

    pass

 
