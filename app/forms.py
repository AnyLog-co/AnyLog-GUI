
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField
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
    report_name = StringField('Report Name', validators=[DataRequired()])
    new_name = StringField('New Name')
    make_default = BooleanField('Set as Default')
    reset = BooleanField('Reset Report')
    deploy = SubmitField('Apply Changes')

