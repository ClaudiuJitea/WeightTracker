from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from app.extensions import db, migrate, login

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.weight import bp as weight_bp
    app.register_blueprint(weight_bp, url_prefix='/weight')

    from app.calories import bp as calories_bp
    app.register_blueprint(calories_bp, url_prefix='/calories')

    from app.fasting import bp as fasting_bp
    app.register_blueprint(fasting_bp, url_prefix='/fasting')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

from app import models