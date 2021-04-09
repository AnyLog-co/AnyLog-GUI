
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

class NetworkForm(FlaskForm):

    command = StringField('Command', validators=[DataRequired()])
    destination = StringField('Destination (IP:Port)', validators=[])
  
    submit = SubmitField('Submit')
