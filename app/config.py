import os

# Basispfad dieses Moduls (app/)
basedir = os.path.abspath(os.path.dirname(__file__))
# Projekt-Root eine Ebene darüber
project_root = os.path.abspath(os.path.join(basedir, os.pardir))

# Pfad zur JSON‑Konfigurationsdatei im Projekt‑Root
CONFIG_FILE = os.path.join(project_root, 'config.json')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(project_root, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
