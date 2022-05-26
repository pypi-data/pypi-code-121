template = """
DB_NAME=ms-name
DB_ENGINE=mysql+pymysql
DB_USER=ms-user
DB_PASSWORD=ms-pass
DB_HOST=127.0.0.1
DB_PORT=3306

JWT_SECRET_KEY=%(secret)s

REGISTER=http://ip_node:5555/ms/register
MS_HOST=https://ip_ms:5000

HOST=localhost
PORT=5000
DEBUG=false
"""
