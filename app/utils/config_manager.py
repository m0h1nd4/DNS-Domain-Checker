import json
import os
from app.config import CONFIG_FILE

DEFAULT_CONFIG = {
    "parts": {
        "must": [],
        "should": [],
        "can": []
    },
    "tlds": [],
    "selected_tlds": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
