from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import os
import sys

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates")
    app.secret_key = 'abcd'

    if test_config:
        app.config.update(test_config)
    else:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL fehlt.", file=sys.stderr)
            sys.exit(1)

        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
        app.config['MAIL_DEFAULT_SENDER'] = 'hello@lara-geyer.de'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USERNAME'] = 'api'
        app.config['MAIL_PASSWORD'] = 'd5bd2752336246fc91e61c75020eb010'
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'main.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    if not test_config:
        with app.app_context():
            from .models import User, Message
            db.create_all()

    return app
