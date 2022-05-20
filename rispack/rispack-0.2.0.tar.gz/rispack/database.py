import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from rispack.aws import get_proxy_token, get_secret


class DatabaseCredentialError(RuntimeError):
    pass


class Database:
    def __init__(
        self,
        user: str = None,
        endpoint: str = None,
        port: int = None,
        name: str = None,
        use_proxy: bool = None,
        secret_arn: str = None,
    ) -> None:
        self._session = None
        self.user = user or os.environ.get("DB_USER")
        self.endpoint = endpoint or os.environ.get("DB_ENDPOINT")
        self.port = port or os.environ.get("DB_PORT")
        self.name = name or os.environ.get("DB_NAME")
        self.proxy = use_proxy or os.environ.get("DB_USE_PROXY", False)
        self.secret_arn = secret_arn or os.environ.get("DB_SECRET_ARN", None)
        self.region = os.environ.get("AWS_REGION")

        if not self.proxy and not self.secret_arn:
            raise DatabaseCredentialError(
                "You must provide DB_SECRET_ARN or set DB_USE_PROXY environment variable."
            )

    @property
    def session(self):
        if self._session:
            return self._session

        self._session = self.create_session()

        return self._session

    def create_session(self):
        password = None

        if self.use_proxy:
            password = self.get_proxy_password()
        else:
            password = self.get_secret_password()

        conn = "postgresql://%s:%s@%s:%s/%s".format(
            self.user, password, self.endpoint, self.port, self.name
        )

        engine = create_engine(conn)
        session = Session(engine, future=True)

        return session

    def get_proxy_password(self):
        return get_proxy_token(endpoint=self.endpoint, port=self.port, user=self.user)

    def get_secret_password(self):
        secret = get_secret(self.secret_arn)

        password = json.loads(secret).get("password")

        return password
