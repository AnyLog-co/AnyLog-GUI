
from flask import render_template, flash, redirect, request, url_for, jsonify
from flask_table import  Table, Col, LinkCol
from app import app
from app.forms import LoginForm
from app.forms import ConfigForm
from app.forms import CommandsForm
from app.forms import InstallForm
from app.entities import Companies
from app.entities import Item
from app.entities import AnyLogItem

from config import Config

import json
import requests
from requests.exceptions import HTTPError

from app import app_view        # maintains the logical view of the GUI from a JSON File

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

    gui_view_.set_menue()
    
    return render_template('main.html', title = 'Home',  private_gui = gui_view_.get_base_menu() )
# -----------------------------------------------------------------------------------
# Machine
# -----------------------------------------------------------------------------------
@app.route('/machine')
def machine(company_name = None):

    if not user_connect_:
        return redirect(('/login'))        # start with Login

    metadata = {"id": "1",
                "data": {"installation":
                             {"customer": "TuscanBrands",
                              "machine_name": "VGF-R-40",
                              "serial_number": "15575"},
                         "tags":
                             {"CODE OK": {"description": "Elevated access granted"},
                              "HEATER TEMPERATURE 1": {"description": "Heater 1 Temperature"},
                              "HEATER TEMPERATURE 2": {"description": "Heater 2 Temperature"},
                              "HEATER TEMPERATURE 3": {"description": "Heater 3 Temperature"},
                              "HEATER TEMPERATURE 4": {"description": "Heater 4 Temperature"},
                              "TEMPERATURE LOW LIM": {"description": "Low Temperature Threshold"},
                              "TEMPERATURE HIGH LIM": {"description": "High Temperature Threshold"},
                              "ChamberLifter.OutputCurrent": {"description": "Chamber Lifter Output Current"},
                              "MACHINE CYCLE TIME": {"description": "Machine Cycles (cycles/min)"},
                              "SFR OK": {"description": "Safety Circuit Reset"},
                              "BATCH COUNT": {"description": "Number of Trays Sealed"},
                              "FilmSupply:I.OutputCurrent": {"description": "Film Supply Output Current"},
                              "FilmAdvance:I.OutputCurrent": {"description": "Film Advance Output Current"},
                              "OutfeedConv:I.OutputCurrent": {"description": "Outfeed Output Current"},
                              "Capper:I.OutputCurrent": {"description": "Capper Output Current"},
                              "Table:I.OutputCurrent": {"description": "Table Output Current"},
                              "ALARMS DESPLAY TIME": {"description": "Active Alarms"}}}}


    

    return render_template('index.html', title = 'Home', metadata = metadata, builder = "Orics", customer = metadata["data"]["installation"]["customer"], private_gui = gui_view_.get_base_menu())

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

    gui_view_.set_menue()

    form = LoginForm()

    if form.validate_on_submit():
        al_headers = {
            'command' : 'get status',
            'User-Agent' : 'AnyLog/1.23'
            }

        try:
            response = requests.get('http://10.0.0.78:7849', headers=al_headers)
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

        return redirect(('/index'))     # Go to main page

    if company_name_:
        title_str = 'Sign In: %s' % company_name_
    else:
        title_str = 'Sign In'

    return render_template('login.html', title = title_str, form = form,  private_gui = gui_view_.get_base_menu())

# -----------------------------------------------------------------------------------
# Companies
# -----------------------------------------------------------------------------------
@app.route('/company')
def company():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    
    al_headers = {
            'command' : "blockchain get operator bring.unique [operator][company] ,",
            'User-Agent' : 'AnyLog/1.23'
    }


    try:
        response = requests.get('http://10.0.0.78:7849', headers=al_headers)
    except:
        flash('AnyLog: Network connection failed')
        return redirect(('/index'))     # Go to main page
    else:
        companies_list = []
        if response.status_code == 200:
            data = response.text
            if data and len(data) > 21:
                companies = list(filter(None, data[21:-2].split(',')))
                
                for company in companies:
                    companies_list.append(Item(company))

        table = Companies(companies_list)
        table.border = True

    return render_template('companies.html', table = table, private_gui = gui_view_.get_base_menu())

# -----------------------------------------------------------------------------------
# Sensor
# -----------------------------------------------------------------------------------
@app.route('/sensor')
def sensor():
    return redirect(('/login'))        # start with Login if not yet provided
# -----------------------------------------------------------------------------------
# Reports
# -----------------------------------------------------------------------------------
@app.route('/reports')
def reports():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided


    return render_template('reports.html', title = 'Orics', private_gui = gui_view_.get_base_menu())
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

    gui_view_.set_menue()
    
    form = ConfigForm()
    if form.validate_on_submit():
        flash('AnyLog: Network Member Node {}:{}'.format(form.node_ip, form.node_port))

    return render_template('configure.html', title = 'Configure Network Connection', form = form, private_gui = gui_view_.get_base_menu())

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

    form = CommandsForm()         # New Form

    def_dest = "10.0.0.78:7848"

    return render_template('commands.html', title = 'Network Commands', form = form, def_dest=def_dest, private_gui = gui_view_.get_base_menu())


@app.route('/al_command', methods = ['GET', 'POST'])
def al_command():

    al_headers = {
            'User-Agent' : 'AnyLog/1.23'
    }


    try:
        al_headers["command"] = request.form["command"]
        
        response = requests.get('http://10.0.0.78:7849', headers=al_headers)
    except:
        flash('AnyLog: Network connection failed')
        return redirect(('/network'))     # Go to main page
    else:
        if response.status_code == 200:
            data = response.text
            data = data.replace('\r','')
            text = data.split('\n')
            return render_template('output.html', title = 'Network Node Reply', text=text, private_gui = gui_view_.get_base_menu())
  
    
    form = CommandsForm()         # New Form

    def_dest = "10.0.0.78:7848"
    
    return render_template('network.html', title = 'Network Status', form = form, def_dest=def_dest, private_gui = gui_view_.get_base_menu())

@app.route('/install', methods = ['GET', 'POST'])
def install():
  
    form = InstallForm()         # New Form
    return render_template('install.html', title = 'Install Network Node', form = form, private_gui = gui_view_.get_base_menu())


# -----------------------------------------------------------------------------------
# Logical tree navigation
# https://hackersandslackers.com/flask-routes/
# https://www.freecodecamp.org/news/dynamic-class-definition-in-python-3e6f7d20a381/
# -----------------------------------------------------------------------------------
@app.route('/tree')

def tree( level = 1):
    global query_node_
    global user_connect_

    # Need to login before navigating
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    target_node = query_node_ or gui_view_.get_query_node()
    if not target_node:
        flash("AnyLog: Missing query node connection info")
        return redirect(('/configure'))     # Get the query node info

    nav_list = []
    gui_view_.get_nav_bar( nav_list, level )    # Set the user navigation links

    gui_tree = gui_view_.get_view_location( level )

    al_command = app_view.get_tree_entree(gui_tree, "query")

    if not al_command:
        flash("AnyLog: Missing AnyLog Command in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options

    # Get the columns names of the table to show
    list_columns = app_view.get_tree_entree(gui_tree, "list_title")
    if not list_columns:
        flash("AnyLog: Missing 'list_columns' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options

   # Get the keys to pull data from the JSON reply
    list_keys = app_view.get_tree_entree(gui_tree, "list_keys")
    if not list_keys:
        flash("AnyLog: Missing 'list_keys' in '%s' Config file at lavel %u" % (Config.GUI_VIEW, level))
        return redirect(('/index'))        # Show all user select options
       

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
        # Let the user select view to see the JSON
        attributes ["view"] = LinkCol('view', 'view_policy', url_kwargs=args)

    if not app_view.is_edge_node(gui_tree):
        # provide select option
        args = dict(id='id')
        extra_args = {'level' : level + 1}
        attributes ["select"] = LinkCol('select', 'tree_move', url_kwargs=args, url_kwargs_extra=extra_args)
        
    TableClass = type ( 'AnyLogTable', (Table,), attributes)
    table = TableClass(table_rows)
    table.border = True

    return render_template('entries_list.html', table = table, private_gui = gui_view_.get_base_menu())
# -----------------------------------------------------------------------------------
# Select the children elements or move to parent
# -----------------------------------------------------------------------------------
@app.route('/tree_move/<string:id><int:level>')
def tree_move( id, level ):
    '''
    Select the children elements or move to parent
    '''
    pass

# -----------------------------------------------------------------------------------
# Show AnyLog Policy by ID
# -----------------------------------------------------------------------------------
@app.route('/view_policy/<string:id>')
def view_policy( id = None ):

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

    return render_template('output.html', title = 'Network Node Reply', text=data_list, private_gui = gui_view_.get_base_menu())

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

    target_node = query_node_ or gui_view_.get_query_node()
    if not target_node:
        flash("AnyLog: Missing query node connection info")
        return redirect(('/configure'))     # Get the query node info


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