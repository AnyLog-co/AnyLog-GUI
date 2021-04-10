
from flask import render_template, flash, redirect, request
from app import app
from app.forms import LoginForm
from app.forms import ConfigForm
from app.forms import CommandsForm
from app.forms import InstallForm
from app.entities import Companies
from app.entities import Item

import requests

from app import app_view        # maintains the logical view of the GUI from a JSON File
app_view.load_json()            # Load the definition of the user view of the metadata from a JSON file

user_connect_ = False       # Flag indicating connected to the AnyLog Node 
node_config_ = {}           # Config as f(company_name)
company_name_ = None        # Company to service



struct_info_ = {
    "title" : "",           # The title to display
    "cildren" : [],         # List of entriesm each entry is struct_info
    "query"   : "Query to pull the data"

}

# -----------------------------------------------------------------------------------
# GUI forms
# HTML Cheat Sheet - http://www.simplehtmlguide.com/cheatsheet.php
# -----------------------------------------------------------------------------------

@app.route('/')
@app.route('/index')
def index():
    if not user_connect_:
        return redirect(('/login'))        # start with Login
    
    return render_template('main.html', title = 'Home')
# -----------------------------------------------------------------------------------
# Machine
# -----------------------------------------------------------------------------------
@app.route('/machine')
def machine(company_name = None):
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

    return render_template('index.html', title = 'Home', metadata = metadata, builder = "Orics", customer = metadata["data"]["installation"]["customer"])

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

    return render_template('login.html', title = title_str, form = form)

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

    return render_template('companies.html', table = table)


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

    return render_template('reports.html', title = 'Orics')
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
    if form.validate_on_submit():
        flash('AnyLog: Network Member Node {}:{}'.format(form.node_ip, form.node_port))

    return render_template('configure.html', title = 'Configure Network Connection', form = form)

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
    
    return render_template('configure.html', title = 'Configure Network Connection', form = form)
# -----------------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------------
@app.route('/network')
def network():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    form = CommandsForm()         # New Form

    def_dest = "10.0.0.78:7848"

    return render_template('commands.html', title = 'Network Commands', form = form, def_dest=def_dest)


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
            return render_template('output.html', title = 'Network Node Reply', text=text)
  
    
    form = NetworkForm()         # New Form

    def_dest = "10.0.0.78:7848"
    
    return render_template('network.html', title = 'Network Status', form = form, def_dest=def_dest)

@app.route('/install', methods = ['GET', 'POST'])
def install():
  
    form = InstallForm()         # New Form
    return render_template('install.html', title = 'Install Network Node', form = form)