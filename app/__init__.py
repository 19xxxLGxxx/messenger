from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = 'abcd'

    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    elif not database_url:
        database_url = f"sqlite:///{os.path.join('/tmp', 'db.db')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_DEFAULT_SENDER'] = 'laramariegeyer@gmail.com'
    app.config['MAIL_USERNAME'] = '8afe4e49962d19'
    app.config['MAIL_PASSWORD'] = '6198c872f723aa'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    # app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
    # app.config['MAIL_DEFAULT_SENDER'] = 'hello@lara-geyer.de'
    # app.config['MAIL_PORT'] = 587
    # app.config['MAIL_USERNAME'] = 'api'
    # app.config['MAIL_PASSWORD'] = '...'
    # app.config['MAIL_USE_TLS'] = True
    # app.config['MAIL_USE_SSL'] = False

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

    with app.app_context():
        from .models import User, Message
        db.create_all()

    return app
