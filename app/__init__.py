

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes          # Routes includes the implemented URLs

@app.route('/')
def hello():
    return 'Hello, World!'
