import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Pfad zur Konfigurationsdatei für gespeicherte Eingaben
CONFIG_FILE = os.path.join(basedir, 'config.json')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
