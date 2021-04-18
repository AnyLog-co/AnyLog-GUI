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

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')
    submit = SubmitField('Sign In')

class ConfigForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    node_ip = StringField('Node IP', validators=[DataRequired()])
    node_port = IntegerField('Node Port', validators=[DataRequired()])
    reports_ip = StringField('Reports IP', validators=[DataRequired()])
    reports_port = IntegerField('Reports Port', validators=[DataRequired()])

    remember_me = BooleanField('Remember_me')
    submit = SubmitField('Save')

class CommandsForm(FlaskForm):

    command = StringField('Command', validators=[DataRequired()])
    destination = StringField('Destination (IP:Port)', validators=[])
  
    submit = SubmitField('Submit')

class InstallForm(FlaskForm):
    connect_ip = StringField('New Node IP', validators=[DataRequired()])
    connect_port = IntegerField('New Node Port', validators=[DataRequired()])
    connect_pwd = StringField('New Node Password', validators=[DataRequired()])
    is_operator = BooleanField('Operator')
    is_publisher = BooleanField('Publisher')
    is_query = BooleanField('Query')
    is_master = BooleanField('Master')
    deploy = SubmitField('Deploy')

class ConfDynamicReport(FlaskForm):
    
    report_name = SelectField('Select Report', default="")
    new_report = StringField('New Report', default="")
    rename = StringField('Rename Report', default="")
    make_default = BooleanField('Set as Default', default=False)
    reset = BooleanField('Reset Report', default=False)
    delete = BooleanField('Delete Report', default=False)
    submit = SubmitField('Apply Changes')

