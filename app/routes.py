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


from flask import render_template, flash, redirect, request, url_for, session
from flask_table import  Table, Col, LinkCol

from app import app
from app.forms import LoginForm
from app.forms import ConfigForm
from app.forms import CommandsForm
from app.forms import InstallForm
from app.forms import ConfDynamicReport


from app.entities import Item
from app.entities import AnyLogItem

from app.entities import AnyLogTable

from config import Config

import copy
import requests
from requests.exceptions import HTTPError

from app import app_view        # maintains the logical view of the GUI from a JSON File
from app import path_stat       # Maintain the path of the user
from app import visualize       # The connectors to Grafana, Power BI etc
from app import anylog_api      # Connector to the network
from app import rest_api        # REST API
from app import json_api        # JSON data mapper
from app import nav_tree        # Navigation Tree

user_connect_ = False       # Flag indicating connected to the AnyLog Node 

gui_view_ = app_view.gui()            # Load the definition of the user view of the metadata from a JSON file
gui_view_.set_gui()

query_node_ = None

time_selection_ = [
    ("Last 5 minutes", "-5m"),
    ("Last 15 minutes", "-15m"),
    ("Last 30 minutes", "-30m"),
    ("Last hour", "-1h"),
    ("Last 2 hour2", "-2h"),
    ("Last 3 hours", "-3h"),
    ("last 6 hours", "-6h"),
    ("Last 12 hours", "-12h"),
    ("Last 24 hours", "-1d"),
    ("Last 2 days", "-2d"),
    ("Last 7 days", "-7d"),
    ("Last 14 days", "-14d"),
    ("Last 1 month", "-1M"),
    ("Last 2 months", "-2M"),
    ("Last 3 months", "-3M"),
    ("Last 6 months", "-6M"),
    ("last 1 year", "-1y"),
    ("last 2 years", "-2y"),
    ("last 3 years", "-3y"),
]
# -----------------------------------------------------------------------------------
# GUI forms
# HTML Cheat Sheet - http://www.simplehtmlguide.com/cheatsheet.php
# Example Table: https://progbook.org/shop5.html
# -----------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():

    if not user_connect_:
        return redirect(('/login'))        # start with Login

    select_info = get_select_menu()
    select_info['title'] = "AnyLog Network"
    
    return render_template('main.html', **select_info)
# -----------------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------------
@app.route('/login', methods={'GET','POST'})
def login():
    '''
    Input login name & password, connecet to a node in the network
    and move to main page to determine GUI to use
    '''
    global user_connect_

    select_info = get_select_menu( caller = "login" )

    form = LoginForm()

    if form.validate_on_submit():

        target_node = get_target_node()

        al_headers = {
            'command' : 'get status',
            'User-Agent' : 'AnyLog/1.23'
            }

        try:
            response = requests.get(target_node, headers=al_headers)
        except:
            flash('AnyLog: No network connection', category='error')
            user_connect_ = False
        else:
            if response.status_code == 200:
                user_connect_ = True
            else:
                user_connect_ = False
                flash('AnyLog: Netowk node failed to authenticate {}'.format(form.username.data))
        
        if not user_connect_:
            return redirect(('/login'))        # Redo the login

        user_name = request.form['username']
        session['username'] = user_name
        path_stat.set_new_user( user_name )

        return redirect(('/index'))     # Go to main page


    title_str = 'Sign In'

    if 'username' in session:
        user_name = session['username']
        if not path_stat.is_with_user( user_name ):
            path_stat.set_new_user( user_name )

   
    select_info['title'] = title_str
    select_info['form'] = form

    return render_template('login.html', **select_info)

# -----------------------------------------------------------------------------------
# View the report structure being dynamically build by navigation
#
# Called from - base.html
# -----------------------------------------------------------------------------------
@app.route('/dynamic_report/', methods={'GET','POST'})
@app.route('/dynamic_report/<string:report_name>', methods={'GET','POST'})
def dynamic_report( report_name = "" ):
    '''
    View the report being used
    Called from - base.html
    '''
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session['username']

    select_info = get_select_menu()
    if not report_name:
        report_name = select_info["report_name"]

    report_data = path_stat.get_report_info(user_name, report_name)
    if not report_data or not len(report_data["entries"]):
        flash("AnyLog: Report '%s' has no selections" % report_name)
        return redirect(url_for('index')) 

    list_columns = ["ID", "DBMS", "Table"]
    table_rows = []
    report_entries = report_data["entries"]     # The selected info
    for key, entry_info in report_entries.items():
        table_rows.append((key, entry_info["dbms_name"], entry_info["table_name"]))

    # Remove - deletes the table from the report
    # Ignore - ignores the table from this run
    extra_columns =  [('Remove','checkbox'), ('Ignore','checkbox')]
 
    al_table = AnyLogTable(report_name, list_columns, None, table_rows, extra_columns)

    select_info = get_select_menu()


    select_info['table'] = al_table
    select_info['title'] = report_name

    # select output options
    select_info['default_options_list'] = ["Min", "Max", "Avg"]    # These are flagged as selected
    select_info['more_options_list'] = ["Range", "Count"]

    # Get the list of panels to the report (if Available and suggest to replace a panel or add a panel)
    platform, panels_list = get_panels_list(user_name, report_name)

    select_info['new_panel_name'] = "Panel_%u" % (len(panels_list) + 1)   # Default name for the panel

    if panels_list and len(panels_list):
        select_info['panels_list'] = panels_list  # Add the list of existing panels in this report
    if not platform:
        # select visualization platform
        visualization = gui_view_.get_base_info("visualization") or ["Grafana"]
        platforms = []
        default_platform = None
        for entry in visualization:
            if "default" in visualization[entry] and visualization[entry]:  # look for the default platform
                default_platform = entry
            else:
                platforms.append(entry)
        if not default_platform:
            if not len(platforms):
                flash("AnyLog: Missing visualization platforms in config file: %s" % Config.GUI_VIEW)
                return redirect(url_for('index'))
            if len(platforms) == 1:
                # Only one platform
                default_platform = platforms[0]
                platforms = None
            else:
                flash("AnyLog: Define default platform in config file: %s" % Config.GUI_VIEW)
                return redirect(url_for('index'))

        select_info['default_platform'] = default_platform      # Default like: Grafana
        if platforms and len(platforms):
            select_info['platforms_list'] = platforms                # Other platforms like power BI

    select_info['report_name'] = report_name

    # Organize the report time selections as last selection
    select_info['time_options'] = time_selection_
    from_date, to_date = path_stat.get_dates_selection(user_name, report_name)      # Get the last selections of dates
    if to_date:
        if to_date == 'now':
            for entry in time_selection_:
                # go over the entries to find the last selection made and set it as default
                if entry[1] == from_date[3:]:
                    select_info['previous_range'] = (entry[0], entry[1])
        else:
            select_info['from_date'] = from_date
            select_info['to_date'] = to_date


    return render_template('report_deploy.html',  **select_info )

# -----------------------------------------------------------------------------------
# If a visualization platform was selected, get the panels from the platform
# Otherwise, search in all platforms
# -----------------------------------------------------------------------------------
def get_panels_list(user_name, report_name):

    platform_name = path_stat.get_platform_name(user_name, report_name)
    platforms_tree = gui_view_.get_base_info("visualization")
    panels_list = []
    if not platform_name:
        # Get from all platforms
        for platform_option in platforms_tree:
            if "url" in platforms_tree[platform_option] and "token" in platforms_tree[platform_option]:
                url = platforms_tree[platform_option]['url']
                token = platforms_tree[platform_option]['token']
                one_list, err_msg = visualize.get_panels(platform_option, url, token, report_name)
                if err_msg:
                    flash(err_msg, category='error')
                if one_list and len(one_list):
                    panels_list = one_list
                    platform_name = platform_option
                    path_stat.set_platform_name(user_name, report_name, platform_name)
                    break           # Platform was found
    else:
        # Platform was selected
        if platform_name in platforms_tree:
            platform_option = platforms_tree[platform_name]
            if "url" in platform_option and "token" in platform_option:
                url = platform_option['url']
                token = platform_option['token']
                panels_list, err_msg = visualize.get_panels(platform_name, url, token, report_name)
                if err_msg:
                    flash(err_msg, category='error')
    for index, entry in enumerate(panels_list):
        if entry.find(' ') != -1:
            # replace space with underline
            panels_list[index] = entry.replace(' ','_')

    return [platform_name, panels_list]

# -----------------------------------------------------------------------------------
# Processing form: report_deploy.html - Push the info to the interface
# -----------------------------------------------------------------------------------
@app.route('/deploy_report', methods={'GET','POST'})
def deploy_report():

    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session['username']

    form_info = request.form

    report_name = form_info["report_name"]

    # Remove the tables flagged as removed from the report
    for entry in form_info:
        if entry.startswith("Remove."):
            # User removes this selsction from the report
            path_stat.remove_selected_entry(user_name, report_name, entry[7:])

    # get the tables selected for the report
    tables_list = []
    report_tables = path_stat.get_report_entries(user_name, report_name)
    for key, info in report_tables.items():
        if "Ignore." + key in form_info:
            continue        # Ignore this selection in the report
        tables_list.append((info["dbms_name"], info["table_name"]))

    # Get the platform
    platform_name = path_stat.get_platform_name(user_name, report_name)
    if not platform_name:
        if "platform" not in form_info:
            flash('AnyLog: Select platform from options', category='error')
            return redirect(('/dynamic_report'))

        platform_name = form_info["platform"]    # Platform name + connect string + token
        path_stat.set_platform_name(user_name, report_name, platform_name)

    from_date, to_date, err_msg = get_time_range(form_info)
    if err_msg:
        flash(err_msg, category='error')
        return redirect(('/dynamic_report'))

    query_functions = get_query_functions(form_info)  # get min, max, count, avg

    platforms_tree = gui_view_.get_base_info("visualization")
    
    # The Info from the config file
    platform_info = copy.deepcopy( platforms_tree[platform_name])

    if 'operation' in form_info:
        operation = form_info['operation']
    else:
        operation = 'Replace'       # With new report - replces the existing panel

    platform_info['operation'] = operation

    if operation == 'Remove' or operation == 'Replace':
        if 'panel' in form_info:
            platform_info['title'] = form_info['panel'].replace('_',' ')     # Take the title from the panel select list
        else:
            platform_info['title'] = form_info['title']
    else:
        if 'title' in form_info:
            platform_info['title'] = form_info['title'] # take the title from the input field

    # add info from the report

    platform_info['from_date'] = from_date
    platform_info['to_date'] = to_date
    path_stat.set_dates_selection(user_name, report_name, from_date, to_date)   # Save the selction for next report

    platform_info['report_name'] = report_name
    platform_info['tables_list'] = tables_list
    platform_info['base_report'] = "AnyLog_Base"
    platform_info['functions'] = query_functions

    report_url, err_msg = visualize.deploy_report(platform_name, **platform_info)
    if not report_url:
        # Failed to update the report
        flash("AnyLog: Failed to deploy report to %s - Error: %s" % (platform_name, err_msg))
        return redirect(('/dynamic_report'))

    return redirect((report_url))       # Goto Grafana

# -----------------------------------------------------------------------------------
# Get the functions of the query - min, max etc.
# -----------------------------------------------------------------------------------
def get_query_functions(form_info):
    functions = []
    if "Min" in form_info:
        functions.append("min")
    if "Max" in form_info:
        functions.append("max")
    if "Avg" in form_info:
        functions.append("avg")
    if "Count" in form_info:
        functions.append("count")
    if "Range" in form_info:
        functions.append("range")

    if not len(functions):
        # set defaults
        functions = ["min","max","avg"]
    return functions

# -----------------------------------------------------------------------------------
# Get the time range from the form - select between specifying the range and predefined options.
# -----------------------------------------------------------------------------------
def get_time_range(form_info):

    err_msg = None
    from_date = None
    to_date = None
    wrong_selection = False
    if not form_info['date_range'] and form_info['start_date'] and form_info['end_date']:
        # select to dates
        from_date = form_info['start_date']
        to_date = form_info["end_date"]
        if from_date >= to_date:
            wrong_selection = True
    elif form_info['date_range'] and not form_info['start_date'] and not form_info["end_date"]:
        from_date = "now" + form_info['date_range']
        to_date = "now"
    else:
        wrong_selection = True

    if wrong_selection:
        err_msg = "AnyLog: Wrong selection for report date and time range"

    return [from_date, to_date, err_msg]
# -----------------------------------------------------------------------------------
# Reports
# -----------------------------------------------------------------------------------
@app.route('/reports')
def reports():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    select_info = get_select_menu()
    select_info['title'] = 'Reports'

    return render_template('reports.html', **select_info)
# -----------------------------------------------------------------------------------
# Alerts
# -----------------------------------------------------------------------------------
@app.route('/alerts')
def alerts():
    return redirect(('/login'))        # start with Login if not yet provided
# -----------------------------------------------------------------------------------
# Configure
# -----------------------------------------------------------------------------------
@app.route('/configure', methods = ['GET', 'POST'])
def configure():

    select_info = get_select_menu( caller = "configure")
    select_info["form"] = ConfigForm()
    select_info["title"] = 'Configure Network Connection'

    if not gui_view_.is_with_config():
        # Faild to recognize the JSON Config File
        if gui_view_.is_config_error():
            flash(gui_view_.get_config_error())

    # Test connectors to the Visualization platforms
    platforms = gui_view_.get_base_info("visualization")
    if platforms:
        for entry in platforms:
            if isinstance(platforms[entry], dict) and "url" in platforms[entry] and "token" in platforms[entry]:
                ret_val, err_msg = visualize.test_connection( entry, platforms[entry]["url"], platforms[entry]["token"] )  # Platform name + connect_string
                if not ret_val:
                    flash("AnyLog: Failed to connect to '%s' Error: '%s'" % (entry[0], err_msg))
            else:
                flash("AnyLog: Missing setup info for '%s' in config file: %s" % (entry, Config.GUI_VIEW))

    if request.method == 'POST':
        # Need to be completed
        conf = {}
        conf["node_ip"] = request.form["node_ip"]
        conf["node_port"] = request.form["node_port"]
        conf["reports_ip"] = request.form["reports_ip"]
        conf["reports_port"] = request.form["reports_ip"]
  

    select_info["title"] = 'Configure Network Connection'
    select_info["form"] = ConfigForm()         # New Form

    return render_template('configure.html', **select_info )
# -----------------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------------
@app.route('/network')
def network():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided


    target_node = get_target_node()
    
    form = CommandsForm()         # New Form
    
    select_info = get_select_menu()
    select_info['title'] = 'Network Operations'
    select_info['form'] = form
    select_info['def_dest'] = target_node


    return render_template('commands.html', **select_info)

# -----------------------------------------------------------------------------------
# AnyLog Commands
# -----------------------------------------------------------------------------------
@app.route('/al_command', methods = ['GET', 'POST'])
def al_command():

    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    al_headers = {
            'User-Agent' : 'AnyLog/1.23'
    }


    select_info = get_select_menu()
 
    target_node = get_target_node()

    command = request.form["command"]
    try:
        al_headers["command"] = command
        
        response = requests.get(target_node, headers=al_headers)
    except:
        flash('AnyLog: Network connection failed')
        return redirect(('/network'))     # Go to main page
    else:
        reply = response.text
        if response.status_code == 200:
            return print_network_reply(command, reply)
        else:
            flash("AnyLog Network: Command Reply: '%s'" % (reply))

    
    select_info['title'] = 'Network Status'
    select_info['form'] = CommandsForm()         # New Form
    select_info['def_dest'] = target_node
    
    return render_template('commands.html', **select_info)

# -----------------------------------------------------------------------------------
# Print network reply -
# Option 1 - a tree
# Option 2 - a table
# Option 3 - text
# -----------------------------------------------------------------------------------
def print_network_reply(command, data):

    select_info = get_select_menu()
    select_info['title'] = 'Network Command'
    select_info['command'] = command

    # Print Tree

    policy = None
    if data[0] == '{' and data[-1] == '}':
        policy, error_msg = json_api.string_to_json(data)

    elif data[0] == '[' and data[-1] == ']':
        policy, error_msg = json_api.string_to_list(data)

    if policy:
        # Print Tree Structure
        data_list = []
        json_api.setup_print_tree(policy, data_list)
        select_info['text'] = data_list
        # path_selection(parent_menu, id, data)      # save the path, the key and the data on the report
        return render_template('output_tree.html', **select_info)

    # Make a list of strings to print
    data = data.replace('\r', '')
    text_list = data.split('\n')


    # Print a Table
    is_table = False
    for index, entry in enumerate(text_list):
        if entry and index:
            if entry[0] == '-' and entry[-1] == '|':
                # Identified a table
                is_table = True
                columns_list = entry.split('|')
                columns_size = []
                for column in columns_list:
                    if len(column):
                        columns_size.append(len(column))     # An array with the size of each column
                header = []
                offset = 0
                for column_id, size in enumerate(columns_size):
                    header.append(text_list[index - 1][offset:offset + size])
                    offset += (size + 1)                # Add the field size and the separator (|)

                select_info['header'] = header
                if index > 1 and len(text_list[index -2]):
                    select_info['table_title'] = text_list[index -2]         # Get the title if available
                break
        if index >= 5:
            break  # not a table

    if is_table:
        # a Table setup and print
        table_rows = []
        for y in range(index + 1, len(text_list)): # Skip the dashed separator to the column titles
            row = text_list[y]

            columns = []
            offset = 0
            for column_id, size in enumerate(columns_size):
                columns.append(row[offset:offset + size])
                offset += (size + 1)  # Add the field size and the separator (|)

            table_rows.append(columns)

        select_info['rows'] = table_rows
        return render_template('output_table.html', **select_info)

    # Print Text

    print_info = []     # Every entry holds type of text ("text" or "Url) and the text string

    for entry in text_list:
        # Setup URL Link
        if entry[:6] == "Link: ":
            index = entry.rfind('#')  # try to find name of help section
            if index != -1:
                section = entry[index + 1:].replace('-', ' ')
            else:
                section = ""
            print_info.append(("url", entry[6:], section))
        else:
            print_info.append(("text", entry))

    select_info['text'] = print_info

    return render_template('output_cmd.html', **select_info)
# -----------------------------------------------------------------------------------
# Install New Node
# -----------------------------------------------------------------------------------
@app.route('/install', methods = ['GET', 'POST'])
def install():

    select_info = get_select_menu()
    select_info['title'] = 'Install Network Node'
    select_info['form'] = InstallForm()

    return render_template('install.html', **select_info)


# -----------------------------------------------------------------------------------
# Issue a report based on the list of policies IDs and the method to extract the dbms name and database name
# -----------------------------------------------------------------------------------
def policies_to_status_report( selection, policies_list ):
    '''
    Each Policy is transformed to a report showing the data status

    :param policies_list: Each entry on the list includes:
        1) DBMS Name (or method to extract the name from the policy)
        2) Table Name (or method to extract the name from the policy)
        3) Policy ID
    :return:            URL of a report using a 3rd party platform (like Grafana)
    '''

    # Make a list with the following entries:
    # Name, Table Name, DBMS name
    projection_list = []

    for entry in policies_list:
        dbms_table_id = entry.split('@')
        if len(dbms_table_id) != 3: # needs to be: BMS + Table + Policy ID
            flash('AnyLog: Missing definitions to deploy report: %s' % '.'.join(dbms_table_id), category='error')
            return None
        extract_dbms = dbms_table_id[0]  # The method to extract the dbms name from the policy
        extract_table = dbms_table_id[1]  # The method to extract the table name from the policy
        if dbms_table_id[2][-1] == "?":
            # Retrieved from a query string on the URL
            policy_id = dbms_table_id[2][:-1]
        else:
            policy_id = dbms_table_id[2]
        # Lookup on the blockchain to retrieve the policy
        retrieved = get_json_policy(policy_id)    # Remove the question mark at the end of the string
        if retrieved and len(retrieved) == 1:
            # Get returns a list of policies
            policy = retrieved[0]
            policy_name = path_stat.get_policy_value(policy, "name")
            if policy_name:
                dbms_name = path_stat.get_sql_name(policy, extract_dbms)
                if dbms_name:
                    table_name = path_stat.get_sql_name(policy, extract_table)
                    if table_name:
                        projection_list.append((policy_name, dbms_name, table_name))


    if not len (projection_list):
        flash('AnyLog: Missing metadata information in policies', category='error')
        return None

    platforms_tree = gui_view_.get_base_info("visualization")
    if not platforms_tree or not "Grafana" in platforms_tree:
        flash('AnyLog: Missing Grafana definitions in config file', category='error')
        return None

    platform_info = copy.deepcopy(platforms_tree["Grafana"])
    platform_info['base_report'] = "AnyLog_Base"

    platform_info["projection_list"] = projection_list

    platform_info['functions'] = ["min", "max", "avg"]

    platform_info['from_date'] = "-2M"
    platform_info['to_date'] = "now"

    url_list, err_msg = visualize.status_report("Grafana", **platform_info)
    if err_msg:
        flash(err_msg, category='error')
        return None

    select_info = get_select_menu()
    select_info['title'] = "Current Status"

    select_info["url_list"] = url_list

    return  render_template('output_frame.html', **select_info)

# -----------------------------------------------------------------------------------
# Navigate in the metadata
# https://flask-navigation.readthedocs.io/en/latest/
# -----------------------------------------------------------------------------------
@app.route('/metadata', methods = ['GET', 'POST'])
@app.route('/metadata/<string:selection>', methods = ['GET', 'POST'])
def metadata( selection = "" ):

    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session["username"]

    if selection:
        offset = selection.rfind('#')       # Offset to #start_location in the URL
        if offset != -1:
            location_key = selection[:offset]       # Remove the scroll location added by the JS in metadata.html
        else:
            location_key = selection
    else:
        location_key = selection

    if request.query_string:
        query_string = request.query_string.decode('ascii')
        if query_string[:7] == "report=":
            # Option 1 - User selected a report (graph) using a LINK over the edge node name
            # User selected a report on a single edge node
            dbms_table_id = query_string[7:] # DBMS + Table + Policy ID
            # Got the method to determine dbms name and table name
            html = policies_to_status_report(location_key, [dbms_table_id])
            if not html:
                # Got an error
                select_info = get_select_menu(selection=location_key)
                return call_navigation_page(user_name, select_info, location_key, None)
            return html


    form_info = request.form
    get_policy = False

    if len(form_info):
        # Selection on the navigation form

        selected_list = []
        configure_button = False
        save_button = False
        report_button = False
        # Go over report selections
        for form_key, form_val in form_info.items():
            if form_val == "View":
                # Option 2 - User selected to View a Policy (using a View BUTTON)
                # The user selected view - Bring the node Policy
                offset = form_key.rfind('+')
                if offset > 0:
                    # Get the policy ID of the last layer
                    policy_id = form_key[offset + 1:]
                    location_key = form_key
                    get_policy = True       # Get the policy of the node
                break
            if form_key[:7] == "option.":
                # User selected an option representing a metadata navigation (the type of the children to retrieve)
                # Move from metadata to data
                location_key = form_key[7:]     # Remove the "option." prefix
                break
            if form_key[:9] == "selected.":
                # Option 3 - the user selected one or multple ege node (in the CHECKBOX)
                selected_list.append(form_key[9:])
            elif form_key == "Report":
                # The selected list is used for a report
                report_button = True
            elif form_key == "Save":
                save_button = True
            elif form_key == "Configure":
                configure_button = True

        if report_button:
            html = policies_to_status_report(location_key, selected_list)
            if not html:
                # Got an error
                select_info = get_select_menu(selection=location_key)
                return call_navigation_page(user_name, select_info, location_key, None)
            return html


    if not selection:

        params = { 'is_anchor' : True }
        root_nav = nav_tree.TreeNode( **params )

        children = gui_view_.get_gui_root() # Get the list of the children at layer 1 from the config file
        for child in children:
            params = {
                'name' : child,
                'key'  : child,
                'path' : child,
            }
            root_nav.add_child( **params )

        path_stat.register_element(user_name, "root_nav", root_nav)     # Anchor the root as f(user)

        select_info = get_select_menu(selection=location_key)

        current_node = None

    else:
        root_nav = path_stat.get_element(user_name, "root_nav")

        selection_list = location_key.replace('+','@').split('@')

        # Navigate in the tree to find location of Node
        current_node = nav_tree.get_current_node(root_nav, selection_list, 0)

        gui_key = app_view.get_gui_key(location_key)  # Transform selection with data to selection of GUI keys

        if get_policy:
            # User requested ti VIEW the policy of a tree entry
            # Get the policy by the ID (or remove if the policy was retrieved)

            if current_node.is_option_node():
                # move to the data node
                policy_node = current_node.get_parent()
            else:
                policy_node = current_node
            if policy_node.is_with_policy():
                policy_node.add_policy(None)
            else:
                retrieved_policy = get_json_policy(policy_id)
                if retrieved_policy and isinstance(retrieved_policy,list) and len(retrieved_policy) == 1:
                    policy_node.add_policy(retrieved_policy[0] )
            select_info = get_select_menu(selection=gui_key)
        else:
            select_info = get_select_menu(selection=gui_key)

            if current_node.is_with_children():
                current_node.reset_children()  # Delete children from older navigation
            else:
                # Collect the children

                # Get the options from the config file and set the options as children

                gui_sub_tree = gui_view_.get_subtree(gui_key)  # Get the subtree representing the location on the config file

                if current_node.is_option_node() or app_view.is_edge_node(gui_sub_tree):        # User selected a query to the data
                    # Executes a query to select data from the network and set the data as as the children
                    reply = get_path_info(gui_key, select_info, current_node)
                    if reply:
                        # Add children to tree
                        gui_sub_tree, tables_list, list_columns, list_keys, table_rows = reply
                        if "dbms_name" in gui_sub_tree and "table_name" in gui_sub_tree:
                            # Push The key to pull dbms name and table name from the policy
                            dbms_name = gui_sub_tree["dbms_name"]
                            table_name = gui_sub_tree["table_name"]
                        else:
                            dbms_name = None
                            table_name = None

                        current_node.add_data_children(location_key, list_columns, list_keys, table_rows, dbms_name, table_name)

                else:

                    current_node.add_option_children(gui_sub_tree, location_key)


    return call_navigation_page(user_name, select_info, location_key, current_node)


# -----------------------------------------------------------------------------------
# Call the navigation page - metadata.html
# -----------------------------------------------------------------------------------
def call_navigation_page(user_name, select_info, location_key, current_node):

    print_list = []

    root_nav = path_stat.get_element(user_name, "root_nav")

    nav_tree.setup_print_list(root_nav, print_list)

    if current_node:
        # Place a flag to indicate the position n the page  when page is loaded
        # Reset is done in nav_tree.setup_print_list
        current_node.set_scroll_location()

    select_info['selection'] = location_key

    select_info['nodes_list'] = print_list

    select_info['title'] = "AnyLog Network"

    return render_template('metadata.html', **select_info)


# -----------------------------------------------------------------------------------
# Logical tree navigation
# https://hackersandslackers.com/flask-routes/
# https://www.freecodecamp.org/news/dynamic-class-definition-in-python-3e6f7d20a381/
# https://hackersandslackers.com/flask-routes/
# -----------------------------------------------------------------------------------
@app.route('/tree')
@app.route('/tree/<string:selection>')
def tree( selection = "" ):
    global query_node_
    global user_connect_
    global gui_view_

    # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))  # start with Login  if not yet provided

    select_info = get_select_menu(selection=selection)

    # Make title from the path
    title = ""
    parent_menu = select_info["parent_gui"]
    for parent in parent_menu:
        title += " [%s] " % parent[0]
    select_info['title'] = title

    reply = get_path_info(selection, select_info, None)
    if reply:
        gui_sub_tree, tables_list, list_columns, list_keys, table_rows = reply

        extra_columns =  [('Select','checkbox')]
        al_table = AnyLogTable(select_info['parent_gui'][-1][0], list_columns, list_keys, table_rows, extra_columns)

        tables_list.append(al_table)    # Add the children

        select_info['selection'] = selection
        select_info['tables_list'] = tables_list
        select_info['submit'] =  "View"

        if "dbms_name" in gui_sub_tree and "table_name" in gui_sub_tree:
            # These entries can be added to a report
            select_info['add'] =  "Add"
            select_info['dbms_name'] = gui_sub_tree["dbms_name"]
            select_info['table_name'] = gui_sub_tree["table_name"]

    return render_template('selection_table.html',  **select_info )

# -----------------------------------------------------------------------------------
# Get the path info based on the tree navigation
# There are 2 structure options to use with Tree structure:
#       a) path_stat - maintains the path from the root to the node selected
#       OR
#       b) nav_tree - a tree structure that maintains the entire tree navigation
#
# Both structures identify the node selected and pull the children nodes
# -----------------------------------------------------------------------------------
def get_path_info(selection, select_info, current_node):

    '''
    Get the children nodes from the current location

    :param selection:   The ket to the current location
    :param select_info:
    :param current_node: In the case of TREE NAVIGATION - the current node, otherwise NULL
    :return:
            gui_sub_tree:       The location (subtree) in the config file
            tables_list:        Only for Path Navigation - a list with the parents info
            list_columns:       The Column names (form the config file) - of the last level
            list_keys:          The keys of the JSON policy (from the config file) - of the last level
            table_rows:         A list with the data rows of the last level
    '''

    global user_connect_
    global gui_view_

    level = selection.count('@') + 1

    # Get the location in the Config file to set the user navigation links
    gui_sub_tree = gui_view_.get_subtree(selection)

    command = app_view.get_tree_entree(gui_sub_tree, "query")  # get the command from the Config file
    user_name = session["username"]
    if current_node:
        # Use tree Navigation
        al_command = nav_tree.update_command(current_node, selection, command)  # Update the command with the parent info
    else:
        # Use of Path Navigation
        al_command = path_stat.update_command(user_name, selection, command)  # Update the command with the parent info

    if not al_command:
        flash("AnyLog: Missing AnyLog Command in Config file: '%s' with selection: '%s'" % (str(selection)))
        return None  # Show all user select options

    # Get the columns names of the table to show
    list_columns = app_view.get_tree_entree(gui_sub_tree, "table_title")
    if not list_columns:
        flash("AnyLog: Missing column names in config file: '%s' with selection: '%s'" % (Config.GUI_VIEW, str(selection)))
        return None

    # Get the keys to pull data from the JSON reply
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    if not list_keys:
        flash("AnyLog: Missing 'list_keys' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return None # Show all user select options

    target_node = get_target_node()

    # Run the query against the Query Node

    data, error_msg = exec_al_cmd( al_command )
    if error_msg:
        flash(error_msg, category='error')
        return None

    data_list = app_view.str_to_list(data)

    if not data_list:
        flash('AnyLog: Error in data format returned from node', category='error')
        return None
    if not len(data_list):
        flash('AnyLog: AnyLog node did not return data using command: \'%s\'' % al_command, category='error')
        return None


    if "bring" in al_command:
        # Only sections of the policy retrieved - no policy type
        # The table info is pulled from the bring command setup
        policy_type = None
    else:
        # The table info is pulled from the source JSON policy
        cmd_list = al_command.split(' ', 3)
        if len(cmd_list) == 4 and cmd_list[0] == "blockchain" and cmd_list[1] == "get":
            policy_type = cmd_list[2]
        else:
            policy_type = None

    # Set the tables representing the parents:
    if current_node:
        # Use tree Navigation
        tables_list = None
        table_rows = nav_tree.get_step_from_tree(current_node, select_info['parent_gui'])  # Get the info of the current step
    else:
        # Use Path Navigation
        path_steps = path_stat.get_path_overview(user_name, level,
                                             select_info['parent_gui'])  # Get the info of the parent steps

        tables_list = []  # A list to contain all the data to print - every entry represents a pth step
        for parent in path_steps:
            parent_table = AnyLogTable(parent[0], parent[1], parent[2], parent[3], [])
            tables_list.append(parent_table)

    # Set table info to present in form
    table_rows = []
    for entry in data_list:
        columns_list = []

        for key in list_keys:
            # Validate values in reply
            if policy_type and policy_type in entry and key in entry[policy_type]:
                # Get the table data from the source Policy
                value = entry[policy_type][key]
            elif key in entry:
                # Get the table data from the json resulting from the bring
                value = entry[key]
            else:
                value = ""
            columns_list.append(str(value))

        # Set a list of table entries
        table_rows.append(columns_list)

    return [gui_sub_tree, tables_list, list_columns, list_keys, table_rows]

# -----------------------------------------------------------------------------------
# Process selected Items from a table
# Organize the selected data and place the parent info in the path as f(report)
# -----------------------------------------------------------------------------------
@app.route('/selected', methods={'GET','POST'})
@app.route('/selected/<string:selection>', methods={'GET','POST'})
def selected( selection = "" ):
    '''
    Called from selection_table.html
    '''
    global query_node_
    global user_connect_
    global gui_view_

    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    form_info = request.form

    if not selection:
        # Get that selection that is in the form
        if 'selection' in form_info:
            selection = form_info['selection']
        else:
            return redirect(url_for('index')) 

    policies = []
    for key in form_info:
        # Pull the metadata of each policy from the network
        if key[:7] == "Select.":
            policy_id = key[7:]
            retrieved_policy = get_json_policy(policy_id)
            if retrieved_policy:
                policies.append(retrieved_policy[0])

    if not len(policies):
        # Nothing was selected - redo
        flash('AnyLog: Missing entry selection', category='error')
        return redirect(url_for('tree', selection=selection)) 


    if "Status" in form_info:
        # Show rows status (using Iframe)
        return status_view(selection, form_info,  policies)

    if "Add" in form_info:
        # Add selected rows to report
        user_name = session["username"]
        dbms_name = form_info["dbms"]
        table_name = form_info["table"]
        for json_entry in policies:
            # Get the location in the Config file to get the database name and table name
            path_stat.add_entry_to_report(user_name, dbms_name, table_name, json_entry)
        return redirect(('/dynamic_report'))            # Goto delect type of report

    select_info = get_select_menu(selection=selection)

    if "Browse" in form_info:
        # Put the key of the parent in the tree
        if len(policies) > 1:
            flash('AnyLog: Only one entry can be selected for browsing', category='error')
            return redirect(url_for('tree', selection=selection))

        child_name = form_info["Browse"]
        # Update the path for the currently used report
        # Place the parent info in the path as f(report)

        path_selection(select_info['parent_gui'], policy_id, retrieved_policy[0])   # Only one policy selected

        # Move with the selected child
        return redirect(url_for('tree', selection='%s@%s' % (selection, child_name)))



    # organize JSON entries to display
    data_list = []
    json_api.setup_print_tree(policies, data_list)

    select_info['text'] = data_list

    return render_template('output_tree.html', **select_info )

# -----------------------------------------------------------------------------------
# Option View - display the Status of the selected policies using Iframe
# -----------------------------------------------------------------------------------
def status_view(selection, form_info,  policies):
    '''
    Print 2 panels for each selected item (using iframe)
    :param selection: the path in the navigation
    :param user_name: the user
    :param dbms_name: how dbms name is derived from the policies
    :param table_name: how table name is derived from the policies
    :param form_info: The selections made by the user
    :param policies: The metadata of the selected rows
    :return:
    '''
    #return  render_template('output_frame.html')

    user_name = session["username"]
    extract_dbms = form_info["dbms"]       # how dbms name is derived from the policies (based on Config file)
    extract_table = form_info["table"]     #  how table name is derived from the policies (based on Config file)

    select_info = get_select_menu(selection=selection)
    report_name = path_stat.get_report_name(user_name)   # get the report marked as default for this user

    # Make a list with the following entries:
    # Name, Table Name, DBMS name
    projection_list = []
    for entry in policies:
        entry_name = path_stat.get_policy_value(entry, "name")
        if entry_name:
            dbms_name = path_stat.get_sql_name(entry, extract_dbms)
            if dbms_name:
                table_name = path_stat.get_sql_name(entry, extract_table)
                if table_name:
                    projection_list.append((entry_name, dbms_name, table_name))

    if not len (projection_list):
        flash('AnyLog: Missing metadata information in policies', category='error')
        return redirect(url_for('tree', selection=selection))

    platforms_tree = gui_view_.get_base_info("visualization")
    if not platforms_tree or not "Grafana" in platforms_tree:
        flash('AnyLog: Missing Grafana definitions in config file', category='error')
        return redirect(url_for('tree', selection=selection))

    platform_info = copy.deepcopy(platforms_tree["Grafana"])
    platform_info['base_report'] = "AnyLog_Base"

    platform_info["projection_list"] = projection_list

    query_functions = get_query_functions(form_info)
    platform_info['functions'] = query_functions

    platform_info['from_date'] = "-2M"
    platform_info['to_date'] = "now"

    url_list, err_msg = visualize.status_report("Grafana", **platform_info)

    if err_msg:
        return err_msg

    select_info = get_select_menu()
    select_info['title'] = "Current Status"

    select_info["url_list"] = url_list

    return  render_template('output_frame.html', **select_info)

# -----------------------------------------------------------------------------------
# Show AnyLog Policy by ID
# -----------------------------------------------------------------------------------
def get_json_policy( id ):

    # Run the query against the Query Node
    if not id or not isinstance(id, str):
        flash('AnyLog: Error in Policy ID', category='error')
        return redirect(('/index'))        # Select a different path

    al_cmd = "blockchain get * where id = %s" % id
    data, error_msg = exec_al_cmd( al_cmd )

    if error_msg:
        flash('AnyLog: Error in data format returned for policy: %s' % id, category='error')
        flash('AnyLog: Error: %s' % error_msg, category='error')
        json_list = None
    else:
        json_list = app_view.str_to_list(data)

    return json_list

# -----------------------------------------------------------------------------------
# User navigation in the metadata is stored in an object assigned to the report.
# The path is the node inf as f(level).
# The process saves the path, the key and the data selected.
# -----------------------------------------------------------------------------------
def path_selection(parent_menu, policy_id, data):

    '''
    Place the parent info in the path as f(report)
    parent_menu - the details of the path
    policy_id - the ID of the JSON policy
    data - the policy JSON data
    '''

    if not 'username' in session:
        return redirect(('/login'))        # Redo the login - need a user name

    user_name = session["username"]

    # pull the keys that are used to print a summary of the data instance
    gui_sub_tree = gui_view_.get_subtree(parent_menu[-1][1][6:])
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    table_title = app_view.get_tree_entree(gui_sub_tree, "table_title")

    path_stat.update_status(user_name, parent_menu, list_keys, table_title, policy_id, data)

# -----------------------------------------------------------------------------------
# Execute a command against the AnyLog Query Node
# -----------------------------------------------------------------------------------
def exec_al_cmd( al_cmd ):
    '''
    Run the query against the Query Node
    '''

    target_node = get_target_node()


    al_headers = {
        'User-Agent' : 'AnyLog/1.23',
        'command' : al_cmd
        }

    response, error_msg = rest_api.do_get(target_node, al_headers)

    if response and response.status_code == 200:
        data = response.text
    else:
        if not error_msg:
            # No data reply
            error_msg = "AnyLog: REST command %s returned error code %u" % response.status_code
    return [data, error_msg]

# -----------------------------------------------------------------------------------
# Get the menu data based on the configuration file
# Test if configuration file is available, otherwise go to configure form
# -----------------------------------------------------------------------------------
def get_select_menu(selection = "", caller = ""):

    select_info = {}

    if not gui_view_.is_with_config():
        # Faild to recognize the JSON Config File
        flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW)
        if caller == "configure" or caller == "login":
            # The config file is not available - ignore get_select_menu
            return select_info  # return empty dictionary

        form = ConfigForm()
        return render_template('configure.html', title = 'Configure Network Connection', form = form)

    company_name = gui_view_.get_base_info("name")                 # The user name
    user_menu = gui_view_.get_base_info("url_pages")           # These are specific web pages to the user
    parent_menu, children_menu = gui_view_.get_dynamic_menu(selection)     # web pages based on the navigation

    # get the loggin name a name from the conf file
    if 'username' in session:
        user_name = session['username']
    else:
        user_name = gui_view_.get_base_info("name") or "AnyLog"

    report_name = path_stat.get_report_selected(user_name)

    if company_name:
        select_info['company_name'] =company_name
    if user_menu and len(user_menu):
        select_info['user_gui'] = user_menu
    if parent_menu and len(parent_menu):
        select_info['parent_gui'] = parent_menu
    if children_menu and len(children_menu):
        select_info['children_gui'] = children_menu
    if report_name:
        select_info['report_name'] = report_name


    return select_info
# -----------------------------------------------------------------------------------
# Get the target node from the Config Form or the Config File
# -----------------------------------------------------------------------------------
def get_target_node():

    target_node = query_node_ or gui_view_.get_base_info("query_node")
    if not target_node:
        flash("AnyLog: Missing query node connection info")
        return redirect(('/configure'))     # Get the query node info
    return target_node

# -----------------------------------------------------------------------------------
# Configure the dynamic reports
# -----------------------------------------------------------------------------------
@app.route('/configure_reports/', methods={'GET','POST'})
def configure_reports():
    '''
    View the report being used
    '''
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session['username']

    form = ConfDynamicReport()

    form_info = request.form.to_dict()
    if "submit" in form_info:   # User need to select existing report or new report
        ret_val, err_msg = path_stat.set_report(user_name, form_info)   # Configure a new report or change report setting
        if not ret_val:
            if err_msg:
                flash('AnyLog: %s' % err_msg, category='error')
        if not err_msg:
            return redirect(url_for('configure_reports')) # After handling a successful form request, redirect to the page to get a fresh state

    # Get the list of the user report to the GUI report menu
    form.report_name.choices = path_stat.get_user_reports(user_name)    # set list with report names

    select_info = get_select_menu()
    select_info['title'] = "Configure Reports"
    select_info['form'] = form

    return render_template('configure_reports.html', **select_info)

# -----------------------------------------------------------------------------------
# Update Policies based on the JSON Config file
# -----------------------------------------------------------------------------------
@app.route('/policies', methods={'GET','POST'})
@app.route('/policies/<string:policy_name>', methods={'GET','POST'})
def policies(policy_name = ""):
   

    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    select_info = get_select_menu()
    select_info['title'] = "Network Policies"
    select_info['policies'] = gui_view_.get_policies_list()  # Collect the names of the policies

    if policy_name:
        # A policy was selected
        policy = gui_view_.get_policy_info(policy_name)
        if len(request.form):
            # send policy from Form
            target_node = get_target_node()

            err_msg = anylog_api.deliver_policy(target_node, policy, request.form)
            if err_msg:
                flash('AnyLog Connector: %s' % err_msg, category='error')

        # Goto the same form again to add a new policy
        select_info['policy_name'] = policy_name
        policy = gui_view_.get_policy_info(policy_name)
        if policy:
            select_info['policy_name'] = policy_name
            policy_attr, err_msg = app_view.set_policy_form(policy_name, policy)
            if err_msg:
                flash("AnyLog: Error in %s policy declarations in config file: %s" % (policy_name, err_msg), category='error')
            else:
                select_info["policy"] = policy_attr
                return render_template('policy_add.html', **select_info)

    return render_template('policies.html', **select_info)

# -----------------------------------------------------------------------------------
# Logout
# -----------------------------------------------------------------------------------
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))