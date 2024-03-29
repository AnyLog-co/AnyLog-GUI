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

import os

from flask import render_template, flash, redirect, request, url_for, session
from flask_table import  Table, Col, LinkCol

from app import app
from app.forms import LoginForm
from app.forms import ConfigForm
from app.forms import CommandsForm
from app.forms import InstallForm
from app.forms import ConfDynamicReport
from app.forms import DashboardConfig       # Base config of a user defined report to include multiple panels
from app.forms import PanelConfig           # Base config of a user defined panel
from app.forms import TimeConfig            # Time/date selection for a report a panel

from app.entities import Item
from app.entities import AnyLogItem

from app.entities import AnyLogTable
from app.entities import AnyLogDashboard
from app.entities import get_functions      # Get the list of supported functions
from app.entities import get_functions_names      # Get the list of supported functions

from app.entities import AnyLogPanel

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
from app import utils           # Generic utils

time_selection_ = [
    ("Day & Time Selection", ""),
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
# Is user connected
# -----------------------------------------------------------------------------------
def get_user_by_session():
    '''
    Need to sattisfy 2 conditions:
    a) Registered in Flask Session
    b) Registered on oath_stat
    :return: User Name
    '''
    if 'username' in session:       # Session is a Flask object organizing the session and is setg in login
        user_name = session['username']     # Example in https://pythonbasics.org/flask-sessions/
        if user_name and not path_stat.is_user_connnected( user_name ):
            user_name  = None
    else:
        user_name = None

    return user_name
# -----------------------------------------------------------------------------------
# Get GUI_VIEW - pull the user name from the session and bring the GUI_VIEW struct from path_stat
# -----------------------------------------------------------------------------------
def get_gui_view():
    if 'username' in session:
        user_name = session['username']
        gui_view = path_stat.get_element(user_name, "gui_view")
    else:
        gui_view = None
    return gui_view
# -----------------------------------------------------------------------------------
# Determine in the config file if selection is for reports
# -----------------------------------------------------------------------------------
def is_reports(user_name, selection):
    ret_val = False
    gui_view = path_stat.get_element(user_name, "gui_view")
    if 'children' in gui_view.config_struct['gui']:
        first_children = gui_view.config_struct['gui']['children']
        if selection in first_children:
            if 'type' in first_children[selection] and first_children[selection]['type'] == 'reports':
                ret_val = True
    return ret_val

# -----------------------------------------------------------------------------------
# GUI forms
# HTML Cheat Sheet - http://www.simplehtmlguide.com/cheatsheet.php
# Example Table: https://progbook.org/shop5.html
# -----------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    return  redirect(url_for('metadata'))

# -----------------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------------
@app.route('/login', methods={'GET','POST'})
def login():
    '''
    Input login name & password, connecet to a node in the network
    and move to main page to determine GUI to use
    '''


    form = LoginForm()

    if form.validate_on_submit():

        user_name = request.form['username']
        session['username'] = user_name

        password =  request.form['password']

        encrypted_user_password = utils.encrypt_string(user_name + ':' + password)
        if not encrypted_user_password:
            flash('AnyLog: Error with user name and password', category='error')
            return redirect(('/login'))  # Redo the login


        # Register User
        path_stat.set_new_user(user_name)
        # Register user name + password for basic authentication
        path_stat.register_element(user_name, "basic auth", encrypted_user_password)


        dashboard = AnyLogDashboard()  # The default dashboard for this user
        dashboard.set_default()
        path_stat.register_element(user_name, "default_dashboard", dashboard)

        # Load the default CONFIG file

        if load_config_file("login", user_name, Config.GUI_VIEW):

            data, error_msg = exec_al_cmd("get status")
            if error_msg:
                flash(error_msg, category='error')
                return redirect(('/login'))  # Redo the login

            path_stat.set_user_connnected(user_name)

            return redirect(('/index'))     # Go to main page

    select_info = get_select_menu( caller = "login" )
    select_info['title'] = 'Sign In'
    select_info['form'] = form

    return render_template('login.html', **select_info)

# -----------------------------------------------------------------------------------
# Load config file - register the config file and the target node
# -----------------------------------------------------------------------------------
def load_config_file( caller, user_name, config_file):

    if not config_file:
        flash("AnyLog: Missing or wrong system variables: CONFIG_FOLDER and CONFIG_FILE", category='error')
        return False  # No config file - reconfigure

    path_stat.register_element(user_name, "config_file", config_file)  # Register the Config file

    gui_view = app_view.gui()  # Load the definition of the user view of the metadata from a JSON file
    err_msg = gui_view.set_gui(config_file)
    if err_msg:
        flash(err_msg, category='error')
        return False  # No config file - reconfigure

    path_stat.register_element(user_name, "gui_view", gui_view)  # Register the Config file

    # Get query node from the loaded config file
    target_node = gui_view.get_base_info("query_node")
    if not target_node:
        flash("AnyLog: Missing Query Node in config file", category='error')
        return False  # No config file - reconfigure

    path_stat.register_element(user_name, "target_node", target_node)

    return True     # No redirect


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
    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    select_info = get_select_menu()
    if not report_name:
        report_name = select_info["report_name"]

    report_data = path_stat.get_report_info(user_name, report_name)
    if not report_data or not len(report_data["entries"]):
        flash("AnyLog: Report '%s' has no selections" % report_name, category='error')
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
        gui_view = path_stat.get_element(user_name, "gui_view")
        visualization = gui_view.get_base_info("visualization") or ["Grafana"]
        platforms = []
        default_platform = None
        for entry in visualization:
            if "default" in visualization[entry] and visualization[entry]:  # look for the default platform
                default_platform = entry
            else:
                platforms.append(entry)
        if not default_platform:
            if not len(platforms):
                flash("AnyLog: Missing visualization platforms in config file: %s" % Config.GUI_VIEW, category='error')
                return redirect(url_for('index'))
            if len(platforms) == 1:
                # Only one platform
                default_platform = platforms[0]
                platforms = None
            else:
                flash("AnyLog: Define default platform in config file: %s" % Config.GUI_VIEW, category='error')
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
    gui_view = get_gui_view()
    platforms_tree = gui_view.get_base_info("visualization")
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

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

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

    gui_view = path_stat.get_element(user_name, "gui_view")
    platforms_tree = gui_view.get_base_info("visualization")
    
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
        flash("AnyLog: Failed to deploy report to %s - Error: %s" % (platform_name, err_msg), category='error')
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
    if not get_user_by_session():
        return redirect(('/login'))        # start with Login  if not yet provided

    select_info = get_select_menu()
    select_info['title'] = 'Reports'

    return render_template('reports.html', **select_info)
# -----------------------------------------------------------------------------------
# Define which of the selected nodes is to be monitored and how
# -----------------------------------------------------------------------------------
@app.route('/define_monitoring', methods = ['GET', 'POST'])
def define_monitoring():

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    gui_view = path_stat.get_element(user_name, "gui_view")
    gui_key = app_view.get_gui_key("Monitor")  # Transform selection with data to selection of GUI keys
    root_gui, gui_sub_tree = gui_view.get_subtree(gui_key)  # Get the subtree representing the location on the config file


    form_info = request.form.to_dict()

    if len(form_info):

        if "monitor_option" not in form_info:
            flash('AnyLog: Type of monitoring was not selected', category='error')
        else:
            # Get the The commands to execute
            option_id = int(form_info["monitor_option"])
            monitor_cmds = gui_sub_tree["options"][option_id]       # The list of commands to execute

            # Get the list of nodes
            nodes_selected = []
            for key, value in form_info.items():
                if key[:9] == "selected.":
                    nodes_selected.append(key[9:])

            if not len(nodes_selected):
                flash('AnyLog: Monitored nodes were not selected', category='error')
            else:
                flash('AnyLog: Commands submitted', category='message')
                # Go over the nodes
                for node in nodes_selected:
                    # For each node execute the commands
                    node_info = node.split('@') # Get node-type, node-name, node-id, node-ip, node-port
                    dest_node = "http://" + node_info[3] + ':' + node_info[4]

                    for command in monitor_cmds[1:]: # The first entry in monitor_cmds is the name on the GUI
                        data, error_msg = exec_al_cmd(command, dest_node, "POST")



    table_rows = []

    selected_nodes = path_stat.get_info_list(user_name, "monitored")

    if selected_nodes:
        for policy in selected_nodes.values():
            policy_type = path_stat.get_policy_type(policy)
            if policy_type:
                if "name" in policy[policy_type] and "id" in policy[policy_type] and "ip" in policy[policy_type] and "rest_port" in policy[policy_type]:
                    table_rows.append((policy_type, policy[policy_type]["name"], policy[policy_type]["id"], policy[policy_type]["ip"], policy[policy_type]["rest_port"]))
    else:
        table_rows = []
        flash('AnyLog: Missing selection of nodes for monitoring', category='error')

    extra_columns = [("Select", 'checkbox')]
    al_table = AnyLogTable("Select participating nodes", ["Type", "Name", "ID", "IP", "Port"], None, table_rows, extra_columns)


    monitor_options = []
    if 'options' in gui_sub_tree:
        monitored_options = gui_sub_tree['options']
        for index, option in enumerate(monitored_options):
            option_name = option[0]
            monitor_options.append((option_name, index))       # Create a list of options to monitor
    else:
        flash('AnyLog: Missing configuration options for monitoring', category='error')


    select_info = get_select_menu()
    select_info["title"] = 'Setup Monitoring'
    if al_table:
        select_info["table"] = al_table

    select_info["monitor_options"] = monitor_options

    return render_template('monitor_setup.html', **select_info)
# -----------------------------------------------------------------------------------
# Configure
# -----------------------------------------------------------------------------------
@app.route('/configure', methods = ['GET', 'POST'])
def configure():

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided


    form_info = request.form.to_dict()

    node_ip = ""
    node_port = 0
    target_node = path_stat.get_element(user_name, "target_node")

    gui_view = path_stat.get_element(user_name, "gui_view")
    if (len(form_info)):

        # Change config file
        if "conf_file_name" in form_info:
            new_file = form_info["conf_file_name"] + ".json"
            config_file = Config.CONFIG_FOLDER + new_file         # New config file
            if not load_config_file("configire", user_name, config_file):
                flash('AnyLog: failed to load config file: \'%s\'' % new_file, category='error')
            else:
                target_node = path_stat.get_element(user_name, "target_node")   # get the target node after the load
                flash('AnyLog: New config file: \'%s\'' % new_file, category='message')
        elif "node_ip" in form_info and "node_port" in form_info:
            # Change target node
            node_ip_str = form_info["node_ip"]
            node_port_str = form_info["node_port"]
            target_node = "http://" + node_ip_str + ":" + node_port_str


    if target_node and len(target_node) > 7:
        # Set the default IP and port
        ip_port = target_node[7:].split(':')
        if len(ip_port) == 2 and ip_port[1].isdigit():
            node_ip = ip_port[0]
            node_port = int(ip_port[1])

    if not node_ip or not node_port:
        flash('AnyLog: IP:Port of query node is not properly provided', category='error')
    else:
        path_stat.register_element(user_name, "target_node", target_node)
        data, error_msg = exec_al_cmd("get status")
        if error_msg:
            flash('AnyLog: No network connection', category='error')
            flash(error_msg, category='error')

    form = ConfigForm()

    # Get the list of the config files
    config_dir = Config.CONFIG_FOLDER
    try:
        file_list = os.listdir(config_dir)
    except:
        flash('AnyLog: No config files in: %s' % config_dir, category='error')
        file_list = []

    # Keep the .json files
    config_files = []
    for entry in file_list:
        if len(entry) > 5 and entry[-5:] == ".json":
            value = entry[:-5]
            config_files.append(value)

    if len(config_files):
        form.conf_file_name.choices = config_files  # set list with report names
    else:
        flash('AnyLog: No config files in: %s' % config_dir, category='error')

    select_info = get_select_menu( caller = "configure")
    select_info["form"] = form
    select_info["title"] = 'Configure Network Connection'

    select_info["target_ip"] = node_ip
    select_info["target_port"] = node_port

    # Test connectors to the Visualization platforms
    platforms = gui_view.get_base_info("visualization")
    if platforms:
        for entry in platforms:
            if isinstance(platforms[entry], dict) and "url" in platforms[entry] and "token" in platforms[entry]:
                ret_val, err_msg = visualize.test_connection( entry, platforms[entry]["url"], platforms[entry]["token"] )  # Platform name + connect_string
                if not ret_val:
                    flash("AnyLog: Failed to connect to '%s' Error: '%s'" % (entry, err_msg), category='error')
            else:
                flash("AnyLog: Missing setup info for '%s' in config file: %s" % (entry, Config.GUI_VIEW), category='error')


    return render_template('configure.html', **select_info )
# -----------------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------------
@app.route('/network')
def network():

    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    target_node = path_stat.get_element(user_name,"target_node")
    
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

    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    al_headers = {
            'User-Agent' : 'AnyLog/1.23'
    }


    select_info = get_select_menu()
 
    target_node = path_stat.get_element(user_name,"target_node")

    command = request.form["command"]
    try:
        al_headers["command"] = command
        
        response = requests.get(target_node, headers=al_headers)
    except:
        flash('AnyLog: Network connection failed', category='error')
        return redirect(('/network'))     # Go to main page
    else:
        reply = response.text
        if response.status_code == 200:
            return print_network_reply(command, reply)
        else:
            flash("AnyLog Network: Command Reply: '%s'" % (reply), category='error')

    
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

    policy, table_info, print_info, error_msg = format_message_reply(data)
    if policy:
        # Reply was a JSON policy
        data_list = []
        json_api.setup_print_tree(policy, data_list)
        select_info['text'] = data_list
        # path_selection(parent_menu, id, data)      # save the path, the key and the data on the report
        return render_template('output_tree.html', **select_info)

    if table_info:
        # Reply is structured as a table
        if 'header' in table_info:
            select_info['header'] = table_info['header']
        if 'table_title' in table_info:
            select_info['table_title'] = table_info['table_title']
        if 'rows' in table_info:
            select_info['rows'] = table_info['rows']
        return render_template('output_table.html', **select_info)

    select_info['text'] = print_info        # Only TEXT

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
# The status report is 2 panels - a graph and a gauge which are defined in template base_conf_report.html
# -----------------------------------------------------------------------------------
def policies_to_status_report( user_name, policies_list ):
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

    dashboard = path_stat.get_element(user_name, "default_dashboard")  # An object with panels definitions
    dashboard.reset_panels()        # Remove previously defined panels
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

                        # Add the projection list to each of the 2 default panels (Graph and Gauge)
                        if dashboard.with_selections(policy_name, "graph"):
                            dashboard.add_projection_list(policy_name + '- Operation', "graph", policy_name, dbms_name, table_name, None, None, None)
                        if dashboard.with_selections(policy_name, "gauge"):
                            dashboard.add_projection_list(policy_name + '- Status', "gauge", policy_name, dbms_name, table_name, None, "period", None)


    if not dashboard.get_panels_count():
        flash('AnyLog: Missing metadata information in policies', category='error')
        return None


    gui_view = get_gui_view()
    platforms_tree = gui_view.get_base_info("visualization")
    if not platforms_tree or not "Grafana" in platforms_tree:
        flash('AnyLog: Missing Grafana definitions in config file', category='error')
        return None

    network_name = gui_view.get_base_info("name")
    root_folder = "AnyLog_" + network_name

    platform_info = copy.deepcopy(platforms_tree["Grafana"])
    platform_info['base_report'] = "AnyLog_Base"
    platform_info["folder"] = root_folder

    platform_info["dashboard"] = dashboard

    url_list, err_msg = visualize.new_report("Grafana", **platform_info)
    if err_msg:
        flash(err_msg, category='error')
        return None

    return url_list
# -----------------------------------------------------------------------------------
# Configure the Navigation Report - the report created from metadata.html
# Calls - base_conf_report
# -----------------------------------------------------------------------------------
@app.route('/conf_nav_report', methods = ['GET', 'POST'])
def conf_nav_report():

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    form_info = request.form
    if len(form_info):
        err_msg = get_base_report_config(user_name, form_info)    # update the report configuration (on the user status)
        if err_msg:
            flash("AnyLog: %s" % err_msg, category='error')
            redirect(url_for('conf_nav_report'))        # Redo Form
        flash("AnyLog: Report configured", category='message')

    select_info = get_select_menu()

    select_info['title'] = "Configure Report"

    # define config params

    dashboard_conf = DashboardConfig()

    default_dashboard = path_stat.get_element(user_name, 'default_dashboard')

    functions_list = get_functions()

    functions_selected = default_dashboard.get_default_functions("graph")
    panel_config = PanelConfig( "Graph", "graph", functions_list, functions_selected )
    dashboard_conf.add_panel(panel_config)

    functions_selected = default_dashboard.get_default_functions("gauge")
    panel_config = PanelConfig( "Gauge", "gauge", functions_list, functions_selected )
    dashboard_conf.add_panel(panel_config)

    # Organize the report time selections as last selection

    # Get the last selection for time and date and provide the selection as the setup

    start_date_time, end_date_time, range_date_time = default_dashboard.date_time.get_date_time_selections()

    text_selected = None
    time_selected = None
    if range_date_time:
        for entry in time_selection_:
                # go over the entries to find the last selection made and set it as default
                if entry[1] == range_date_time:
                    text_selected = entry[0]
                    time_selected = entry[1]
                    break


    time_config = TimeConfig(time_selection_, text_selected, time_selected, start_date_time, end_date_time)

    dashboard_conf.set_time(time_config)  # Apply time selections options to the report

    select_info['dashboard'] = dashboard_conf

    return render_template('base_conf_report.html', **select_info)


# -----------------------------------------------------------------------------------
# Get the report config info from the form
# Set the info on the default_dashboard assigned to the user
# -----------------------------------------------------------------------------------
def get_base_report_config(user_name, form_info):

    dashboard = path_stat.get_element(user_name, "default_dashboard")       # An object to include all dashboards declared on the form
    dashboard.reset()
    dashboard.set_default_name()    # The default name is "Current Status"

    for key, value in form_info.items():

        if key[:9] == "checkbox.":
            checkbox = key.split('.')   # get the panel id and the function (Min, Max etc)
            if len(checkbox) == 3:
                panel_id = checkbox[1]
                function = checkbox[2]
                dashboard.add_default_function(panel_id, function)  # add function to the dashboard (and create a panel in the dashboard if needed)

        elif key[:5] == "date_":
            dashboard.set_date_time(key[5:], value) # Set date start, date end, date range

    selection_errors = dashboard.test_selections()

    return selection_errors

# -----------------------------------------------------------------------------------
# Analyze the form returned info
# Returns form_selections - showing buttons selected
# Selected list - showing a list of sensors selected
# -----------------------------------------------------------------------------------
def process_tree_form():

    form_selections = {
        "policy_id" : None,         # AN ID of a JSON policy
        "location_key": None,       # Replace the user selection with the location key
        "get_policy": False,        # Show the JSON policy (View button)
        "report_button": False,     # Show a report of multiple selections (Report button)
        "select_button": False,     # Add the database and table of an edge node to a list that is used when a new report is defined
        "url" : None,               # URL to redirect  the process (For example to configure a report)
        "add_report" : False,       # Define a new report in the report section
        "add_folder" : False,        # Add a new Grafana Folder
        "rename_folder": False,
        "delete_folder" : False,
        "folder_name" : None,
        "status_report" : False,    # A report determined dynamically by the navigation
        "existing_report" : False,   # A predefined report
        "delete_dashboard" : False,
        "dashboard_name" : None,
        "rename_dashboard" : False,
        "nodes_selected" : False,       # User selection of nodes
        "monitor"   : None,         # Name of topic to monitor
    }

    selected_list = []


    # Go over report selections

    form_info = request.form
    if len(form_info):
        for form_key, form_val in form_info.items():
            if form_val == "View":
                #  User selected to View a Policy (using a View BUTTON)
                #  The user selected view - Bring the node Policy
                offset = form_key.rfind('+')
                if offset > 0:
                    # Get the policy ID of the last layer
                    form_selections["policy_id"] = form_key[offset + 1:]
                    form_selections["location_key"] = form_key
                    form_selections["get_policy"] = True    # Get the policy of the node
                break
            if form_val == "Rename":
                # Rename a folder
                if "new_name" in form_info and len(form_info["new_name"]):
                    if form_key[:7] == "folder.":
                        new_folder_name = form_info["new_name"]
                        old_folder_name = form_key[7:]
                        form_selections["rename_folder"] = True
                        form_selections["new_folder_name"] = new_folder_name
                        form_selections["old_folder_name"] = old_folder_name
                        break
                    if form_key[:10] == "dashboard.":
                        new_dashboard_name = form_info["new_name"]
                        old_dashboard_name = form_key[10:]
                        form_selections["rename_dashboard"] = True
                        form_selections["new_dashboard_name"] = new_dashboard_name
                        form_selections["old_dashboard_name"] = old_dashboard_name
                        break
            if form_val == "Delete":
                if "delete_confirmed" in form_info and form_info["delete_confirmed"] == 'true':
                    # Delete folder
                    if form_key[:7] == "folder.":
                        form_selections["delete_folder"] = True
                        form_selections["folder_name"] = form_key[7:]
                        break
                    if form_key[:10] == "dashboard.":
                        # delete dashboard
                        form_selections["delete_dashboard"] = True
                        form_selections["dashboard_name"] = form_key[10:]

            if form_key[:7] == "option.":
                # User selected an option representing a metadata navigation (the type of the children to retrieve)
                # Move from metadata to data
                key = form_key[7:]
                if len(key) > 11:
                    if key[-11:] == "@Add_Report":
                        form_selections["add_report"] = True
                        key = key[:-11]
                    elif key[-11:] == "@Add_Folder":
                        form_selections["add_folder"] = True
                        key = key[:-11]

                form_selections["location_key"] = key  # Save the location key based on the user button selection
                break
            if form_key[:9] == "selected.":
                # the user selected one or mulitple ege node (in the CHECKBOX)
                if form_key[9:15] == "table.":
                    # The path determines the report (Current status report processed in - policies_to_status_report
                    selected_list.append(form_key[15:])
                    form_selections["status_report"] = True
                elif form_key[9:13] == "url.":
                    # Entries represent existing reports
                    selected_list.append(form_key[13:])
                    form_selections["existing_report"] = True
                elif form_key[9:14] == "node.":
                    # Entries represent nodes selected
                    selected_list.append(form_key[14:])
                    form_selections["nodes_selected"] = True
            elif form_val == "Open":
                # The selected list is used for a report
                form_selections["report_button"] = True
            elif form_val == "Select":
                form_selections["select_button"] = True
                if form_key[:8] == "Network ":
                    index = form_key.find('.',8)
                    if index != -1:
                        topic = form_key[8:index]
                        form_selections["monitor"] = topic      # The monitoring topic (text after "Network")
            elif form_val == "Config":
                # Configure the dynamic report
                form_selections["url"] = url_for('conf_nav_report')
                break

    return [form_selections, selected_list]

# -----------------------------------------------------------------------------------
# Define new report called from new_report.html
# -----------------------------------------------------------------------------------
@app.route('/new_report', methods = ['GET', 'POST'])
@app.route('/new_report/<string:selection>', methods = ['GET', 'POST'])
def new_report( selection = "" ):

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    form_info = request.form

    if len(form_info):
        dashboard = AnyLogDashboard()  # Create a new dasboard
        tables_info = {}
        panels_names = {}   # organize the name of each panel as f(dbms + table)
        for entry in form_info:

            # Make a list with the following entries:
            # dbms name + Table Name + panel name + list of functions

            if entry[:5] == "date_":
                # Set the date- time selections
                dashboard.set_date_time(entry[5:], form_info[entry])  # Set date start, date end, date range

            elif entry[:6] == "table.":
                table_info = entry[6:].split('.')   # List with DBMS name, Table name, function
                dbms_name = table_info[0]
                table_name = table_info[1]
                panel_name = table_info[2]
                function = table_info[3]

                # Test if entry exists - if so add the function
                key = dbms_name + '.' + table_name
                if key in tables_info:
                    # add the function
                    if function == "Panel Name":
                        panel_name = form_info[entry]
                        if panel_name:
                            panels_names[key] = panel_name
                    else:
                        tables_info[key][3].append(function)
                else:
                    # add new entry
                    tables_info[key] = (dbms_name, table_name, panel_name, [function])
            elif entry == 'report_name':
                dashboard.set_name(form_info[entry])

        for entry in tables_info.values():
            # Add the projection list for each table
            key =  entry[0] + '.' + entry[1]
            if key in panels_names:
                panel_name = panels_names[key]      # User provided a name for the panel
            else:
                panel_name = dashboard.get_name()               # Use dashboard name
            dashboard.add_projection_list(panel_name, "graph", entry[2], entry[0], entry[1], entry[3], "increments", None)

        gui_view = get_gui_view()
        platforms_tree = gui_view.get_base_info("visualization")
        if not platforms_tree or not "Grafana" in platforms_tree:
            flash('AnyLog: Missing Grafana definitions in config file', category='error')
            return redirect(url_for('new_report', selection=selection))

        platform, url, token, folder = get_report_info(user_name, selection)
        platform_info = copy.deepcopy(platforms_tree[platform])
        platform_info['base_report'] = "AnyLog_Base"

        platform_info["dashboard"] = dashboard

        platform_info["folder"] = folder

        ret_val, err_msg = visualize.create_report(platform, **platform_info)
        if not ret_val:
            flash(err_msg, category='error')
            return redirect(url_for('new_report', selection=selection))

    return define_new_report(user_name, selection)
# -----------------------------------------------------------------------------------
# Define new report in the requested folder
# -----------------------------------------------------------------------------------
def define_new_report(user_name, folder):

    select_info = get_select_menu(selection=folder)

    dashboard_conf = DashboardConfig()

    default_dashboard = path_stat.get_element(user_name, 'default_dashboard')


    # Get the Report Type - Graph or Gauge
    visualize_selected = ["Grapg", "Gauge"]
    panel_config = PanelConfig( "Select visualization", "visualize", ["Graph", "Gauge"], ["Graph"] )
    dashboard_conf.add_panel(panel_config)

    # Organize the report time selections as last selection

    # Get the last selection for time and date and provide the selection as the setup

    start_date_time, end_date_time, range_date_time = default_dashboard.date_time.get_date_time_selections()

    text_selected = None
    time_selected = None
    if range_date_time:
        for entry in time_selection_:
                # go over the entries to find the last selection made and set it as default
                if entry[1] == range_date_time:
                    text_selected = entry[0]
                    time_selected = entry[1]
                    break


    time_config = TimeConfig(time_selection_, text_selected, time_selected, start_date_time, end_date_time)

    dashboard_conf.set_time(time_config)  # Apply time selections options to the report

    table_rows = path_stat.get_table_with_selected_nodes(user_name, ["name", "id"], True, True)

    tables_list = []
    extra_columns = []
    options = get_functions_names()
    for option in options:
        extra_columns.append( (option,'checkbox' ))

    extra_columns.append( ("Panel Name", 'text'))

    al_table = AnyLogTable("Select report data", ["Name", "ID", "DBMS", "Table"], None, table_rows, extra_columns)

    tables_list.append(al_table)  # Add the children

    select_info['title'] = "New Report"
    select_info['selection'] = folder
    select_info['tables_list'] = tables_list

    select_info['dashboard'] = dashboard_conf


    return render_template('new_report.html', **select_info)


# -----------------------------------------------------------------------------------
# Add new child folder for reports
# -----------------------------------------------------------------------------------
def add_folder(user_name, location_key):


    platform, url, token, parent_folder = get_report_info(user_name, location_key)

    err_msg = visualize.create_folder(platform, url, token, parent_folder, "New Folder")
    if err_msg:
        flash(err_msg, category='error')

# -----------------------------------------------------------------------------------
# Add new child folder for reports
# -----------------------------------------------------------------------------------
def rename_folder(user_name, location_key, old_folder, new_folder):

    platform, url, token, source_folder = get_report_info(user_name, old_folder)

    index = source_folder.rfind('@')
    dest_folder = source_folder[:index +1] + new_folder

    err_msg = visualize.rename_folder(platform, url, token, source_folder, dest_folder)
    if err_msg:
        flash(err_msg, category='error')
# -----------------------------------------------------------------------------------
# Delete a folder
# -----------------------------------------------------------------------------------
def delete_folder(user_name, location_key, folder_name):

    platform, url, token, target_folder = get_report_info(user_name, folder_name)

    err_msg = visualize.delete_folder(platform, url, token, target_folder)
    if err_msg:
        flash(err_msg, category='error')

# -----------------------------------------------------------------------------------
# Delete a dashboard
# -----------------------------------------------------------------------------------
def delete_dashboard(user_name, location_key, dashboard_name):

    platform, url, token, target_folder = get_report_info(user_name, location_key)

    index = dashboard_name.rfind('@')
    if index != -1:
        dashboard = dashboard_name[index + 1:]  # Name without folder
    else:
        dashboard = dashboard_name
    err_msg = visualize.delete_dashboard(platform, url, token, target_folder, dashboard)
    if err_msg:
        flash(err_msg, category='error')

# -----------------------------------------------------------------------------------
# Rename a dashboard
# -----------------------------------------------------------------------------------
def rename_dashboard(user_name, location_key, dashboard_name, new_name):

    platform, url, token, target_folder = get_report_info(user_name, location_key)

    index = dashboard_name.rfind('@')
    if index != -1:
        dashboard = dashboard_name[index + 1:]  # Name without folder
    else:
        dashboard = dashboard_name
    err_msg = visualize.rename_dashboard(platform, url, token, target_folder, dashboard, new_name)
    if err_msg:
        flash(err_msg, category='error')

# -----------------------------------------------------------------------------------
# Navigate in the metadata
# https://flask-navigation.readthedocs.io/en/latest/
# -----------------------------------------------------------------------------------
@app.route('/metadata', methods = ['GET', 'POST'])
@app.route('/metadata/<string:selection>', methods = ['GET', 'POST'])
def metadata( selection = "" ):

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    location_key = selection

    form_selections, selected_list = process_tree_form()

    if form_selections["url"]:
        return redirect(form_selections["url"])       # Redirect to a different proocess

    if form_selections["location_key"]:
        location_key = form_selections["location_key"]  # Form selection changed the location

    if form_selections["add_report"]:
        return define_new_report(user_name, location_key)

    if form_selections["add_folder"]:
        # Continue to print tree  with new folder
        add_folder(user_name, location_key)
    elif form_selections["rename_folder"]:
        rename_folder(user_name, location_key, form_selections["old_folder_name"], form_selections["new_folder_name"])
    elif form_selections["delete_folder"]:
        delete_folder(user_name, location_key, form_selections["folder_name"])
    elif form_selections["delete_dashboard"]:
        delete_dashboard(user_name, location_key, form_selections["dashboard_name"])
    elif form_selections["rename_dashboard"]:
        rename_dashboard(user_name, location_key, form_selections["old_dashboard_name"], form_selections["new_dashboard_name"])
    elif form_selections["report_button"]:    # Report Open Selection
        if form_selections["status_report"]:
            # Show the default report with the selected edge nodes
            url_list = policies_to_status_report(user_name, selected_list)
        elif form_selections["existing_report"]:
            urls_compressed = selected_list            # List of selected URLs
            url_list = []
            for url_encoded in urls_compressed:
                url_list += uncompress_urls(url_encoded)    # Uncompress mutiple pannels that are represented as a single string
        else:
            url_list = None
        if not url_list:
            # Got an error
            select_info = get_select_menu(selection=location_key)
            return call_navigation_page(user_name, select_info, location_key, None)
        select_info = get_select_menu()
        select_info['title'] = "Selected Reports"
        select_info["url_list"] = url_list

        return render_template('output_frame.html', **select_info)

    if form_selections["monitor"]:
        topic = form_selections["monitor"]
        return monitor_topic(topic)

    if location_key:
        index = location_key.find('@')
        if index != -1:
            key = location_key[:index]
        else:
            key = location_key

        if is_reports(user_name, key):

            # Navigate in reports
            return navigate_in_reports(user_name, location_key, form_selections["add_folder"], form_selections["rename_folder"], form_selections["delete_folder"], form_selections["delete_dashboard"])


    if request.query_string:
        query_string = request.query_string.decode('ascii')
        if query_string[:7] == "report=":
            # Option 1 - User selected a report (graph) using a LINK over the edge node name
            # User selected a report on a single edge node
            dbms_table_id = query_string[7:] # DBMS + Table + Policy ID
            # Got the method to determine dbms name and table name
            url_list = policies_to_status_report(user_name, [dbms_table_id])
            if not url_list:
                # Got an error
                select_info = get_select_menu(selection=location_key)
                return call_navigation_page(user_name, select_info, location_key, None)

            select_info = get_select_menu()
            select_info['title'] = "Current Status"

            select_info["url_list"] = url_list

            return render_template('output_frame.html', **select_info)



    if form_selections["select_button"]:
        if len(selected_list):
            if form_selections["nodes_selected"]:
                # Monitor selected nodes
                add_selected_to_nodes_list(user_name, location_key, selected_list)
            else:
                # Report on data noides - Add the selected (edge) nodes to a list of nodes for a report
                add_selected_to_report_list(user_name, location_key, selected_list) # Return one selection from the list
        # Continue to show tree


    return metada_navigation(user_name, location_key, form_selections)

# -----------------------------------------------------------------------------------
# Add the selected nodes to a list of nodes that are option for monitoring

# -----------------------------------------------------------------------------------
def add_selected_to_nodes_list(user_name, location_key, new_selection):

    '''
    Every entry in new_selection includes:
    a) Node Name
    b) Node ID
    Get the policy using the ID and save in a list called "monitored"
    '''

    # Add the next selection to existing selection
    for entry in new_selection:
        node_segments = entry.split('.')
        if len(node_segments) == 2:
            policy_id = node_segments[1]

            if not path_stat.is_in_info_list(user_name, "monitored", policy_id):
                # Not in the list - add info to the list of selected nodes
                policy_list = get_json_policy(policy_id)
                if policy_list and isinstance(policy_list,list) and len(policy_list) == 1:
                    policy = policy_list[0]
                    # Add the selected policy to the list of nodes that can be monitored
                    path_stat.add_to_info_list(user_name, "monitored", policy_id, policy)


# -----------------------------------------------------------------------------------
# Add the selected nodes to a list of nodes that are option for a new report.
# If a new report is selected, the user can select which edge nodes to include.
# The edge nodes determine the database and table to use.
# -----------------------------------------------------------------------------------
def add_selected_to_report_list(user_name, location_key, new_selection):

    '''
    Every entry in new_selection includes:
    a) dbms name (or pull instructions for the dbms name)
    b) table name (or pull instructions for the table name)
    c) JSON policy ID
    '''

    # Add the next selection to existing selection
    for entry in new_selection:
        node_segments = entry.split('@')
        if len(node_segments) == 3:
            policy_id = node_segments[2]
            if not path_stat.is_node_selected(user_name, policy_id):
                # Not in the list - add info to the list of selected nodes

                policy_list = get_json_policy(policy_id)
                policy_id = None  # Missing ID for the policy
                if policy_list and isinstance(policy_list,list) and len(policy_list) == 1:
                    policy = policy_list[0]
                    policy_type = path_stat.get_policy_type(policy)
                    if policy_type:
                        if "id" in policy[policy_type]:
                            policy_id = policy[policy_type]["id"]

                if policy_id:
                    # Copy the path anf pathe elements to the list of selected items to print
                    node_info = {}
                    dbms_name = node_segments[0]
                    table_name = node_segments[1]

                    db_name = path_stat.get_sql_name(policy, dbms_name)  # Pull the dbms name from the policy
                    tb_name = path_stat.get_sql_name(policy, table_name)  # Pull the dbms name from the policy

                    node_info["dbms_name"] = db_name
                    node_info["table_name"] = tb_name
                    node_info["policy"] = policy

                    path_stat.add_selected_node(user_name, policy_id, node_info)        # Add the node info to the report

# -----------------------------------------------------------------------------------
# Navigate using the metadata
# -----------------------------------------------------------------------------------
def metada_navigation(user_name, location_key, form_selections):


    gui_view = path_stat.get_element(user_name, "gui_view")
    if not location_key:

        params = { 'is_anchor' : True }
        root_nav = nav_tree.TreeNode( **params )

        children = gui_view.get_gui_root() # Get the list of the children at layer 1 from the config file
        for child in children:
            params = {
                'name' : child,
                'key'  : child,
                'path' : child,
            }
            if "icon" in children[child]:
                params['icon'] = children[child]['icon']    # Icon shape size and color to show on the nav tree

            root_nav.add_child( **params )

        path_stat.register_element(user_name, "root_nav", root_nav)     # Anchor the root as f(user)

        select_info = get_select_menu(selection=location_key)

        current_node = None

    else:
        root_nav = path_stat.get_element(user_name, "root_nav")

        selection_list = location_key.replace('+','@').split('@')

        # Navigate in the tree to find location of Node
        current_node = nav_tree.get_current_node(root_nav, selection_list, 0)
        if not current_node:
            flash("AnyLog: Navigation failed", category='error')
            location_key = set_location_on_parent(location_key)
            return redirect(url_for('metadata', selection=location_key))

        gui_key = app_view.get_gui_key(location_key)  # Transform selection with data to selection of GUI keys
        select_info = get_select_menu(selection=gui_key)

        if form_selections["get_policy"]:
            # User requested to VIEW the policy of a tree entry
            # Get the policy by the ID (or remove if the policy was retrieved)
            add_policy(current_node, form_selections["policy_id"])

        elif current_node.is_monitoring_node():
            # This is a node that monitors the network using "get monitored" command
            if current_node.is_with_json():
                current_node.reset_json_struct()     # Remove the child JSON struct
            else:
                index = location_key.find("Network ")
                if index != -1:
                    topic = location_key[index + 8:]
                    json_struct = get_monitored_info(topic)
                    if json_struct:
                        current_node.add_json_struct(json_struct)

        elif current_node.is_network_cmd():
            # Execute the network command
            root_gui, gui_sub_tree = gui_view.get_subtree(gui_key)  # Get the subtree representing the location on the config file/
            if gui_sub_tree and isinstance(gui_sub_tree, dict) and "command" in gui_sub_tree:
                if current_node.is_with_json():
                    current_node.reset_json_struct()     # Remove the child JSON struct
                elif current_node.is_with_data():
                    current_node.reset_data_struct()  # Remove the data structure assigned to the node
                elif current_node.is_with_table():
                    current_node.reset_table_struct()
                else:
                    err_msg = add_command_reply(current_node, gui_sub_tree['command'])
                    if err_msg:
                        flash("AnyLog: Network command failed: %s" % err_msg,  category='error')
                        current_node.parent.reset_children()
                        location_key = set_location_on_parent(location_key)
                        return redirect(url_for('metadata', selection=location_key))
            else:
                flash("AnyLog: Missing command in Monitor Nodes", category='error')
                current_node.parent.reset_children()
                location_key = set_location_on_parent(location_key)
                return redirect(url_for('metadata', selection=location_key))

        else:

            if current_node.is_with_children():
                current_node.reset_children()  # Delete children from older navigation
            else:
                # Collect the children

                # Get the options from the config file and set the options as children

                root_gui, gui_sub_tree = gui_view.get_subtree(gui_key)  # Get the subtree representing the location on the config file


                if current_node.is_option_node() or app_view.is_edge_node(gui_sub_tree) or (current_node.is_root() and "query" in gui_sub_tree):
                    # A node that allows a query to the data or a query to the blockchain
                    # Executes a query to select data from the network (data or metadata/blockchain) and set the data as as the children
                    reply = get_path_info(gui_key, select_info, current_node)

                    if reply:
                        # Add children to tree
                        gui_sub_tree, tables_list, list_columns, list_keys, table_rows = reply

                        # Manage data
                        if "dbms_name" in gui_sub_tree and "table_name" in gui_sub_tree:
                            # Push The key to pull dbms name and table name from the policy
                            dbms_name = gui_sub_tree["dbms_name"]
                            table_name = gui_sub_tree["table_name"]
                            add_checkbox = True         # Checkbox to select nodes
                        elif "submit" in gui_sub_tree:
                            add_checkbox = True
                            dbms_name = None
                            table_name = None
                        else:
                            add_checkbox = False
                            dbms_name = None
                            table_name = None

                        current_node.add_data_children(location_key, list_columns, list_keys, table_rows, add_checkbox, dbms_name, table_name)

                else:

                    current_node.add_option_children(gui_sub_tree, location_key)

                    if location_key == "Monitor":
                        add_monitored_topics(current_node)


    return call_navigation_page(user_name, select_info, location_key, current_node)

# -----------------------------------------------------------------------------------
# For Topic in the navigation tree, get the list of monitored topics on the connected node.
# Provide each monitored topic as a child
# -----------------------------------------------------------------------------------
def add_monitored_topics(current_node):

    # get the list of monitored topics

    topics_string, error_msg = exec_al_cmd("get monitored")
    if not error_msg and len(topics_string):
        try:
            topics_list = eval(topics_string)
        except:
            topics_list = None
        else:
            for topic in topics_list:
                # Add each topic as a child
                node_name = "Network %s" % topic
                path = "Monitor@"  + node_name
                icon = ("fas fa-wifi", 16, "#4b7799" )
                submit_buttons = ["Select"]
                current_node.add_child(name=node_name, icon=icon, path = path, monitor=True, submit_buttons = submit_buttons)

# -----------------------------------------------------------------------------------
# Get network info using "get monitored" command
# -----------------------------------------------------------------------------------
def get_monitored_info(topic):

    json_struct = None
    al_cmd = "get monitored %s" % topic
    monitored_info, error_msg = exec_al_cmd(al_cmd)
    if error_msg:
        flash("AnyLog: Network command: '%s' returned error:  %s" % (al_cmd, error_msg), category='error')
    elif len(monitored_info):
        try:
            json_struct = eval(monitored_info)
        except:
            flash("AnyLog: Error in monitored data for topic %s" % topic, category='error')


    return json_struct

# -----------------------------------------------------------------------------------
# Monitor a topic
# -----------------------------------------------------------------------------------
@app.route('/monitor_topic', methods = {'GET','POST'})
@app.route('/monitor_topic/<string:topic>', methods = {'GET','POST'})
def monitor_topic( topic = "" ):


    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # Redo the login - need a user name

    gui_view = path_stat.get_element(user_name, "gui_view")
    gui_sub_tree = gui_view.get_sub_tree(["gui","children","Monitor","Views", topic])

    json_struct = get_monitored_info(topic)

    select_info = get_select_menu()
    select_info['title'] = "Monitored %s" % topic
    select_info['topic'] = topic

    if json_struct:
        # Transform the JSON to a table
        table_data = {}
        table_rows = []
        column_names_list = []
        totals = None
        alerts = None
        if gui_sub_tree:
            if 'header' in gui_sub_tree:
                # User specified (in config file) columns to display
                column_names_list = gui_sub_tree['header']
                select_info['header'] = column_names_list
            if 'totals' in gui_sub_tree:
                totals = gui_sub_tree['totals']
            if 'alerts' in gui_sub_tree:
                alerts = gui_sub_tree['alerts']           # Test values as arrive

        if not len(column_names_list):
            # Get the columns names from the JSON data
            column_names_list.append("Node")
            # take all columns from the json
            for node_name, node_info in  json_struct.items():
                # Key is the node name and value is the second tier dictionary with the info
                for attr_name in node_info:
                    # The keys are the column names
                    if attr_name not in column_names_list:
                        column_names_list.append(attr_name)

        select_info['header'] = column_names_list

        if totals:
            totals_row = []
            # Set an entry for each total
            for column_name in  column_names_list:
                if column_name in totals:
                    totals_row.append([0, False, True])        # Values: Accumulates the total, Alert is false and shift_right is True
                else:
                    totals_row.append(["", False, False])       # Print empty cell

        # Get the columns values
        for node_ip, node_info in  json_struct.items():
            # Key is the node name and value is the second tier dictionary with the info
            row_info = []
            if column_names_list[0] == "Node":
                row_info.append((node_ip, False))      # First column is node name
            for index, column_name in enumerate(column_names_list[1:]):
                if column_name in node_info:
                    column_value = node_info[column_name]
                    if column_value == None:
                        continue

                    if isinstance(column_value, int):
                        data_type = "int"
                        shift_right = True  # Shift right in the table cell
                        formated_val = "{:,}".format(column_value)
                    elif isinstance(column_value, float):
                        data_type = "float"
                        shift_right = True      # Shift right in the table cell
                        formated_val = "{0:,.2f}".format(column_value)
                    else:
                        data_type = "str"
                        shift_right = False  # Shift left in the table cell
                        formated_val = str(column_value)
                        if not formated_val:
                            row_info.append(("N/A", True, False, False))          # "N/A" - The value to print, is alert, shift, the last False means warning (True means alert - impacts the color)
                            continue        # Empty string

                    if totals:
                        if totals_row[index + 1][0] != "":
                            try:
                                if data_type != "str":
                                    totals_row[index + 1][0] += column_value
                                elif column_value.is_digit():
                                    totals_row[index + 1][0] += int(column_value)
                                else:
                                    totals_row[index + 1][0] += float(column_value)
                            except:
                                pass

                    alert_val = False
                    if alerts:
                        # if column_name in alerts --> process alert to change display color
                        if column_name in alerts:
                            alert_code = alerts[column_name].replace("value", str(column_value))
                            try:
                                alert_val = eval(alert_code)
                            except Exception as err_msg:
                                flash("AnyLog: Error in alerts for topic '%s' evaluating: '%s' with error: %s" % (topic, alert_code, err_msg), category='error')
                            else:
                                if alert_val:
                                    # Change color of display
                                    pass

                    row_info.append((formated_val, alert_val, shift_right, True))      # The value to print, is alert, shift, the last True means Alert (False means warning - impacts the color)

                else:
                    row_info.append(("", False))

            table_rows.append(row_info)

        if totals:
            for entry in totals_row:
                if isinstance(entry[0], int):
                    entry[0] = "{:,}".format(entry[0])
                elif isinstance(entry[0], float):
                    entry[0] = "{0:,.2f}".format(entry[0])

            table_rows.append(totals_row)

        select_info['rows'] = table_rows

    return render_template('monitor_topic.html', **select_info)

# -----------------------------------------------------------------------------------
# Set the location key on the parent node
# -----------------------------------------------------------------------------------
def set_location_on_parent( location_key ):

    index = location_key.rfind('@')
    if index != -1:
        new_key = location_key[:index]
    else:
        new_key = ""
    return new_key

# -----------------------------------------------------------------------------------
# Add reply from executing a command
# -----------------------------------------------------------------------------------
def add_command_reply(current_node, al_cmd):
    # Get from the parent the IP and port and issue the query
    parent_node = current_node.get_parent()
    parent_details = parent_node.details
    error_msg = None
    if parent_details:
        if "ip" in parent_details.keys and "rest_port" in parent_details.keys:
            index = parent_details.keys.index("ip")
            ip = parent_details.values[index]
            index = parent_details.keys.index("rest_port")
            port = parent_details.values[index]
            target_node = "http://%s:%s" % (ip, str(port))

            data, error_msg = exec_al_cmd( al_cmd, dest_node = target_node)
            if not error_msg and len(data):
                json_info, table_info, data_info, error_msg = format_message_reply(data)
                if not error_msg:
                    if json_info:
                        # Add a subtree with the JSON message
                        current_node.add_json_struct(json_info)
                    elif table_info:
                        # Add table
                        current_node.add_table(table_info)
                    else:
                        # Add text
                        current_node.add_data(data_info)
        else:
            error_msg = "IP and Port information for node: '%s' are not available" % parent_node.name

    return error_msg

# -----------------------------------------------------------------------------------
# Based on the message reply - organize as a table or as an attrubute values list
# -----------------------------------------------------------------------------------
def format_message_reply(msg_text):
    '''
    Return 4 values depending on the type of message:
    policy
    table_info (header, title and rows)
    Text List (entries are attr - val pairs)
    '''

    # If the message is a dictionary or a list - return the dictionary or the list

    policy = None
    error_msg = None
    if msg_text[0] == '{' and msg_text[-1] == '}':
        policy, error_msg = json_api.string_to_json(msg_text)

    elif msg_text[0] == '[' and msg_text[-1] == ']':
        policy, error_msg = json_api.string_to_list(msg_text)

    if policy or error_msg:
        return [policy, None, None, error_msg]  # return the dictionary or the list


    # Make a list of strings to print
    data = msg_text.replace('\r', '')
    text_list = data.split('\n')


    # Test id the returned message is formatted as a table
    table_data = {}
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

                table_data['header'] = header
                if index > 1 and len(text_list[index -2]):
                    table_data['table_title'] = text_list[index -2]         # Get the title if available
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

        table_data['rows'] = table_rows
        return [None, table_data, None, None]

    # Print Text

    data_list = []     # Every entry holds type of text ("text" or "Url) and the text string

    for entry in text_list:
        # Setup URL Link (reply to help command + a link to the help page)
        if entry[:6] == "Link: ":
            index = entry.rfind('#')  # try to find name of help section
            if index != -1:
                section = entry[index + 1:].replace('-', ' ')
            else:
                section = ""
            data_list.append(("url", entry[6:], section))
        else:
            # Split text to attribiute value using colon
            if entry:
                key_val = entry.split(':', 1)
                key_val.insert(0, "text")

                data_list.append(key_val)

    return [None, None, data_list, None]

# -----------------------------------------------------------------------------------
# Add policy to the GUI
# -----------------------------------------------------------------------------------
def add_policy(current_node, policy_id):
    if current_node.is_option_node():
        # move to the data node
        policy_node = current_node.get_parent()
    else:
        policy_node = current_node
    if policy_node.is_with_json():
        # Policy exists with this node
        policy_node.reset_json_struct()
    else:
        # Read and add new policy
        retrieved_policy = get_json_policy(policy_id)
        if retrieved_policy and isinstance(retrieved_policy, list) and len(retrieved_policy) == 1:
            policy_node.add_json_struct(retrieved_policy[0])


# -----------------------------------------------------------------------------------
# Navigate in the reports partitioned by folders
# -----------------------------------------------------------------------------------
def navigate_in_reports(user_name, location_key, folder_added, folder_renamed, folder_deleted, dashboard_deleted):

    root_nav = path_stat.get_element(user_name, "root_nav")

    if request.query_string:
        query_string = request.query_string.decode('ascii')
        # A Panel was selected - view the panel
        if query_string[:7] == "report=":
            select_info = get_select_menu()
            select_info['title'] = "Current Status"

            compressed_urls = query_string[7:]
            url_list = uncompress_urls(compressed_urls) # Uncompress the string to the list of panels

            select_info["url_list"] = url_list

            return render_template('output_frame.html', **select_info)

    select_info = get_select_menu(selection=location_key)

    selection_list = location_key.replace('+', '@').split('@')

    # Navigate in the tree to find location of Node
    current_node = nav_tree.get_current_node(root_nav, selection_list, 0)
    if folder_added or folder_renamed or folder_deleted or dashboard_deleted:
        # If adding a folder or renaming - reset children and read again the children folders - with the new folder
        current_node.reset_children()
    elif current_node.is_with_children():
        current_node.reset_children()  # Delete children from older navigation
        return call_navigation_page(user_name, select_info, location_key, current_node)

    platform, url, token, folder_name = get_report_info(user_name, location_key)

    current_node.add_child(name=location_key + '@' + "Add_Folder", option="New Folder", path=location_key + '@' + "Add_Folder")

    # Get the child folders
    child_folders, err_msg = visualize.get_child_folders(platform, url, token, folder_name)     # pass location_key after the prefix "Reports"
    if err_msg:
        flash(err_msg, category='error')
        return redirect(url_for('metadata', selection=location_key))

    for child in child_folders:
        # Add folders to tree
        current_node.add_child(name=child, path=location_key + '@' + child, folder=True)

    current_node.add_child(name=location_key + '@' + "Add_Report", option="New Report", path=location_key + '@' + "Add_Report")

    # Get the reports in the folder
    panels_urls, err_msg = visualize.get_reports("Grafana", url, token, folder_name)
    if err_msg:
        flash(err_msg, category='error')
        return redirect(url_for('metadata', selection=location_key))

    # Update the tree
    if panels_urls:
        for name, urls_list in panels_urls.items():
            key = location_key + '@' + name
            urls_string = compress_urls(urls_list)    # Make a string representing the list of urls (each url represents a panel)
            params = {
                'name': name,
                'key': key,
                'path': key,
                'report' : True,
                'url' : urls_string,     # Save a compressed strung representing a list of URLS
            }
            current_node.add_child( **params )

    return call_navigation_page(user_name, select_info, location_key, current_node)
# -----------------------------------------------------------------------------------
# Represent a list of urls as a single string:
# The process:
# Sort the given set of N strings.
# Compare the first and last string in the sorted array of strings.
# The string with prefix characters matching in the first and last string will be the answer.
# -----------------------------------------------------------------------------------
def compress_urls(urls_list):

    counter = len(urls_list)

    if counter == 1:
        compressed_string = "1." + urls_list[0]     # Only one string
    else:
        urls_list.sort()
        first_url =  urls_list[0]
        last_url = urls_list[counter -1]

        # get number of bytes to compare
        max_bytes = len(first_url)
        if len(last_url) < max_bytes:
            max_bytes = len(last_url)

        for bytes_eauql in range (max_bytes):
            if first_url[bytes_eauql] != last_url[bytes_eauql]:
                break

        compressed_info = "%u.%u." % (counter, bytes_eauql)  # The number of URLS + the size of common prefix
        compressed_data = first_url[:bytes_eauql]      # The size of the prefix

        for entry in urls_list:
            len_delta = len(entry) - bytes_eauql    # The difference that is needed to complete the URL
            compressed_info += "%u." % len_delta    # Add the size to complete the url
            compressed_data += entry[-len_delta:] # The url delta (suffix)

        compressed_string = compressed_info + compressed_data

    return compressed_string
# -----------------------------------------------------------------------------------
# Transformed a compressed string to a list of URLS
# -----------------------------------------------------------------------------------
def uncompress_urls(compressed_string):
    urls_list = []
    index = compressed_string.find('.')     # Get the number of urls
    if index > 0:
        counter = int(compressed_string[:index])         # the number of urls
        if counter == 1:
            urls_list.append(compressed_string[index + 1:])
        else:
            list_entries = compressed_string[index + 1:].split('.', counter + 1)
            bytes_eauql = int(list_entries[0])
            shared_prefix = list_entries[-1][:bytes_eauql]
            offset = bytes_eauql

            for i in range (counter):
                suffix_length = int(list_entries[1 + i])
                url_string = shared_prefix + list_entries[-1][offset:offset+suffix_length]
                offset += suffix_length

                urls_list.append(url_string)

    return urls_list

# -----------------------------------------------------------------------------------
# Return the report platform and folder
# -----------------------------------------------------------------------------------
def get_report_info(user_name, location_key):
    gui_key = app_view.get_gui_key(location_key)  # Transform selection with data to selection of GUI keys

    gui_view = path_stat.get_element(user_name, "gui_view")
    root_gui, gui_sub_tree = gui_view.get_subtree(
        gui_key)  # Get the subtree representing the location on the config file

    platform = root_gui["visualization"]  # Grafana, Power BI etc.

    network_name = gui_view.get_base_info("name")
    root_folder = "AnyLog_" + network_name

    if location_key == "Reports":
        folder_name = root_folder
    else:
        folder_name = root_folder + location_key[7:]

    platforms_tree = gui_view.get_base_info("visualization")
    url = platforms_tree[platform]['url']
    token = platforms_tree[platform]['token']

    return [platform, url, token, folder_name]

# -----------------------------------------------------------------------------------
# Call the navigation page - metadata.html
# -----------------------------------------------------------------------------------
def call_navigation_page(user_name, select_info, location_key, current_node):

    print_list = []

    root_nav = path_stat.get_element(user_name, "root_nav")

    nav_tree.setup_print_list(root_nav, print_list)

    if current_node:

        gui_view = path_stat.get_element(user_name, "gui_view")
        gui_key = app_view.get_gui_key(location_key)  # Transform selection with data to selection of GUI keys
        root_gui, gui_sub_tree = gui_view.get_subtree(gui_key)  # Get the subtree representing the location on the config file

        if gui_sub_tree and 'submit' in gui_sub_tree:
            # add submit buttons
            if current_node.is_with_children():
                current_node.add_submit_buttons(gui_sub_tree['submit'])
            else:
                current_node.reset_submit_buttons() # No need in submit buttons with no children

        # Place a flag to indicate the position n the page  when page is loaded
        # Reset is done in nav_tree.setup_print_list
        current_node.set_scroll_location()

    else:
        # First page - nothing selected - show the Network Map
        gui_view = path_stat.get_element(user_name, "gui_view")
        map_url = gui_view.get_base_info("map")
        if map_url:
            select_info['map_url'] = map_url



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

    # Need to login before navigating
    if not get_user_by_session():
        return redirect(('/login'))  # start with Login  if not yet provided

    select_info = get_select_menu(selection=selection)

    # Make title from the path
    title = ""
    if "parent_gui" in select_info:
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


    level = selection.count('@') + 1
    user_name = session["username"]
    gui_view = path_stat.get_element(user_name, "gui_view")

    # Get the location in the Config file to set the user navigation links
    root_gui, gui_sub_tree = gui_view.get_subtree(selection)

    command = app_view.get_tree_entree(gui_sub_tree, "query")  # get the command from the Config file

    if current_node:
        # Use tree Navigation
        al_command = nav_tree.update_command(current_node, selection, command)  # Update the command with the parent info
    else:
        # Use of Path Navigation
        al_command = path_stat.update_command(user_name, selection, command)  # Update the command with the parent info

    if not al_command:
        flash("AnyLog: Missing AnyLog Command in Config file: '%s' with selection: '%s'" % (str(selection)), category='error')
        return None  # Show all user select options

    # Get the columns names of the table to show
    list_columns = app_view.get_tree_entree(gui_sub_tree, "table_title")
    if not list_columns:
        flash("AnyLog: Missing column names in config file: '%s' with selection: '%s'" % (Config.GUI_VIEW, str(selection)), category='error')
        return None

    # Get the keys to pull data from the JSON reply
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    if not list_keys:
        flash("AnyLog: Missing 'list_keys' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level), category='error')
        return None # Show all user select options

    # Run the query against the Query Node

    data, error_msg = exec_al_cmd( al_command )

    if error_msg:
        flash(error_msg, category='error')
        return None
    if not data:
        flash('AnyLog: Empty data set returned with command: %s' % al_command, category='error')
        return None

    data_list = app_view.str_to_list(data)

    if not data_list:
        flash('AnyLog: Error in data format returned from node with command: %s' % al_command, category='error')
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
        if len(cmd_list) >= 3 and cmd_list[0] == "blockchain" and cmd_list[1] == "get":
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

    if not get_user_by_session():
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

    gui_view = path_stat.get_element(user_name, "gui_view")
    platforms_tree = gui_view.get_base_info("visualization")
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

    url_list, err_msg = visualize.new_report("Grafana", **platform_info)

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

    if id.find(' ') != -1:
        if id[0] != "\"":
            id = "\"" + id
        if id[-1] != "\"":
            id = id + "\""
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

    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # Redo the login - need a user name

    gui_view = path_stat.get_element(user_name, "gui_view")
    # pull the keys that are used to print a summary of the data instance
    root_gui, gui_sub_tree = gui_view.get_subtree(parent_menu[-1][1][6:])
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    table_title = app_view.get_tree_entree(gui_sub_tree, "table_title")

    path_stat.update_status(user_name, parent_menu, list_keys, table_title, policy_id, data)

# -----------------------------------------------------------------------------------
# Execute a command against the AnyLog Query Node
# -----------------------------------------------------------------------------------
def exec_al_cmd( al_cmd, dest_node = None, call_type = "GET"):
    '''
    Run the query against the Query Node
    '''

    user_name = session["username"]

    if dest_node:
        target_node = dest_node
    else:
        target_node = path_stat.get_element(user_name, "target_node")

    al_headers = {
        'User-Agent' : 'AnyLog/1.23',
        'command' : al_cmd
        }

    basic_auth = path_stat.get_element(user_name, 'basic auth')
    if basic_auth:
        al_headers['Authorization'] = basic_auth

    if call_type == "POST":
        response, error_msg = rest_api.do_post(target_node, al_headers)
    else:
        response, error_msg = rest_api.do_get(target_node, al_headers)

    if response != None and response.status_code == 200:
        data = response.text
    else:
        data = None
        if not error_msg:
            if response != None and response.reason != "":
                error_msg = "AnyLog: REST command error \"%s\"" %  response.reason
            else:
                # No data reply
                error_msg = "AnyLog: REST command \"%s\" returned error code %u" % (al_cmd, response.status_code)

    return [data, error_msg]

# -----------------------------------------------------------------------------------
# Get the menu data based on the configuration file
# Test if configuration file is available, otherwise go to configure form
# -----------------------------------------------------------------------------------
def get_select_menu(selection = "", caller = ""):

    select_info = {}

    gui_view = get_gui_view()
    if gui_view:

        if not gui_view.is_with_config():
            # Faild to recognize the JSON Config File
            flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW, category='error')
            if caller == "configure" or caller == "login":
                # The config file is not available - ignore get_select_menu
                return select_info  # return empty dictionary

            form = ConfigForm()
            return render_template('configure.html', title = 'Configure Network Connection', form = form)

        company_name = gui_view.get_base_info("name")                 # The user name
        user_menu = gui_view.get_base_info("url_pages")           # These are specific web pages to the user
        parent_menu, children_menu = gui_view.get_dynamic_menu(selection)     # web pages based on the navigation

        if company_name:
            select_info['company_name'] = company_name
        if user_menu and len(user_menu):
            select_info['user_gui'] = user_menu
        if parent_menu and len(parent_menu):
            select_info['parent_gui'] = parent_menu
        if children_menu and len(children_menu):
            select_info['children_gui'] = children_menu

        # get the loggin name a name from the conf file
        if 'username' in session:
            user_name = session['username']
        else:
            user_name = gui_view.get_base_info("name") or "AnyLog"
        select_info['report_name'] = path_stat.get_report_selected(user_name)

    return select_info


# -----------------------------------------------------------------------------------
# Manage the reports
# -----------------------------------------------------------------------------------
@app.route('/manage_reports/', methods={'GET','POST'})
def manage_reports():

    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))  # start with Login  if not yet provided

    select_info = get_select_menu()
    select_info['title'] = "Manage Reports"

    gui_view = path_stat.get_element(user_name, "gui_view")
    platforms_tree = gui_view.get_base_info("visualization")
    url = platforms_tree["Grafana"]['url']
    token = platforms_tree["Grafana"]['token']
    network_name = gui_view.get_network_name()

    panels_urls, err_msg = visualize.get_reports("Grafana", url, token, "AnyLog_" + network_name)   # Get the list of reports associated with

    if not err_msg:
        select_info['panels_urls'] = panels_urls

    return render_template('manage_reports.html', **select_info)
# -----------------------------------------------------------------------------------
# Configure the dynamic reports
# -----------------------------------------------------------------------------------
@app.route('/configure_reports/', methods={'GET','POST'})
def configure_reports():
    '''
    View the report being used
    '''

    user_name =  get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

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
   

    user_name = get_user_by_session()
    if not user_name:
        return redirect(('/login'))        # start with Login  if not yet provided

    gui_view = path_stat.get_element(user_name, "gui_view")

    select_info = get_select_menu()
    select_info['title'] = "Network Policies"
    select_info['policies'] = gui_view.get_policies_list()  # Collect the names of the policies

    if policy_name:
        # A policy was selected
        policy = gui_view.get_policy_info(policy_name)
        if len(request.form):
            # send policy from Form
            target_node = path_stat.get_element(user_name,"target_node")

            err_msg = anylog_api.deliver_policy(target_node, policy, request.form)
            if err_msg:
                flash('AnyLog Connector: %s' % err_msg, category='error')

        # Goto the same form again to add a new policy
        select_info['policy_name'] = policy_name
        policy = gui_view.get_policy_info(policy_name)
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