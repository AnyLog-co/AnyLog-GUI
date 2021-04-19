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

import json
import requests
from requests.exceptions import HTTPError

from app import app_view        # maintains the logical view of the GUI from a JSON File
from app import path_stat       # Maintain the path of the user

user_connect_ = False       # Flag indicating connected to the AnyLog Node 
node_config_ = {}           # Config as f(company_name)
company_name_ = None        # Company to service

gui_view_ = app_view.gui()            # Load the definition of the user view of the metadata from a JSON file
gui_view_.set_gui()

query_node_ = None


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
    select_info['title'] = "Home"
    
    return render_template('main.html', **select_info)
# -----------------------------------------------------------------------------------
# Login
# -----------------------------------------------------------------------------------
@app.route('/login', methods={'GET','POST'})
def login():
    '''
    Inpuit login name & password, connecet to a node in the network
    and move to main page to determine GUI to use
    '''
    global user_connect_

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

    if company_name_:
        title_str = 'Sign In: %s' % company_name_
    else:
        title_str = 'Sign In'

    if 'username' in session:
        user_name = session['username']
        if not path_stat.is_with_user( user_name ):
            path_stat.set_new_user( user_name )

    select_info = get_select_menu()
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
def dynamic_report( report_name = "My_Report" ):
    '''
    View the report being used
    Called from - base.html
    '''
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session['username']

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
 
    al_table = AnyLogTable("Report: %s" % report_name, list_columns, None, table_rows, extra_columns)

    select_info = get_select_menu()
    select_info['table'] = al_table
    select_info['title'] = "Report: %s" % report_name

    # select grafics options
    options_list = ["Min", "Max", "Avg", "Count", "Diff"]
    select_info['options_list'] = options_list

    # select visualization platform
    visualization = gui_view_.get_base_info("visualization") or ["Grafana"]
    select_info['visualization'] = visualization
    select_info['report_name'] = report_name
    
    return render_template('report_deploy.html',  **select_info )
# -----------------------------------------------------------------------------------
# Processing form: report_deploy.html
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

    # Get all the info to genet=rate a report

    return redirect(("http://127.0.0.1:3000/?orgId=1"))      
# -----------------------------------------------------------------------------------
# Reports
# -----------------------------------------------------------------------------------
@app.route('/reports')
def reports():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    select_info = get_select_menu()
    select_info['title'] = 'Orics'

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
@app.route('/configure')
def configure():

    select_info = get_select_menu()
    select_info["form"] = ConfigForm()
    select_info["title"] = 'Configure Network Connection'

    if not gui_view_.is_with_config():
        # Faild to recognize the JSON Config File
        if gui_view_.is_config_error():
            flash(gui_view_.get_config_error())
        
        flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW)
        
    return render_template('configure.html', **select_info )

@app.route('/set_config', methods = ['GET', 'POST'])
def set_config():
    global node_config_
    global company_name_

    if request.method == 'POST':
        conf = {}
        conf["node_ip"] = request.form["node_ip"]
        conf["node_port"] = request.form["node_port"]
        conf["reports_ip"] = request.form["reports_ip"]
        conf["reports_port"] = request.form["reports_ip"]

        company_name = request.form["company"]
        node_config_[company_name] = conf
        company_name_ = company_name
    

    select_info = get_select_menu()
    select_info["title"] = 'Configure Network Connection'
    select_info["form"] = ConfigForm()         # New Form
    
    return render_template('configure.html',**select_info)
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
    select_info['title'] = 'Network Commands'
    select_info['form'] = form
    select_info['def_dest'] = target_node


    return render_template('commands.html', **select_info)

# -----------------------------------------------------------------------------------
# AnyLog Commands
# -----------------------------------------------------------------------------------
@app.route('/al_command', methods = ['GET', 'POST'])
def al_command():

    al_headers = {
            'User-Agent' : 'AnyLog/1.23'
    }

    
    
    select_info = get_select_menu()
 
    target_node = get_target_node()


    try:
        al_headers["command"] = request.form["command"]
        
        response = requests.get(target_node, headers=al_headers)
    except:
        flash('AnyLog: Network connection failed')
        return redirect(('/network'))     # Go to main page
    else:
        if response.status_code == 200:
            data = response.text
            data = data.replace('\r','')
            text = data.split('\n')

            select_info['title'] = 'Network Node Reply'
            select_info['text'] = text

            return render_template('output.html', **select_info)
  
    
    select_info['title'] = 'Network Status'
    select_info['form'] = CommandsForm()         # New Form
    select_info['def_dest'] = target_node
    
    return render_template('network.html', **select_info)

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


    level = selection.count('@') + 1
    # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    # Get the location in the Config file to set the user navigation links
    gui_sub_tree = gui_view_.get_subtree( selection )

    command = app_view.get_tree_entree(gui_sub_tree, "query")   # get the command from the Config file
    user_name = session["username"]
    al_command = path_stat.update_command(user_name, selection, command)   # Update the command with the parent info

    if not al_command:
        flash("AnyLog: Missing AnyLog Command in Config file: '%s' with selection: '%s'" % (Config.GUI_VIEW, str(selection)))
        return redirect(('/index'))        # Show all user select options

    # Get the columns names of the table to show
    list_columns = app_view.get_tree_entree(gui_sub_tree, "table_title")
    if not list_columns:
        flash("AnyLog: Missing 'list_columns' Config file: '%s' with selection: '%s'" % (Config.GUI_VIEW, str(selection)))
        return redirect(('/index'))        # Show all user select options

   # Get the keys to pull data from the JSON reply
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    if not list_keys:
        flash("AnyLog: Missing 'list_keys' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options
       

    target_node = get_target_node()


    # Run the query against the Query Node

    al_headers = {
        'User-Agent' : 'AnyLog/1.23',
        'command' : al_command
        }

    try:
        response = requests.get(target_node, headers=al_headers)
    except:
        flash('AnyLog: No network connection', category='error')
        user_connect_ = False
        return redirect(('/login'))        # Redo the login


    if response.status_code == 200:
        data = response.text
        data_list = app_view.str_to_list(data)
        if not data_list:
            flash('AnyLog: Error in data format returned from node', category='error')
            return redirect((url_for('index')))        # Select a different path
        if not len(data_list):
            flash('AnyLog: AnyLog node did not return data using command: \'%s\'' % al_command, category='error')
            return redirect((url_for('index')))        # Select a different path
    else:
        flash('AnyLog: No data satisfies the request', category='error')
        return redirect(('/index'))        # Select a different path

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


    select_info = get_select_menu(selection)
    extra_columns =  [('Select','checkbox')]
    al_table = AnyLogTable(select_info['parent_gui'][-1][0], list_columns, list_keys, table_rows, extra_columns)

    select_info['selection'] = selection
    select_info['tables_list'] = [al_table]
    select_info['submit'] =  "View"

    if "dbms_name" in gui_sub_tree and "table_name" in gui_sub_tree:
        # These entries can be added to a report
        select_info['add'] =  "Add"
        select_info['dbms_name'] = gui_sub_tree["dbms_name"]
        select_info['table_name'] = gui_sub_tree["table_name"]
    
    return render_template('selection_table.html',  **select_info )

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

    selected_rows = request.form

    if not selection:
        # Get that selection that is in the form
        if 'selection' in selected_rows:
            selection = selected_rows['selection']
        else:
            return redirect(url_for('index')) 

    policies = []
    for key in selected_rows:    
        if key[:7] == "Select.":
            policy_id = key[7:]
            retrieved_policy = get_json_policy(policy_id)
            if retrieved_policy:
                policies.append(retrieved_policy[0])

    if not len(policies):
        # Nothing was selected - redo
        flash('AnyLog: Missing entry selection', category='error')
        return redirect(url_for('tree', selection=selection)) 

    select_info = get_select_menu(selection)

    if "Browse" in selected_rows:
        # Put the key of the parent in the tree
        if len(policies) > 1:
            flash('AnyLog: Only one entry can be selected for browsing', category='error')
            return redirect(url_for('tree', selection=selection))

        child_name = selected_rows["Browse"]
        # Update the path for the currently used report
        # Place the parent info in the path as f(report)

        path_selection(select_info['parent_gui'], policy_id, retrieved_policy[0])   # Only one policy selected

        # Move with the selected child
        return redirect(url_for('tree', selection='%s@%s' % (selection, child_name)))

    if "Add" in selected_rows:
        # Add selected rows to report
        user_name = session["username"]
        dbms_name = selected_rows["dbms"]
        table_name = selected_rows["table"]
        for json_entry in policies:
            # Get the location in the Config file to get the database name and table name
            path_stat.add_entry_to_report(user_name, dbms_name, table_name, json_entry)

        return redirect(url_for('tree', selection='%s' % (selection)))

           
    # organize JSON entries to display
    data_list = []
    for json_entry in policies:
        json_string = json.dumps(json_entry,indent=4, separators=(',', ': '), sort_keys=True)
        data_list.append(json_string)  #  transformed to a JSON string.

    select_info['text'] = data_list
    
    # path_selection(parent_menu, id, data)      # save the path, the key and the data on the report

    return render_template('output.html', **select_info )

# -----------------------------------------------------------------------------------
# Show AnyLog Policy by ID
# -----------------------------------------------------------------------------------
def get_json_policy( id ):

        # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided


    # Run the query against the Query Node
    if not id or not isinstance(id, str):
        flash('AnyLog: Error in Policy ID', category='error')
        return redirect(('/index'))        # Select a different path

    al_cmd = "blockchain get * where id = %s" % id
    data = exec_al_cmd( al_cmd )
    json_list = app_view.str_to_list(data)
    if not json_list:
        flash('AnyLog: Error in data format returned for policy: %s' % id, category='error')
        return redirect(('/index'))        # Select a different path

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

    path_stat.update_status(user_name, parent_menu, policy_id, data)

# -----------------------------------------------------------------------------------
# Execute a command against the AnyLog Query Node
# -----------------------------------------------------------------------------------
def exec_al_cmd( al_cmd ):
    '''
    Run the query against the Query Node
    '''
    global user_connect_

    # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    target_node = get_target_node()


    al_headers = {
        'User-Agent' : 'AnyLog/1.23',
        'command' : al_cmd
        }

    
    try:
        response = requests.get(target_node, headers=al_headers)
    except HTTPError as http_err:
        error_msg = "REST GET HTTP Error: %s" % str(http_err)
        rest_err = True
    except Exception as err:
        error_msg = "REST GET Error: %s" % str(err)
        rest_err = True
    else:
        rest_err = False
       
    if rest_err:
        flash('AnyLog: %s' % error_msg, category='error')
        user_connect_ = False
        return redirect(('/login'))        # Redo the login


    if response.status_code == 200:
        data = response.text
    else:
        flash('AnyLog: No data satisfies the request', category='error')
        return redirect(('/index'))        # Select a different path
    return data

# -----------------------------------------------------------------------------------
# Get the menu data based on the configuration file
# Test if configuration file is available, otherwise go to configure form
# -----------------------------------------------------------------------------------
def get_select_menu(selection = ""):

    if gui_view_.is_with_config():

        company_name = gui_view_.get_base_info("name")                 # The user name
        user_menu = gui_view_.get_base_info("url_pages")           # These are specific web pages to the user
        parent_menu, children_menu = gui_view_.get_dynamic_menu(selection)     # web pages based on the navigation
    else:
        # Faild to recognize the JSON Config File
        form = ConfigForm()
        flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW)
        return render_template('configure.html', title = 'Configure Network Connection', form = form)

    # get the loggin name a name from the conf file
    if 'username' in session:
        user_name = session['username']
    else:
        user_name = gui_view_.get_base_info("name") or "AnyLog"

    report_name = path_stat.get_report_selected(user_name)

    select_info = {
        'company_name' : company_name,
        'user_gui' : user_menu,
        'parent_gui' : parent_menu,
        'children_gui' : children_menu,
        'report_name' : report_name
    }

    # Make title from the path
    title = ""
    for parent in parent_menu:
        title += parent[0] + " : "
    select_info['title'] = title

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
# Logout
# -----------------------------------------------------------------------------------
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))