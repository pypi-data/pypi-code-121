from pathlib import Path

LOGIN_URL = "/auth/jwt/login"
CREDENTIALS_FILE = Path.home() / ".config" / "iris" / "credentials.json"

BASE_URL_ENV = "IRIS_BASE_URL"
USERNAME_ENV = "IRIS_USERNAME"
PASSWORD_ENV = "IRIS_PASSWORD"

PAGINATION_DATA_KEY = "results"
PAGINATION_NEXT_KEY = "next"
