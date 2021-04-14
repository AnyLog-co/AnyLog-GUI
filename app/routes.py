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
# -----------------------------------------------------------------------------------

@app.route('/')
@app.route('/index')
def index():

    if not user_connect_:
        return redirect(('/login'))        # start with Login

   
    user_name = gui_view_.get_base_info("name")                 # The user name
    user_menu = gui_view_.get_base_info("url_pages")           # These are specific web pages to the user
    parent_menu, children_menu = gui_view_.get_dynamic_menu(None)     # web pages based on the navigation

    return render_template('main.html', title='Home',user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)
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
            redirect(('/login'))        # Redo the login

        session['username'] = request.form['username']


        return redirect(('/index'))     # Go to main page

    if company_name_:
        title_str = 'Sign In: %s' % company_name_
    else:
        title_str = 'Sign In'

    if not 'username' in session:
        redirect(('/login'))        # Redo the login - need a user name
    
    user_name = session['username']
    if not path_stat.is_with_user( user_name ):
        path_stat.set_new_user( user_name )

    user_name, user_menu, parent_menu, children_menu = get_select_menu()

    return render_template('login.html', title = title_str, form = form, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu )


# -----------------------------------------------------------------------------------
# Reports
# -----------------------------------------------------------------------------------
@app.route('/reports')
def reports():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name, user_menu, parent_menu, children_menu = get_select_menu()

    return render_template('reports.html', title = 'Orics', user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)
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

    form = ConfigForm()
    if gui_view_.is_with_config():

        user_name = gui_view_.get_base_info("name")                 # The user name
        user_menu = gui_view_.get_base_info("url_pages")           # These are specific web pages to the user
        parent_menu, children_menu = gui_view_.get_dynamic_menu(None)     # web pages based on the navigation
    else:
        # Faild to recognize the JSON Config File
        if gui_view_.is_config_error():
            flash(gui_view_.get_config_error())
        
        flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW)
        return render_template('configure.html', title = 'Configure Network Connection', form = form)

    if form.validate_on_submit():
        flash('AnyLog: Network Member Node {}:{}'.format(form.node_ip, form.node_port))

    return render_template('configure.html', title = 'Configure Network Connection', form = form, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu )

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
    
    form = ConfigForm()         # New Form
    
    return render_template('configure.html', title = 'Configure Network Connection', form = form, private_gui = gui_view_.get_base_menu())
# -----------------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------------
@app.route('/network')
def network():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided


    target_node = get_target_node()
    user_name, user_menu, parent_menu, children_menu = get_select_menu()
    
    form = CommandsForm()         # New Form

    return render_template('commands.html', title = 'Network Commands', form = form, def_dest=target_node, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)


@app.route('/al_command', methods = ['GET', 'POST'])
def al_command():

    al_headers = {
            'User-Agent' : 'AnyLog/1.23'
    }

    
    user_name, user_menu, parent_menu, children_menu = get_select_menu()
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
            return render_template('output.html', title = 'Network Node Reply', text=text, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)
  
    
    form = CommandsForm()         # New Form

    user_name, user_menu, parent_menu, children_menu = get_select_menu()
    
    return render_template('network.html', title = 'Network Status', form = form, def_dest=target_node, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)

@app.route('/install', methods = ['GET', 'POST'])
def install():

    user_name, user_menu, parent_menu, children_menu = get_select_menu()
  
    form = InstallForm()         # New Form
    return render_template('install.html', title = 'Install Network Node', form = form, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)


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

    gui_sub_tree = gui_view_.get_subtree( selection )    # Set the user navigation links

    al_command = app_view.get_tree_entree(gui_sub_tree, "query")

    if not al_command:
        flash("AnyLog: Missing AnyLog Command in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options

    # Get the columns names of the table to show
    list_columns = app_view.get_tree_entree(gui_sub_tree, "table_title")
    if not list_columns:
        flash("AnyLog: Missing 'list_columns' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options

   # Get the keys to pull data from the JSON reply
    list_keys = app_view.get_tree_entree(gui_sub_tree, "json_keys")
    if not list_keys:
        flash("AnyLog: Missing 'list_keys' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options
       

    user_name, user_menu, parent_menu, children_menu = get_select_menu(selection)
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
        redirect(('/login'))        # Redo the login


    if response.status_code == 200:
        data = response.text
        data_list = app_view.str_to_list(data)
        if not data_list:
            flash('AnyLog: Error in data format returned from node', category='error')
            redirect(('/index'))        # Select a different path
    else:
        flash('AnyLog: No data satisfies the request', category='error')
        redirect(('/index'))        # Select a different path

    # Set table info to present in form

    table_rows = []
    for entry in data_list:
        columns_list = []
        for key in list_keys:
            # Validate values in reply
            if key in entry:
                value = entry[key]
            else:
                value = ""
            columns_list.append((key, str(value)))
        
        # Set a list of table entries
        table_rows.append(AnyLogItem(columns_list))

    
    # Create a class dynamically with the needed attributes
    attributes = {}
    for entry in list_columns:
        attributes[entry.lower()] = Col(entry)

    if "id" in list_keys:
        # Data includes an id of the JSON object
        args = dict(id='id')
        extra_args = {
            'selection' : selection
            }
        # Let the user select view to see the JSON
        attributes ["Select"] = LinkCol('Select', 'view_policy', url_kwargs=args, url_kwargs_extra=extra_args)

    # If node has children - show the childrens
    if not app_view.is_edge_node(gui_sub_tree):
        # provide select option
        args = dict(id='id')
        extra_args = {
            'selection' : selection

            }
        # attributes ["select"] = LinkCol('select', 'edge_select', url_kwargs=args, url_kwargs_extra=extra_args)
        
    TableClass = type ( 'AnyLogTable', (Table,), attributes)
    table = TableClass(table_rows)
    table.border = True

  
    return render_template('entries_list.html', table = table,  user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu )
# -----------------------------------------------------------------------------------
# Select the children elements or move to parent
# -----------------------------------------------------------------------------------
@app.route('/edge_select/<string:selection><string:id>')
def edge_select( selection, id ):
    '''
    Select the children elements or move to parent
    '''
    pass

# -----------------------------------------------------------------------------------
# Show AnyLog Policy by ID
# -----------------------------------------------------------------------------------
@app.route('/view_policy/<string:selection>@<string:id>')
def view_policy( selection, id ):

        # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided


    # Run the query against the Query Node
    if not id or not isinstance(id, str):
        flash('AnyLog: Error in Policy ID', category='error')
        redirect(('/index'))        # Select a different path

    al_cmd = "blockchain get * where id = %s" % id
    data = exec_al_cmd( al_cmd )
    json_list = app_view.str_to_list(data)
    if not json_list:
        flash('AnyLog: Error in data format returned from node', category='error')
        redirect(('/index'))        # Select a different path

    # organize JSON entries to display
    data_list = []
    for json_entry in json_list:
        json_string = json.dumps(json_entry,indent=4, separators=(',', ': '), sort_keys=True)
        data_list.append(json_string)  #  transformed to a JSON string.

    user_name, user_menu, parent_menu, children_menu = get_select_menu(selection)

    path_selection(parent_menu, id, data)      # save the path, the key and the data on the report

    # Make title from the path
    title = ""
    for parent in parent_menu:
        title += parent[0] + " : "

   
    return render_template('output.html', title = title, text=data_list, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu )

# -----------------------------------------------------------------------------------
# Save the path, the key and the data on the report used
# -----------------------------------------------------------------------------------
def path_selection(parent_menu, id, data):

    if not 'username' in session:
        redirect(('/login'))        # Redo the login - need a user name

    user_name = session["username"]

    path_stat.update_status(user_name, parent_menu, id, data)

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
        redirect(('/login'))        # Redo the login


    if response.status_code == 200:
        data = response.text
    else:
        flash('AnyLog: No data satisfies the request', category='error')
        redirect(('/index'))        # Select a different path
    return data

# -----------------------------------------------------------------------------------
# Get the menu data based on the configuration file
# Test if configuration file is available, otherwise go to configure form
# -----------------------------------------------------------------------------------
def get_select_menu(selection = ""):

    if gui_view_.is_with_config():

        user_name = gui_view_.get_base_info("name")                 # The user name
        user_menu = gui_view_.get_base_info("url_pages")           # These are specific web pages to the user
        parent_menu, children_menu = gui_view_.get_dynamic_menu(selection)     # web pages based on the navigation
    else:
        # Faild to recognize the JSON Config File
        form = ConfigForm()
        flash('AnyLog: Failed to load Config File or wrong file structure: %s' % Config.GUI_VIEW)
        return render_template('configure.html', title = 'Configure Network Connection', form = form)

    return [user_name, user_menu, parent_menu, children_menu]


def get_target_node():

    target_node = query_node_ or gui_view_.get_base_info("query_node")
    if not target_node:
        flash("AnyLog: Missing query node connection info")
        return redirect(('/configure'))     # Get the query node info
    return target_node

# -----------------------------------------------------------------------------------
# View the report structure being used
# -----------------------------------------------------------------------------------
@app.route('/dynamic_report/')
def dynamic_report():
    '''
    View the report being used
    '''
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    user_name = session['username']

    return "Default"
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

    if form.validate_on_submit():
        pass

    user_name, user_menu, parent_menu, children_menu = get_select_menu()

    return render_template('configure_reports.html', title='Configure Reports',form = form, user_name=user_name,user_gui=user_menu,parent_gui=parent_menu,children_gui=children_menu)

# -----------------------------------------------------------------------------------
# Logout
# -----------------------------------------------------------------------------------
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))