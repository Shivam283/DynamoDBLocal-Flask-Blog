import os
path = os.getcwd()

"""Flask configuration."""

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
SECRET_KEY = 'dev'
UPLOAD_FOLDER = path + '/Blog/static/images/'