import json
import os
from app.config import project_root

DOMAIN_CONFIG_FILE = os.path.join(project_root, 'config-domain.json')

DEFAULT_DOMAIN_CONFIG = {
    "max_combinations": 20,
    "force_all": False,
    "combinations": [],
    "selected_combinations": []
}

def load_domain_config():
    if not os.path.exists(DOMAIN_CONFIG_FILE):
        return DEFAULT_DOMAIN_CONFIG.copy()
    with open(DOMAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_domain_config(cfg):
    with open(DOMAIN_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
