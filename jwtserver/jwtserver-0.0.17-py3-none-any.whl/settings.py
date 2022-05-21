from functools import lru_cache
from pydantic import BaseSettings, BaseModel, RedisDsn, PostgresDsn, PyObject
from jwtserver.internal.SMSC import SMSModel


class TokenModel(BaseModel):
    base_sol: str = '1234567890987654321'
    secret_key: str = None
    algorithm: str = 'HS256'
    access_expire_time: int = 90  # minutes
    refresh_expire_time: int = 10800  # minutes


class PostgresConfig(BaseModel):
    # pg_dsn: PostgresDsn = 'postgresql+asyncpg://jwtserver:jwtserver-password@localhost:5433/jwtserver-tests'
    pg_dsn: PostgresDsn = None
    # pg_dsn_sync: PostgresDsn = 'postgresql://jwtserver:jwtserver-password@localhost:5433/jwtserver-tests'
    pg_dsn_sync: PostgresDsn = None


class RedisConfig(BaseModel):
    # redis_dsn: RedisDsn = 'redis://:@localhost:6379/1'
    redis_dsn: RedisDsn = None
    max_connections: int = 10


class RecaptchaModel(BaseModel):
    secret_key: str = 'uudud'
    score: float = 0.7
    for_tests: bool = False


class GoogleConfig(BaseModel):
    Recaptcha: RecaptchaModel = RecaptchaModel()


class ServerConfig(BaseModel):
    # domain: Set[str] = set()
    host: str = '0.0.0.0'
    port: int = 8000
    max_requests: int = 1000
    debug: bool = True


a = ServerConfig()

class Settings(BaseSettings):
    environment: str = 'production'
    server: ServerConfig = ServerConfig()
    token: TokenModel = TokenModel()
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    Google: GoogleConfig = GoogleConfig()
    sms: SMSModel = SMSModel()

    class Config:
        env_file = '.env'
        env_nested_delimiter = '__'
        # env_prefix = ''


@lru_cache()
def get_settings():
    return Settings()

# def get_config():
#     raise NotImplementedError

# @lru_cache
# class Settings:
#     def __init__(self, _config=None):
#         self.config = _config or self.load_config()
#
#     def __call__(self, *args, **kwargs) -> ConfigModel:
#         return self.config
#
#     @staticmethod
#     def load_config() -> ConfigModel:
#         """
#         Load default and user config. Merge configs (override default values) and typing.
#         :return: merge configs.
#         :rtype: Config.
#         """
#
#         # Load default.ini file and parsing.
#         default_ini = pkg_resources.open_text(jwtserver, 'default.ini')
#         default_cfg = configparser.ConfigParser()
#         default_cfg.read_file(default_ini)
#
#         # Load config.ini file (User config) and parsing.
#         user_ini = configparser.ConfigParser()
#         user_ini.read('config.ini')
#
#         # Merge dicts.
#         merged_dict = defaultdict(dict)
#         merged_dict.update(default_cfg)
#
#         for key, nested_dict in user_ini.items():
#             merged_dict[key].update(nested_dict)
#
#         return ConfigModel(**dict(merged_dict))
#
#     def get_config(self) -> ConfigModel:
#         return self.config
#
#     def get_tests_config(self) -> ConfigModel:
#         db_url = 'jwtserver:jwtserver-password@localhost:5433/jwtserver-tests'
#         self.config.redis.url = "redis://:@localhost:6380/1"
#         self.config.db.sync_url = f"postgresql://{db_url}"
#         self.config.db.async_url = f"postgresql+asyncpg://{db_url}"
#         return self.config
