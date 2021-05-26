
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'missing_key'

    # Add slash to end of dir
    CONFIG_FOLDER = os.environ.get('CONFIG_FOLDER')
    if CONFIG_FOLDER and CONFIG_FOLDER[-1] != '/' and CONFIG_FOLDER[-1] != '\\':
        CONFIG_FOLDER += '/'

    # Add .json
    CONFIG_FILE = os.environ.get('CONFIG_FILE')
    if CONFIG_FILE:
        index = CONFIG_FILE.find('.')
        if index == -1:
            CONFIG_FILE += '.json'


    if CONFIG_FOLDER and CONFIG_FILE:
        GUI_VIEW = CONFIG_FOLDER + CONFIG_FILE
    else:
        GUI_VIEW = None

