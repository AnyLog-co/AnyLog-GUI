'''
By using this source code, you acknowledge that this software in source code form remains a confidential information of AnyLog, Inc.,
and you shall not transfer it to any other party without AnyLog, Inc.'s prior written consent. You further acknowledge that all right,
title and interest in and to this source code, and any copies and/or derivatives thereof and all documentation, which describes
and/or composes such source code or any such derivatives, shall remain the sole and exclusive property of AnyLog, Inc.,
and you shall not edit, reverse engineer, copy, emulate, create derivatives of, compile or decompile or otherwise tamper or modify
this source code in any way, or allow others to do so. In the event of any such editing, reverse engineering, copying, emulation,
creation of derivative, compilation, decompilation, tampering or modification of this source code by you, or any of your affiliates (term
to be broadly interpreted) you or your such affiliates shall unconditionally assign and transfer any intellectual property created by any
such non-permitted act to AnyLog, Inc.
'''

'''
Grafana Config file needs to be set to allow embedding:
To validate setting: go to Server-Admin (Left side on the main panel) --> Setting --> allow_embedding : true
'''

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

    response, err_msg = rest_api.do_get(url, headers)

    if response and response.status_code == 200:
        ret_val = True
    else:
        ret_val = False
    
    return [ret_val, err_msg]

# -----------------------------------------------------------------------------------
# Get the list of Dashboards (reports) for the given directory
# For each dashboard - pull the panels
# Return a list of all the panels per each dashboard
# -----------------------------------------------------------------------------------
def get_reports(url:str, token:str, directory:str):
    '''
    Return the list of urls to the panels of the dashboards in the directory
    '''

    directory_name = directory.lower()

    # Get the list of grafana folders
    folder_id = -1
    folders, err_msg = get_folders(url, token)
    for entry in folders:
        if "title" in entry and "id" in entry:
            if entry["title"].lower() == directory_name :
                folder_id = entry["id"]
                break

    if folder_id != -1:

        dashboards, err_msg = get_dashboards(url, folder_id, token)

        panels = {}
        if not err_msg:
            for entry in dashboards:
                # every entry is a report
                if "type" in entry and entry["type"] == 'dash-db':
                    # this is a dashboard entry
                    if "title" in entry:
                        # reports exists
                        dashboard_name = entry['title']
                        dashboard_id = entry["id"]
                        dashboard_uid = entry["uid"]
                        if "version" in entry:
                            report_version = entry["version"]
                        dashboard_info, err_msg = get_dashboard_info(url, token, dashboard_uid, dashboard_name)
                        if dashboard_info:
                            if 'dashboard' in dashboard_info and 'panels' in dashboard_info['dashboard']:
                                panels_urls = get_panels_urls(url, dashboard_info, dashboard_uid, dashboard_name)
                                panels[dashboard_name] = panels_urls

    return [panels, err_msg]

# -----------------------------------------------------------------------------------
# Get panels URLs of a particular dashboard - the urls are based on the dashboard url and the panel ID.
# -----------------------------------------------------------------------------------
def get_panels_urls(grafana_url, dashboard_info, dashboard_uid, dashboard_name):
    base_url = grafana_url.replace("localhost", "127.0.0.1")  # Otherwise Iframe does not works
    base_url = "%s/d/%s/%s" % (base_url, dashboard_uid, dashboard_name)

    panels_list = []
    for panel in dashboard_info['dashboard']['panels']:
        id = panel['id']
        panel_url = base_url + "?orgId=1&viewPanel=%u" % (id)
        panel_url += get_url_time_range(None)
        panels_list.append(panel_url)

    return panels_list  # Return list of urls, one for each panel
# -----------------------------------------------------------------------------------
# Get the list of panels for the dashboard name
# -----------------------------------------------------------------------------------
def get_panels(grafana_url:str, token:str, dashboard_name:str):

    panels_list = []
    reply, err_msg = get_dashboards(grafana_url, "", token)
    if not err_msg:
        dashboard_id, dashboard_uid, dashboard_version = get_existing_dashboaard(reply, dashboard_name)

        if dashboard_id:
            dashboard_info, err_msg = get_dashboard_info(grafana_url, token, dashboard_uid, dashboard_name)
            if dashboard_info:
                if 'dashboard' in dashboard_info and 'panels' in dashboard_info['dashboard']:
                    panels = dashboard_info['dashboard']['panels']
                    for entry in panels:
                        if 'title' in entry:
                            panels_list.append(entry['title'])

    return [panels_list, err_msg]

# --------------------------------------------------------
# Provide status on the list of entries at platform_info["projection_list]
# Example URL returned: http://127.0.0.1:3000/d/nfDMna9Gz/current_status?orgId=1&viewPanel=2&from=-2M&to=now
# --------------------------------------------------------
def status_report(**platform_info):

    params_required = [
        ("url", str),
        ("token", str),
        ("base_report", str),
        ("functions", list),
        ("projection_list", list),
    ]

    err_msg = test_params(params_required, platform_info)
    if err_msg:
        return [None, err_msg]

    grafana_url = platform_info['url']
    token =  platform_info['token']

    err_msg = get_init_dashboard(platform_info, "current_status")
    if err_msg:
        return [None, err_msg]

    dashboard_uid = platform_info['dashboard_uid']
    dashboard_version = platform_info['dashboard_version']
    new_dashboard = platform_info["new_dashboard"]

    dashboard_info, err_msg = get_dashboard_info(grafana_url, token, dashboard_uid, "current_status") # The Grafana dasboard requested or the base_report
    if err_msg:
        return [None, err_msg]

    projection_list = platform_info["projection_list"]
    functions = platform_info["functions"]

    is_modified, err_msg = create_dashboard(dashboard_info["dashboard"], "current_status", platform_info)

    '''
    copy_dash = copy.deepcopy(dashboard_info)

    is_modified, err_msg = make_status_dashboard(dashboard_info["dashboard"], "current_status", projection_list, functions)
    '''

    if err_msg:
        return [None, err_msg]

    err_msg = add_update_dashboard(new_dashboard, is_modified, platform_info, "current_status", dashboard_info)
    if err_msg:
        return [None, err_msg]

    base_url = grafana_url.replace("localhost", "127.0.0.1")    # Otherwise Iframe does not works
    base_url = "%s/d/%s/%s" % (base_url, dashboard_uid, "current_status")

    panels_list = []
    panels_counter = len(dashboard_info['dashboard']['panels'])
    for i in range (panels_counter):        # Create a url for each Panel
        panel_url = base_url + "?orgId=1&viewPanel=%u" % (i + 1)
        panel_url += get_url_time_range(platform_info)
        panels_list.append(panel_url)

    return [panels_list, None]      # Return list of urls, one for each panel


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

    err_msg = test_params(params_required, platform_info)
    if err_msg:
        return  [None, err_msg]

        
    grafana_url = platform_info['url']
    token =  platform_info['token']
    dashboard_name =  platform_info['report_name']
    tables_list =  platform_info['tables_list']
    functions = platform_info["functions"]
    operation = platform_info["operation"]      # Add panel or delete or remove a panel
    if 'title' in platform_info:
        title = platform_info['title']
    else:
        title = dashboard_name                  # Use same nme as dashboard

    # Get the requested dashboard or the base dashboard
    err_msg = get_init_dashboard(platform_info, dashboard_name) # Info is updated in platform_info
    if err_msg:
        return [None, err_msg]

    dashboard_uid = platform_info['dashboard_uid']
    dashboard_version = platform_info['dashboard_version']
    new_dashboard = platform_info["new_dashboard"]

    dashboard_info, err_msg = get_dashboard_info(grafana_url, token, dashboard_uid, dashboard_name) # The Grafana dasboard requested or the base_report
    if err_msg:
        return [None, err_msg]

    is_modified, err_msg = modify_dashboard(dashboard_info["dashboard"], operation, dashboard_name, title, tables_list, functions)
    if err_msg:
        return [None, err_msg]

    err_msg = add_update_dashboard(new_dashboard, is_modified, platform_info, dashboard_name, dashboard_info)
    if err_msg:
        return [None, err_msg]


    url = "%s/d/%s/%s" % (grafana_url, dashboard_uid, dashboard_name)
    url += get_url_time_range(platform_info)

    return [url, None]


# -----------------------------------------------------------------------------------
# Given a dashboard - if the dashboard is new - add the dashboard, otherwise update the dashboard
# -----------------------------------------------------------------------------------
def add_update_dashboard(new_dashboard, is_modified, platform_info, dashboard_name, dashboard_info):

    grafana_url = platform_info['url']
    token = platform_info['token']
    dashboard_uid = platform_info['dashboard_uid']
    dashboard_version = platform_info['dashboard_version']
    new_dashboard = platform_info["new_dashboard"]


    if new_dashboard:
        # First time that the dasboard with that name is written
        dashboard_uid, err_msg = add_dashboard(grafana_url, token, dashboard_name, dashboard_info["dashboard"])
        if err_msg:
            return err_msg

    else:

        dashboard_id = platform_info["dashboard_id"]

        if not dashboard_version:
            if "meta" in dashboard_info and "version" in dashboard_info["meta"]:
                dashboard_version = dashboard_info["meta"]["version"]
            else:
                dashboard_version = 1

        if is_modified:
            # push update to Grafana
            if not update_dashboard(grafana_url, token, dashboard_info["dashboard"], dashboard_id, dashboard_uid,
                                    dashboard_version):
                # Failed to upfate a report
                return "Grafana API: Failed to update dasboard %s" % dashboard_name

    return None
# -----------------------------------------------------------------------------------
# Get the dashboard to use
# -----------------------------------------------------------------------------------
def get_init_dashboard(platform_info, dashboard_name):
    '''
    Get the dashboard using the name, if doesn't exists, get the base dashboard
    '''

    grafana_url = platform_info['url']
    token = platform_info['token']

    reply, err_msg = get_dashboards(grafana_url, "", token)
    if err_msg:
        return "Grafana API: Failed to provide the list of dashboards: %s" % err_msg

    dashboard_id, dashboard_uid, dashboard_version = get_existing_dashboaard(reply, dashboard_name)


    if dashboard_id:
        new_dashboard = False
    else:
        new_dashboard = True
        base_dashboard = platform_info['base_report']  # Get the initial report name from the config file
        dashboard_id, dashboard_uid, dashboard_version = get_existing_dashboaard(reply, base_dashboard)

        if not dashboard_id:
            # Missing base report
            return "Grafana API: Missing base dashboard: %s Using: %s" % (base_dashboard, grafana_url)

    platform_info["new_dashboard"] = new_dashboard
    platform_info["dashboard_id"] = dashboard_id
    platform_info["dashboard_uid"] = dashboard_uid
    platform_info["dashboard_version"] = dashboard_version

    return None
# -----------------------------------------------------------------------------------
# Get the time tange in the format for the URL
# Time range is added to the URL - https://grafana.com/docs/grafana/latest/dashboards/time-range-controls/#control-the-time-range-using-a-url
    # Example data to add:
    # ?&from=1614585600000&to=1619938799000
    # ?&from=now-90d&to=now
    # ?&from=now-2M&to=now
    # ?&from=202103011248&to=202105011248
# -----------------------------------------------------------------------------------
def get_url_time_range(platform_info):

    if not platform_info:
        time_url = "?&to=now&from=now-%s" % "2M"   # Arbitrary default
    else:

        from_date = platform_info["from_date"]
        to_date = platform_info["to_date"]

        if to_date[:3] == "now":
            time_url = "?&from=%s&to=now" % from_date
        else:
            # Transform to  ms epoch
            ms_from = int((datetime(int(from_date[:4]), int(from_date[5:7]), int(from_date[8:10]), int(from_date[11:13]), \
                                    int(from_date[14:16])) \
                           - datetime(1970, 1, 1)).total_seconds() * 1000)
            ms_to = int( \
                (datetime(int(to_date[:4]), int(to_date[5:7]), int(to_date[8:10]), int(to_date[11:13]), int(to_date[14:16])) \
                 - datetime(1970, 1, 1)).total_seconds() * 1000)

            time_url = "?&from=%s&to=%s" % (str(ms_from), str(ms_to))

    return time_url

# -----------------------------------------------------------------------------------
# Find a dashboard by name
# -----------------------------------------------------------------------------------
def get_existing_dashboaard( dashboards, dashboard_name ):

    report_id = 0
    report_uid = ""
    report_version = 0

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


    return [report_id, report_uid, report_version]
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
# Get the list of Folders
# -----------------------------------------------------------------------------------
def get_folders(grafana_url, token):
    '''
    Return a list with all the dashboards
    '''

    dashboards, err_msg = grafana_get("Get Dashboards", grafana_url, "/api/folders", token)

    return [dashboards, err_msg]


# -----------------------------------------------------------------------------------
# Get dashboards IDs
# There is no method to list dashboards, - do an empty search request and get dashboards from the results.
# Details - https://grafana.com/docs/grafana/latest/http_api/folder_dashboard_search/
# -----------------------------------------------------------------------------------
def get_dashboards( grafana_url, folder_id, token ):

    '''
    Return a list with all the dashboards
    '''

    if folder_id:
        query = "/api/search?folderIds=%u&query=%s" % (folder_id, '%')
    else:
        query = "/api/search?query=%"

    dashboards, err_msg = grafana_get("Get Dashboards", grafana_url, query, token)

    return [dashboards, err_msg]

# -----------------------------------------------------------------------------------
# Grafana Get Call, transform the reply to JSON
# -----------------------------------------------------------------------------------
def grafana_get(get_type, grafana_url, query, token):

    headers = {
        "Authorization":"Bearer %s" % token,
        "Content-Type":"application/json",
        "Accept": "application/json"
    }

    url = grafana_url + query

    response, err_msg = rest_api.do_get(url, headers)

    json_info = None
    if not err_msg:
        if response.status_code == 200:
            # List of all dashboards is available
            try:
                json_info = response.json()
            except:
                errno, value = sys.exc_info()[:2]
                err_msg = "Grafana API: Unable to parse Grafana reply for '%s' (Errno: %s, %s) using URL: %s" % (get_type, str(errno), str(value), url)
            else:
                err_msg = None

        else:
            info = ""
            if hasattr(response, 'reason'):
                info = response.reason
            if hasattr(response, 'text'):
                info += ' [' + response.text + ']'

            err_msg = "HTTP GET returned code %u - (%s) URL: %s" % (response.status_code, info, url)

    return [json_info, err_msg]
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
# Make a dashboard based on a source dashboard and params set in platform_info
# -----------------------------------------------------------------------------------
def create_dashboard(dashboard, dashboard_name, platform_info):
    '''
    The status dashboard shows 2 panels for every sensor:
    1) Last data available
    2) Graph of last 24 hours

    :param dashboard:         The previously used dashboard or the base
    :param dashboard_name:    A name for the dashboard
    :param platform_info:     The definitions of the new dashboard
    '''

    panels_list = dashboard["panels"]
    panels_counter = len(panels_list)
    if not panels_counter:
        # A report needs to have one panel
        return [False, "Grafana API: Source dashbord (%s) has no panels" % dashboard_name]

    new_dashboard_defs = platform_info["dashboard"]     # The definitions of a new dashboard


    # The source panel is duplicated twice for every entry in the projection
    # Showing the last week trends and showing last values
    source_panel = copy.deepcopy(panels_list[0])
    panels_list = []        # Start from empty list
    dashboard["panels"] = panels_list

    panel_id = 0
    is_modified = False
    err_msg = None
    for new_panel_defs in  new_dashboard_defs.panels:
        # Go over all new panels definitions
        new_panel_name = new_panel_defs.panel_name
        new_projection_list = new_panel_defs.projection_list
        new_panel_type = new_panel_defs.panel_type         # "Graph" or "Gauge"

        new_panel = copy.deepcopy(source_panel)         # Get source panel
        panel_id += 1
        new_panel['id'] = panel_id                      # Set the panel ID
        panels_list.append(new_panel)                   # Connect the panel to the dashboard

        is_modified, err_msg = update_panel(dashboard_name, new_panel, new_panel_name, new_panel_type, new_projection_list)

    return [is_modified, err_msg]

# -----------------------------------------------------------------------------------
# Replace the content of an existing panel
# -----------------------------------------------------------------------------------
def update_panel( dashboard_name, panel, panel_title, display_type, projection_list):
    '''
    Set a new panel and modify the panel definitions as needed
    :param dashboard_name:
    :param panel:               The JSON Panel info from Grafana
    :param panel_title:
    :param display_type:        Grafana - gauge or graph
    :param projection_list:     Tables, query per tables, query functions
    '''

    err_msg = None
    is_modified = False
    if not "title" in panel or not panel["title"] or panel["title"] != panel_title:
        # Change the panel name to be as the report name
        panel["title"] = panel_title
        is_modified = True

    if not "type" in panel or panel["type"] != display_type:
        panel["type"] = display_type        # gauge or graph
        is_modified = True


    # Make Grafana source Panel


    updated_targets = []
    for projection in projection_list:
        # Define the queries for the panel
        new_target = {}
        new_target['refId'] = 'A'
        new_target['target'] = ''
        new_target['type'] = 'timeseries'

        # Make source data representing 'Additional JSON Data' on the panel
        al_query = {}
        al_query['value_column'] = projection.value_column
        al_query['timestamp_column'] = projection.timestamp_column
        al_query['functions'] = projection.functions
        al_query["dbms"] = projection.dbms_name
        al_query["table"] = projection.table_name
        al_query["type"] = projection.query         # "increments" or "period
        # Map back to a string

        data, err_msg = format_grafana_json(al_query)
        if err_msg:
            err_msg = "Grafana API: Report (%s) failed to process 'Additional JSON Data' definitions" % dashboard_name
            break

        new_target["data"] = data

        updated_targets.append(new_target)
        is_modified = True

    if is_modified:
        panel["targets"] = updated_targets  # Add a target with the dbms and table


    return [is_modified, err_msg]
# -----------------------------------------------------------------------------------
# Create a dashboard to show current Status
# -----------------------------------------------------------------------------------
def make_status_dashboard(dashboard, dashboard_name, projection_list, functions):
    '''
    The status dashboard shows 2 panels for every sensor:
    1) Last data available
    2) Graph of last 24 hours

    :param dashboard:         The previously used dashboard or the base
    :param dashboard_name:    Some default name
    :param projection_list:   Data selected by user:  entry_name, dbms_name, table_name
    :param functions:         Min, Max, Avg etc
    :return:
    '''

    panels_list = dashboard["panels"]
    panels_counter = len(panels_list)
    if not panels_counter:
        # A report needs to have one panel
        return [False, "Grafana API: Report (%s) has no panels" % dashboard_name]

    # The source panel is duplicated twice for every entry in the projection
    # Showing the last week trends and showing last values
    source_panel = copy.deepcopy(panels_list[0])
    panels_list = []        # Start from empty list
    dashboard["panels"] = panels_list

    panel_id = 0
    for index, projection in enumerate(projection_list):
        entry_name = projection[0]                      # The sensor name from the sensor policy
        tables_list = [(projection[1], projection[2])]    # The database and table name derived from the policy

        report_type = "increments"      # AnyLog query function
        display_type = "graph"
        for i in range(2):      # Adding 2 panels each time (increments + period) - Current status and last day graph
            new_panel = copy.deepcopy(source_panel)
            panel_id += 1
            new_panel['id'] = panel_id     # Adding 2 panels each time
            panels_list.append(new_panel)  # Duplicate the same panel
            is_modified, err_msg = replace_panel(dashboard_name, report_type, display_type, new_panel, entry_name, tables_list, functions)
            if err_msg:
                break
            report_type = "period"  # AnyLog query function
            display_type = "gauge"

    return [True, err_msg]
# -----------------------------------------------------------------------------------
# Update the dashboard -
# Go over all the panels and modify the targets on each panel.
# Each target[0] is duplicated for each database and table
# -----------------------------------------------------------------------------------
def modify_dashboard(dashboard, operation, dashboard_name, panel_name, tables_list, functions):

    err_msg = None
    is_modified = False
    panels_list = dashboard["panels"]
    panels_counter = len(panels_list)
    if not panels_counter:
        # A report needs to have one panel
        err_msg = "Grafana API: Report (%s) has no panels" % dashboard_name
    else:
        if operation == 'Replace':
            if panels_counter == 1:
                panels_list[0]['id'] = 1
                is_modified, err_msg = replace_panel(dashboard_name, "increments", "graph", panels_list[0], panel_name, tables_list, functions)
            else:
                for panel in panels_list:
                    if 'title' in panel and panel['title'] == panel_name:
                        is_modified, err_msg = replace_panel(dashboard_name, "increments", "graph", panel, panel_name, tables_list, functions)
                        break
                if not err_msg:
                    if not is_modified:
                        err_msg = "Grafana API: Panel (%s) not available in dasboard: %s" % (panel_name, dashboard_name)
        elif operation == 'Add':
            # Find non duplicate name
            for panel in panels_list:
                if 'title' in panel and panel['title'] == panel_name:
                    err_msg =  "Grafana API: Duplicate panel names (%s) for dasboard: %s" % (panel_name, dashboard_name)
                    break
            if not err_msg:
                new_panel = copy.deepcopy(panels_list[0])
                new_panel['id'] = panels_counter + 1
                panels_list.append(new_panel)      # Duplicate the same panel
                is_modified, err_msg = replace_panel(dashboard_name, "increments", "graph", panels_list[-1], panel_name, tables_list, functions)
        elif operation == 'Remove':
            if panels_counter == 1:
                err_msg = "Grafana API: Removal of a panel from a single panel dashboard is not allowed"
            else:
                is_deleted = False
                for index, panel in enumerate(panels_list):
                    if 'title' in panel and panel['title'] == panel_name:
                        is_deleted = True
                        del panels_list[index]
                        break
                if is_deleted:
                    # Change panels IDs
                    for index, panel in enumerate(panels_list):
                        panel['id'] = index + 1
                    is_modified = True

    return [is_modified, err_msg]
# -----------------------------------------------------------------------------------
# Replace the content of an existing panel
# -----------------------------------------------------------------------------------
def replace_panel( dashboard_name, report_type, display_type, panel, panel_title, tables_list, functions):
    '''
    Set a new panel and modify the panel definitions as needed
    :param dashboard_name:
    :param report_type:         AnyLog type of query - Increments or Period - set in targets.data
    :param display_type:        Grafana - gauge or graph
    :param panel:               The JSON Panel info from Grafana
    :param panel_title:
    :param tables_list:         The AnyLog DBMS + Tables to apply - each pair of dbms + table is a query
    :param functions:           The AnyLog functions: Min, Max, Avg
    :return:
    '''

    err_msg = None
    is_modified = False
    if not "title" in panel or not panel["title"] or panel["title"] != panel_title:
        # Change the panel name to be as the report name
        panel["title"] = panel_title
        is_modified = True

    if not "type" in panel or panel["type"] != display_type:
        panel["type"] = display_type        # gauge or graph
        is_modified = True

    if "targets" in panel:
        targets = panel["targets"]  # Get the list of queries
    else:
        # Make Grafana source Panel
        targets = []
        source_panel = {}
        source_panel['refId'] = 'A'
        source_panel['target'] = ''
        source_panel['type'] = 'timeseries'
        targets.append(source_panel)
    updated_targets = []
    if len(targets):
        base_target = copy.deepcopy(targets[0])  # An example target
        for table in tables_list:
            if "data" in base_target:
                json_str = base_target["data"]  # This is the ANyLog Query
                al_query, err_msg = json_api.string_to_json(json_str)
                if not al_query or not isinstance(al_query, dict):
                    err_msg = "Grafana API: Report (%s) does not contain 'Additional JSON Data' definitions" % dashboard_name
                    break
            else:
                # Make source data representing 'Additional JSON Data' on the panel
                al_query = {}
                al_query['value_column'] = 'value'
                al_query['timestamp_column'] = 'timestamp'
                if not len(functions):
                    al_query['functions'] = ["min","max","avg"]

            al_query["dbms"] = table[0]
            al_query["table"] = table[1]

            al_query["type"] = report_type

            if len(functions):
                # If user specified SQL functions Min Max etc
                al_query["functions"] = functions

            # Map back to a string

            data, err_msg = format_grafana_json(al_query)
            if err_msg:
                err_msg = "Grafana API: Report (%s) failed to process 'Additional JSON Data' definitions" % dashboard_name
                break

            base_target["data"] = data
            updated_targets.append(copy.deepcopy(base_target))  # Create a new entry
            is_modified = True

        if is_modified:
            panel["targets"] = updated_targets  # Add a target with the dbms and table

    return [is_modified, err_msg]
# -----------------------------------------------------------------------------------
# Format the Grafana JSON (in the additional JSON data)
# -----------------------------------------------------------------------------------
def format_grafana_json(al_query):

    data_str, err_msg = json_api.json_to_string(al_query)
    if err_msg:
        err_msg = "Grafana API: Report (%s) failed to process 'Additional JSON Data' definitions" % dashboard_name
    else:
        err_msg = None
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

    return [data_formated, err_msg]

# -----------------------------------------------------------------------------------
# Test if the list of needed params with the correct data types is passed to the method
# -----------------------------------------------------------------------------------
def test_params(params_required:list, platform_info):

    err_msg = None
    for param in params_required:
        key = param[0]
        if key not in platform_info:
            # Missing param
            err_msg = "Grafana: Missing '%s' in visualization parameters" % key
            break
        value = platform_info[key]
        if not isinstance(value, param[1]):
            # Wrong data type
            err_msg = "Grafana: Wrong visualization data structure for '%s'" % key
            break

    return err_msg