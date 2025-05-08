from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "..", "instance", "db.db")

    app = Flask(__name__, template_folder="templates")
    print("Template-Pfad:", app.template_folder)
    app.secret_key = 'abcd'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
