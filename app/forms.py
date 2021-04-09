
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')
    submit = SubmitField('Sign In')

class ConfigForm(FlaskForm):
    node_ip = StringField('IP', validators=[DataRequired()])
    node_port = StringField('Port', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')
    submit = SubmitField('Save')
