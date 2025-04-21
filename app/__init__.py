from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.frontend.routes import frontend_bp
    app.register_blueprint(frontend_bp)

    # Tabellen automatisch anlegen, falls noch nicht vorhanden
    with app.app_context():
        # Sicherstellen, dass alle Model-Klassen importiert sind
        from app.models import Check
        db.create_all()

    return app
