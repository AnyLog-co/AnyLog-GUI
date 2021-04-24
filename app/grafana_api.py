

# Example - https://avleonov.com/2020/06/10/how-to-list-create-update-and-delete-grafana-dashboards-via-api/


from app import json_api
from app import rest_api

import requests
import copy
import sys
from datetime import datetime

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
# Get the list of panels for the dashboard name
# -----------------------------------------------------------------------------------
def get_panels(grafana_url:str, token:str, dashboard_name:str):

    panels_list = []
    reply, err_msg = get_dashboards(grafana_url, token)
    if reply:
        dashboard_id, dashboard_uid, dashboard_version, err_msg = get_existing_dashboaard(reply, dashboard_name)
        if dashboard_id:
            dashboard_info, err_msg = get_dashboard_info(grafana_url, token, dashboard_uid, dashboard_name)
            if dashboard_info:
                if 'dashboard' in dashboard_info and 'panels' in dashboard_info['dashboard']:
                    panels = dashboard_info['dashboard']['panels']
                    for entry in panels:
                        if 'title' in entry:
                            panels_list.append(entry['title'])

    return panels_list

# -----------------------------------------------------------------------------------
# Deploy a report
# With Grafana - a report is a dashboard, each dashboard has multiple panels (a visualization window), each panel has multiple targets (queries to a table)
# If the report is new - add the report
# If the report exists - make an update
# -----------------------------------------------------------------------------------
def deploy_report(**platform_info):
    
    
    params_required = [
        ("url", str),
        ("token", str),
        ("report_name",str),
        ("tables_list",list),
        ("base_report",str),                 # The list of base reports
        ("from_date", str),
        ("to_date", str),
        ("functions",list),                 # Query functions like min max etc
        ("operation", str),
    ]

    for param in params_required:
        key = param[0]
        if key not in platform_info:
            # Missing param
            err_msg = "Grafana: Missing '%s' in visualization parameters" % key
            return [None, err_msg]
        value = platform_info[key]
        if not isinstance(value, param[1]):
            # Wrong data type
            err_msg = "Grafana: Wrong visualization data structure for '%s'" % key
            return [None, err_msg]
        
    grafana_url = platform_info['url']
    token =  platform_info['token']
    dashboard_name =  platform_info['report_name']
    tables_list =  platform_info['tables_list']
    from_date = platform_info["from_date"]
    to_date = platform_info["to_date"]
    functions = platform_info["functions"]
    operation = platform_info["operation"]      # Add panel or delete or remove a panel
    if 'title' in platform_info:
        title = platform_info['title']
    else:
        title = dashboard_name                  # Use same nme as dashboard

    url = None
    # Get the list of dashboards
    reply, err_msg = get_dashboards( grafana_url, token )
    
    if reply:
        dashboard_id, dashboard_uid, dashboard_version, err_msg = get_existing_dashboaard(reply, dashboard_name)
    else:
        err_msg = "Grafana API: Failed to provide the list of dashboards"

    if not err_msg:

        if not dashboard_id:
            # deploy a new report
            base_dashboard = platform_info['base_report']
            dashboard_id, dashboard_uid, dashboard_version, err_msg = get_existing_dashboaard(reply, base_dashboard)
            if not dashboard_id:
                # Missing base report
                err_msg = "Grafana API: Missing base dasboard: %s" % base_dashboard
            else:
                # Get the report
                dashboard_info, err_msg = get_dashboard_info(grafana_url, token, dashboard_uid, dashboard_name)
                if not err_msg:
                    # Update the dasboard based on the tables and time to query
                    is_modified, error_msg = modify_dashboard(dashboard_info["dashboard"], dashboard_name, tables_list, functions)
                    if error_msg:
                        err_msg = "Grafana API: Unable to update dasboard %s" % dashboard_name
                    else:
                        dashboard_uid, err_msg = add_dashboard(grafana_url, token, dashboard_name, dashboard_info["dashboard"])
                        if not err_msg:
                            url = "%s/d/%s/%s" % (grafana_url, dashboard_uid, dashboard_name)
        else:
            # Update an existing report
            dashboard_info, err_msg = get_dashboard_info( grafana_url, token, dashboard_uid, dashboard_name )
            if not err_msg:
                if not dashboard_version:
                    if "meta" in dashboard_info and "version" in  dashboard_info["meta"]:
                        dashboard_version = dashboard_info["meta"]["version"]
                    else:
                        dashboard_version = 1

                # Update the dasboard based on the tables and time to query
                is_modified, error_msg = modify_dashboard(dashboard_info["dashboard"], dashboard_name, tables_list, functions)
                if error_msg:
                    err_msg = "Grafana API: Unable to update dasboard %s" % dashboard_name
                else:
                    if is_modified:
                        # push update to Grafana
                        if not update_dashboard(grafana_url, token, dashboard_info["dashboard"], dashboard_id, dashboard_uid, dashboard_version):
                            # Failed to upfate a report
                            err_msg = "Grafana API: Failed to update dasboard %s" % dashboard_name

                    if not err_msg and "url" in dashboard_info["meta"]:
                        url = "%s/d/%s/%s" % (grafana_url, dashboard_uid, dashboard_name)
            else:
                err_msg = "Grafana API: Unable to extract version from dasboard %s" % dashboard_name

    if not err_msg:
        # Time range is added to the URL - https://grafana.com/docs/grafana/latest/dashboards/time-range-controls/#control-the-time-range-using-a-url
        # Example data to add:
        # ?&from=1614585600000&to=1619938799000
        # ?&from=now-90d&to=now
        # ?&from=now-2M&to=now
        # ?&from=202103011248&to=202105011248
        if to_date[:3] == "now":
            url += "?&from=%s&to=now" % from_date
        else:
            # Transform to  ms epoch
            ms_from = int((datetime(int(from_date[:4]), int(from_date[5:7]), int(from_date[8:10]), int(from_date[11:13]), int(from_date[14:16]) ) \
                           - datetime(1970, 1, 1)).total_seconds() * 1000)
            ms_to = int((datetime(int(to_date[:4]), int(to_date[5:7]), int(to_date[8:10]), int(to_date[11:13]), int(to_date[14:16])) \
                 - datetime(1970, 1, 1)).total_seconds() * 1000)
            url += "?&from=%s&to=%s" % (str(ms_from), str(ms_to))

    return [url, err_msg]
# -----------------------------------------------------------------------------------
# Find a dashboard by name
# -----------------------------------------------------------------------------------
def get_existing_dashboaard( dasborads_reply, dashboard_name ):

    report_id = 0
    report_uid = ""
    report_version = 0
    if dasborads_reply.status_code == 200:
        # List of all dashboards is available
        try:
            dashboards = dasborads_reply.json()
        except:
            err_msg = "Grafana API: Unable to parse data retrieved from request to dashboards"
        else:
            err_msg = None

            # test if the report is in the list
            for entry in dashboards:
                # every entry is a report
                if "type" in entry and entry["type"] == 'dash-db':
                    # this is a dashboard entry
                    if "title" in entry and entry["title"] == dashboard_name:
                        # reports exists
                        report_id = entry["id"]
                        report_uid = entry["uid"]
                        if "version" in entry:
                            report_version = entry["version"]


    return [report_id, report_uid, report_version, err_msg]
# -----------------------------------------------------------------------------------
# Get a report
# If the report is new - add the report
# If the report exists - make an update
# -----------------------------------------------------------------------------------
def get_dashboard_info(grafana_url, token, dashboard_uid, dashboard_name):
    '''
    Return the JSON data of the dashboard
    '''

    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }

    # get the content of dashboard from the example above
    url = grafana_url + "/api/dashboards/uid/" + dashboard_uid
    response, err_msg = rest_api.do_get(url, headers)

    if response.status_code == 200:
        try:
            dashboard_struct = response.json()
        except:
            ret_val = False
        else:
            ret_val = True
            err_msg = None
    else:
        ret_val = False

    if not ret_val:
        err_msg = "Grafana API: Failed to retrieve dashboard %s" % dashboard_name
        dashboard_struct = None

    return [dashboard_struct, err_msg]

# -----------------------------------------------------------------------------------
# Add a new report
# -----------------------------------------------------------------------------------
def add_dashboard(grafana_url:str, token:str, dashboard_name:str, new_dashboard):

    url = "%s/api/dashboards/db" % grafana_url

    headers_data = {
        "Authorization":"Bearer %s" %token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    new_dashboard_data = {
    "folderId": 0,
    "overwrite": False
    }

    new_dashboard["title"] = dashboard_name
    new_dashboard["id"] = None
    new_dashboard["uid"] = None
    new_dashboard["version"] = 0
    new_dashboard_data["dashboard"] = new_dashboard


    dashboard_uid = None
    dashboard_data, err_msg = json_api.json_to_string(new_dashboard_data)

    if dashboard_data:
        response, err_msg = rest_api.do_post(url=url, headers_data=headers_data, data_str=dashboard_data)

        if response:
            if response.status_code != 200:
                err_msg = "Grafana API: Failed to update a mew dashboard"
            else:
                try:
                    post_reply = response.json()
                except:
                    errno, err = sys.exc_info()[:2]
                    err_msg =  "Grafana API: Failed to update  new dashboard: %s" % str(err)
                else:
                    dashboard_uid =  post_reply["uid"]

    
    return [dashboard_uid, err_msg]
# -----------------------------------------------------------------------------------
# Get dasboards IDs
# There is no method to list dashboards, - do an empty search request and get dashboards from the results.
# -----------------------------------------------------------------------------------
def get_dashboards( grafana_url, token ):

    '''
    Return a list with all the dasboards
    '''

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

# -----------------------------------------------------------------------------------
# update an existing dashboard. 
# delete and create generates a new ID - this new one will have new UID and the UID is in the dashboard’s URL. 
# The update operation:
# * get data for an existing dashboard by UID, extract it’s id and version. 
# * set id, uid, incremented version and set overwrite parameter to true. 
# * make the same request as creating a new dashboard.dashboard
# -----------------------------------------------------------------------------------
def update_dashboard(grafana_url, token, dashboard_data, report_id, report_uid, report_version):

    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }

    dashboard_data['id'] = report_id
    dashboard_data['uid'] = report_uid
    dashboard_data['version'] = report_version + 1


    updated_dashboard_data = {
        "dashboard":   dashboard_data,
        "folderId": 0,
        "overwrite": True
    }

    #dashboard_data["panels"][0]['targets'].append(dashboard_data["panels"][0]['targets'][0])
    url = grafana_url + "/api/dashboards/db/"

    # http://127.0.0.1:3000/d/KnYOOwuMz/my_report
    # https://www.metricfire.com/docs/grafana-http-api/#Update-dashboard

    dashboard_data, err_msg = json_api.json_to_string(updated_dashboard_data)

    if dashboard_data:
        response, err_msg = rest_api.do_post(url=url, headers_data=headers, data_str=dashboard_data)

    if err_msg or response.status_code != 200:
        ret_val = False
    else:
        ret_val = True

    #reply = requests.post(url=url, headers=headers, data=json.dumps(updated_dashboard_data), verify=False)

    return ret_val


# -----------------------------------------------------------------------------------
# Update the dashboard -
# Go over all the panels and modify the targets on each panel.
# Each target[0] is duplicated for each database and table
# -----------------------------------------------------------------------------------
def modify_dashboard(dashboard, dashboard_name, tables_list, functions):
    error_msg = None
    panels_list = dashboard["panels"]
    is_modified = False

    for panel in panels_list:
        if not "title" in panel or not panel["title"] or panel["title"] == "Panel Title":
            # Change the panel name to be as the report name
            panel["title"] = dashboard_name
        targets = panel["targets"]      # Get the list of queries
        updated_targets = []
        if len(targets):
            base_target = copy.deepcopy(targets[0])    # An example target
            for table in tables_list:
                if "data" in base_target:
                    json_str =  base_target["data"]         # This is the ANyLog Query
                    al_query, err_msg = json_api.string_to_json(json_str)
                    if not al_query or not isinstance(al_query,dict):
                        error_msg = "Grafana API: Report (%s) does not contain 'Additional JSON Data' definitions" % dashboard_name
                        break

                    al_query["dbms"] = table[0]
                    al_query["table"] = table[1]

                    if len(functions):
                        # If user specified SQL functions Min Max etc
                        al_query["functions"] = functions

                    # Map back to a string

                    data, error_msg = format_grafana_json(al_query)
                    if error_msg:
                        error_msg = "Grafana API: Report (%s) failed to process 'Additional JSON Data' definitions" % dashboard_name
                        break

                    base_target["data"] = data
                    updated_targets.append(copy.deepcopy(base_target))   # Create a new entry
                    is_modified = True

            if is_modified:
                panel["targets"] = updated_targets     # Add a target with the dbms and table

    return [is_modified, error_msg]

# -----------------------------------------------------------------------------------
# Format the Grafana JSON (in the additional JSON data)
# -----------------------------------------------------------------------------------
def format_grafana_json(al_query):

    data_str, error_msg = json_api.json_to_string(al_query)
    if error_msg:
        error_msg = "Grafana API: Report (%s) failed to process 'Additional JSON Data' definitions" % dashboard_name
    else:
        error_msg = None
        data_list = data_str.split('[')     # no nre line inside a list

        for index, entry in enumerate(data_list):
            if not index:
                offset = 0  # format the entire row
            else:
                offset = entry.find(']')
            if offset != -1:
                data_formated = entry[offset:].replace(',', ',\r\n')
                data_formated = data_formated.replace('{', '{\r\n')
                data_formated = data_formated.replace('}', '\r\n}')
                data_formated = entry[:offset] + data_formated
            else:
                data_formated = entry
            data_list[index] = data_formated

        data_formated = '['.join(data_list)

    return [data_formated, error_msg]

