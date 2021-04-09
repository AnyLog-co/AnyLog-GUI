
from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
from app.forms import CompanyForm

import requests

user_connect_ = False       # Flag indicating connected to the AnyLog Node 

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

@app.route('/machine')
def machine():
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

al_reply = None
@app.route('/login', methods={'GET','POST'})
def login():
    '''
    Inpuit login name & password, connecet to a node in the network
    and move to main page to determine GUI to use
    '''
    global user_connect_
    form = LoginForm()
    if form.validate_on_submit():
        flash('login requested for user {}, remember_me-={}'.format(
            form.username.data, form.remember_me.data))

        al_headers = {
            'command' : 'get status',
            'User-Agent' : 'AnyLog/1.23'
            }

        try:
            response = requests.get('http://10.0.0.78:7849', headers=al_headers)
        except:
            flash('AnyLog: No network connection')
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

    return render_template('login.html', title = 'Sign In', form = form)

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
        if response.status_code == 200:
            data = response.text
            if data and len(data) > 21:
                companies = list(filter(None, data[21:-2].split(',')))
        else:
            companies = []

    return render_template('companies.html', title = 'Company', companies = companies)

@app.route('/sensor')
def sensor():
    return redirect(('/login'))        # start with Login if not yet provided

@app.route('/reports')
def reports():
    if not user_connect_:
        return redirect(('/login'))        # start with Login  if not yet provided

    return render_template('reports.html', title = 'Orics')

@app.route('/alerts')
def alerts():
    return redirect(('/login'))        # start with Login if not yet provided

@app.route('/configure')
def configure():
    return redirect(('/login'))        # start with Login if not yet provided

@app.route('/network')
def network():
    return redirect(('/login'))        # start with Login if not yet provided
