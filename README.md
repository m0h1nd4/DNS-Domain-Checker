# DNS-Domain-Checker

A Flask-based web application that allows you to generate domain name combinations from user‑defined parts and TLDs, check their DNS availability against public resolvers, and store the results in a SQLite database. It comes with a modern dark-themed UI.

## Features

- **Domain Parts Input**  
  - Define "must", "should", and "can" parts for your domain names.
- **Combination Generator**  
  - Generates all combinations of your parts, with optional separators (`none`, `-`, `_`).
  - Slider to limit how many combinations are shown; checkbox to force showing all.
  - Heatmap indicator of combination count (green → few, red → many).
- **TLD Import & Selection**  
  - Import TLDs via JSON list or comma-separated text.
  - Paginated, scrollable checklist to select which TLDs to check.
- **DNS Lookup**  
  - Checks each selected combination + TLD against public DNS servers (8.8.8.8, 1.1.1.1).
  - Marks available names in green (✓ verfügbar) and taken names in red (✗ belegt), displaying returned IP addresses.
- **Persistence**  
  - Stores each check (domain base, TLD, status, IP, timestamp) in a `checks` table within `app.db` (SQLite).
  - Saves your UI configuration in two JSON files:
    - `config.json` for domain parts & TLD lists.
    - `config-domain.json` for combination settings and selections.
- **Modular & Extendable**  
  - Clean separation of concerns:  
    - `app/utils/` for config managers  
    - `app/services/` for DNS lookup  
    - `app/api/` and `app/frontend/` for routes  
    - `app/models.py` for data models  
  - Dark theme via Bootstrap + custom CSS.

## Prerequisites

- Python 3.7 or higher  
- `pip` package manager  

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/m0h1nd4/DNS-Domain-Checker.git
   cd DNS-Domain-Checker.git
   ```

2. **Create & activate a virtual environment (recommended)**  
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- **Database**  
  By default, uses SQLite file `app.db` in the project root. To use another database, set the environment variable `DATABASE_URL` (e.g., PostgreSQL).

- **Config Files**  
  - `config.json` will be created on first run to hold your domain parts and TLD list.  
  - `config-domain.json` will be created on first run to hold combination settings and selected combinations.  

  You don’t need to edit these by hand; the UI manages them.

## Usage

1. **Start the development server**  
   ```bash
   python run.py
   ```
   The app will run at [http://127.0.0.1:5000](http://127.0.0.1:5000).

2. **Navigate the UI**  
   - **Bestandteile** (Home): Enter your “must”, “should”, and “can” domain parts.  
   - **Kombinationen**:  
     - View how many name combinations are possible.  
     - Use the slider or “Alle Kombinationen anzeigen” checkbox to control how many to list.  
     - Select the combinations you want to check.  
   - **TLD‑Import**: Paste your TLD list (JSON or CSV).  
   - **TLD‑Auswahl**: Quickly select which TLDs to include in the check.  
   - **Ergebnisse**: See a table of each `combination.tld`, status (✓ verfügbar / ✗ belegt), and IP.

3. **Resetting Config**  
   If you wish to start fresh, delete `config.json`, `config-domain.json`, and/or `app.db` before restarting the app.

## Project Structure

```
flask_dns_checker/
├── app/
│   ├── __init__.py           # App factory, DB init
│   ├── config.py             # Config class + paths
│   ├── models.py             # SQLAlchemy models
│   ├── api/
│   │   └── routes.py         # (Unused placeholder for JSON API)
│   ├── frontend/
│   │   └── routes.py         # All HTML page routes
│   ├── services/
│   │   └── dns_lookup.py     # DNS resolver logic
│   └── utils/
│       ├── config_manager.py       # Manages config.json
│       └── domain_config_manager.py# Manages config-domain.json
├── static/
│   └── css/
│       └── dark-theme.css    # Custom dark theme
├── templates/
│   ├── base.html             # Main layout + nav
│   ├── parts.html            # Domain parts input
│   ├── combinations.html     # Combination generation & selection
│   ├── tlds_import.html      # TLD import
│   ├── tlds_select.html      # TLD selection
│   └── results.html          # DNS check results
├── config.json               # Auto‑generated user config
├── config-domain.json        # Auto‑generated combination config
├── app.db                    # SQLite database
├── requirements.txt          # Python dependencies
└── run.py                    # Entry point
```

## Extending & Customization

- **Add More DNS Record Types**  
  Modify `app/services/dns_lookup.py` to check MX, AAAA, etc.

- **API Endpoints**  
  The `app/api/routes.py` module is scaffolded—feel free to expose JSON endpoints for headless usage.

- **Styling**  
  Edit `static/css/dark-theme.css` or swap in another Bootstrap theme.

## License

MIT License. Feel free to use and modify.
