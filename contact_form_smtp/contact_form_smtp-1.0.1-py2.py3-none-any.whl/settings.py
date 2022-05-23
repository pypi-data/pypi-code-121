from starlette.config import Config

# load variables from .env if it exists
config = Config(".env")

# debug flags

DEBUG = config("DEBUG", cast=bool, default=False)
HOST = config("HOST", cast=str, default="0.0.0.0")
PORT = config("PORT", cast=int, default=80)
SMTP_SERVER = config("SMTP_SERVER", cast=str, default="smtp")
LOG_LEVEL = config("LOG_LEVEL", cast=str, default="INFO")
