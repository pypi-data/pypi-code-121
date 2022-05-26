template = """# generado automaticamente

import os
import sys
from dotenv import load_dotenv

envfile = "../{}".format(os.getenv("ENVFILE", ".env"))

dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=os.path.join(dir_path, envfile), verbose=True, override=True)

def parse_url_db(engine, user, password, host, port, name):
    return f"{engine}://{user}:{password}@{host}:{port or 3306}/{name}?charset=UTF8MB4&autocommit=false"

TESTING = False
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", 'development')

NAME     = os.getenv("NAME", os.getenv("HOSTNAME"))
HOST     = os.getenv("HOST", "localhost")
PORT     = os.getenv("PORT", 5000)
REGISTER = os.getenv("REGISTER", "http://ip_node")
MS_HOST = os.getenv("MS_HOST")
DEBUG = os.getenv("DEBUG", False)

DB_ENGINE = os.getenv("DB_ENGINE", "mysql+pymysql")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", parse_url_db(
    engine=DB_ENGINE,
    name=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
    host=DB_HOST
))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 490,
    "pool_pre_ping": 60,
}

INSTALLED_APPS = [
    "app.%(app)s",
]
"""
