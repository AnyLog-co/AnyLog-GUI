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

# https://exploreflask.com/en/latest/forms.html
import getpass
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ConfigForm(FlaskForm):

    conf_file_name = SelectField('Select File', default="")
    node_ip = StringField('Node IP')
    node_port = IntegerField('Node Port')
    submit = SubmitField('Apply')

class CommandsForm(FlaskForm):

    command = StringField('Command', validators=[DataRequired()])
    destination = StringField('Destination (IP:Port)', validators=[])
  
    submit = SubmitField('Submit')


# Time configuration for a panel or a report
class TimeConfig():
    def __init__(self, time_options, text_selected, time_selected, default_from, default_to):
        '''
        time_options - the list of predefined time range
        text_selected - The text selected from the list
        time_selected - the key of the selected text
        default_from - start date and time
        default_to - end date and time
        '''
        self.time_options = time_options
        self.text_selected = text_selected  # Last 2 months
        self.time_selected = time_selected # i.e. now-2M
        self.default_from = default_from
        self.default_to = default_to

# Type of queries for the panel
class PanelConfig():

    def __init__(self, name, panel_type, options, selected):
        self.name = name        # The name of the panel on the config page (not the panel name when report is requested)
        self.panel_type = panel_type      # Graph, Gauge
        self.chek_box_options = options             # a list - Each entry represents a checkbox option
        self.chek_box_selected = selected           # a list - Each entry represent a selected option
        self.time_config = None      # Time selection for the panel (if different than dashboard)


class DashboardConfig():
    def __init__(self):
        self.panels = []        # List of panels
        self.time_config = None  # Time selection for the dashboard

    def add_panel(self, new_panel):
        self.panels.append(new_panel)
    def set_time(self, time_config):
        self.time_config = time_config  # Time selection for the dashboard



class ConfDynamicReport(FlaskForm):
    report_name = SelectField('Select Report', default="")
    new_report = StringField('New Report', default="")
    rename = StringField('Rename Report', default="")
    make_default = BooleanField('Set as Default', default=False)
    reset = BooleanField('Reset Report', default=False)
    delete = BooleanField('Delete Report', default=False)
    submit = SubmitField('Apply Changes')


class InstallForm(FlaskForm):
    # Basic SCP/SSH connection information
    """
    Process used for: 
    1. SCP of config to new machine 
    2. SSH command to start AnyLog with new config
    """ 
    conn_info   = StringField('Connection Information [format: user@ip]: ', default='%s@127.0.0.1' % getpass.getuser(), validators=[DataRequired()])
    conn_port   = IntegerField('Connection Port: ', default=22, validators=[Optional()]) 
    conn_passwd = StringField('Connection Password: ', validators=[DataRequired()])
    
    # Basic AnyLog Params
    """
    Issues: 
    1. for company name there should be an copy of it where dashses (-) and spackes ( ) are repalced with underscore (_) - the word should also be lower case 
    2. node_name should have a default value that's ${company_name}-${node_type}
    """
    build_type   = StringField('Build Type [options: alpine, debian, centos]: ', default='debian', validators=[Optional()])
    #node_type    = StringField('Node Type [options: master, operator, publisher, query]: ', default='operator', validators=[Optional()]) 
    is_master    = BooleanField('Master') 
    is_operator  = BooleanField('Operator') 
    is_publisher = BooleanField('Publisher') 
    is_query     = BooleanField('Query')
    company_name = StringField('Company Name: ', validators=[DataRequired()])
    node_name    = StringField('Node Name: ', validators=[DataRequired()])  
    
    # Autentication 
    """
    Issue
    1. authentication_user_info should be disabled if set_authentication is False  
    """
    set_authentication       = BooleanField('Enable REST Authentication: ', default=False, validators=[Optional()])
    authentication_user_info = StringField('REST authentication Info [format: user:passwd]: ', validators=[DataRequired()]) 

    # Networking 
    """
    Note
    1. Master node is set (by default) to our demo env 
    Issue
    1. anylog_broker_port should disbaled if local_broker isn't enabled 
    2. local_broker/ anylog_broker_port should be enabled only when node_type is Operator || Publisher 
    """
    master_node        = StringField('Master Node: ', default='45.33.41.185:2048', validators=[Optional()]) 
    anylog_tcp_port    = IntegerField('AnyLog TCP Port: ', default=2048, validators=[Optional()]) 
    anylog_rest_port   = IntegerField('AnyLog REST Port: ', default=2049, validators=[Optional()]) 
    local_broker       = BooleanField('Enable Local Broker: ', default=False, validators=[Optional()])
    anylog_broker_port = IntegerField('AnyLog Broker Port: ', default=2050, validators=[Optional()])

    # Cluster Information 
    """
    Issues 
    1. The following information should appear only if node_type is Operator
    2. If cluster is enabled, assert either Cluster ID || New cluster ifnormation is set
    """
    enable_cluster = BooleanField('Enable Cluster: ', default=True) 
    cluster_id     = StringField('Cluster ID: ', validators=[Optional()]) # Existing cluster 
    cluster_name   = StringField('Cluster Name: ', validators=[Optional()]) # New cluster 
    table          = StringField('Comma Seperated Tables: ', validators=[Optional()]) # New cluster 

    # Database Information 
    """
    1. default DBMS should be set only when node_type is Operator
    2. for default_dbms, there should be default value set to formatted_company_name
    3. db_type should be sqlite if build_type is alpine
    4. db_user default should be formatted_company_name
    """
    default_dbms = StringField('Database Name (Operator Only): ', validators=[Optional()]) 
    #db_type      = StringField('Database Type [options: psql, sqlite]: ', default="psql", validators=[DataRequired()])
    is_psql      = BooleanField('Postgres')
    is_sqlite    = BooleanField('SQLite')
    db_user      = StringField('Database Credentials [format: user@ip:passwd]: ', default='admin@127.0.0.1:demo', validators=[DataRequired()])
    db_port      = IntegerField('Database Port: ', default=5432, validators=[DataRequired()]) 

    # MQTT Information 
    """
    Notes
    1. MQTT defaults are set to our example 
    Issue
    1. If local broker is enabled, mqtt_enable should 
       a) be enabled by default 
       b) conn_info should have a default of "local" with port matching anylog_broker_port
    """
    mqtt_enable       = BooleanField('Enable MQTT: ')
    mqtt_enable_other = BooleanField('Extract data from other MQTT topics - same connection info: ')
    mqtt_conn_info    = StringField('MQTT connection info [format: user@broker:passwd]: ', default='mqwdtklv@driver.cloudmqtt.com:uRimssLO4dIo', validators=[Optional()])
    mqtt_conn_port    = IntegerField('MQTT connection port: ', default=18975, validators=[Optional()])
    mqtt_log          = BooleanField('Enable MQTT Log: ')
    mqtt_topic_name   = StringField('MQTT Topic: ', validators=[DataRequired()]) 

    # The following are optional configs for MQTT - if 1 or more isn't set the code will store data as raw
    mqtt_topic_dbms        = StringField('Database Name: ', validators=[Optional()]) 
    mqtt_topic_table       = StringField('MQTT Table Name [example: bring [metadata][machine_name]]: ', validators=[Optional()])
    mqtt_column_timestamp  = StringField('MQTT Timestamp column [example: bring [ts]: ', validators=[Optional()])
    mqtt_column_value_type = StringField('MQTT Value column type [options: str, int, timestamp, bool]: ', validators=[Optional()])
    mqtt_column_value      = StringField('MQTT Value column [example: bring [ts]]: ', validators=[Optional()])
    mqtt_extra_column      = StringField("Any other columns to extract from MQTT data [example: and column.new_column.str='and bring [new_column]': ", validators=[Optional()])

    #is_master = BooleanField('Master')
    deploy = SubmitField('Deploy')





