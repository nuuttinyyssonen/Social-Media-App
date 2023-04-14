from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


SECRET_KEY = environ.get('SECRET_KEY')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'nuutti.project@gmail.com'
MAIL_DEFAULT_SENDER = 'nuutti.project@gmail.com'
MAIL_MAX_EMAIL = None
MAIL_ASCII_ATTACHMENT = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///my_database.db'