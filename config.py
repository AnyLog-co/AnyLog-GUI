
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'missing_key'

    CONFIG_FOLDER = os.environ.get('CONFIG_FOLDER') or 'D:/AnyLog-Code/AnyLog-GUI/views/'
    CONFIG_FILE = os.environ.get('CONFIG_FILE') or "machines.json"

    GUI_VIEW = os.environ.get('GUI_VIEW')

    if not GUI_VIEW:
        GUI_VIEW = CONFIG_FOLDER + CONFIG_FILE

