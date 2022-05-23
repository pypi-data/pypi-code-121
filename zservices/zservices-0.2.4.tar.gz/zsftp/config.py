import os
from dotenv import load_dotenv

load_dotenv(override=False)


class Config:
    APP_NAME = os.getenv('APP_NAME', 'SFTP')

    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'PRODUCTION')
    REGION = os.getenv('REGION', 'IND')
    LANGUAGE = os.getenv('APP_LANGUAGE', 'EN')

    # Log
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # AWS
    SFTP = {
        'hostname': os.getenv('SFTP_HOSTNAME'),
        'username': os.getenv('SFTP_USERNAME'),
        'password': os.getenv('SFTP_PASSWORD'),
    }
