from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

login = LoginManager()
db = SQLAlchemy()
mail = Mail()