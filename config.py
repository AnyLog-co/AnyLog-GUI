
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'missing_key'
    GUI_VIEW = os.environ.get('GUI_VIEW') or 'D:/AnyLog-Code/AnyLog-GUI/views/machines.json'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'D:/AnyLog-Code/AnyLog-GUI/views/'