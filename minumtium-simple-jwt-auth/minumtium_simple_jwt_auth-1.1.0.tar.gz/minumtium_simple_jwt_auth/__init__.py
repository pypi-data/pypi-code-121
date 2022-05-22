from datetime import datetime, timedelta
from string import punctuation
from typing import List

import bcrypt
import jwt
from minumtium.infra.authentication import AuthenticationAdapter, AuthenticationException
from minumtium.infra.database import DatabaseAdapter, DataNotFoundException
from minumtium.modules.idm import Session, MAX_LOGIN_TRIALS, LOGIN_COOLDOWN_MINUTES
from pydantic import BaseModel


class MinumtiumSimpleJwtAuthenticationConfig(BaseModel):
    jwt_key: str
    session_duration_hours: int = 6


class MinumtiumSimpleJwtAuthentication(AuthenticationAdapter):
    """
    A simple adapter for authenticating with a JWT token.
    """
    PASSWORD_CHARS = 12
    SESSION_DURATION_FORMAT = '%Y%m%d%H%M%S%f'
    ALGORITHM = 'HS256'
    DEFAULT_USERNAME = 'minumtium'
    DEFAULT_PASSWORD = 'minumtium'

    def __init__(self, config: MinumtiumSimpleJwtAuthenticationConfig, db: DatabaseAdapter):
        self.secret: str = config.jwt_key
        self.session_duration: int = config.session_duration_hours
        self.db: DatabaseAdapter = db
        self.trials = {}
        self._initialize_default_user()

    def _initialize_default_user(self):
        def user_list(db: DatabaseAdapter) -> List[str]:
            return [user['username'] for user in db.all()]

        def has_default_user(db: DatabaseAdapter):
            return MinumtiumSimpleJwtAuthentication.DEFAULT_USERNAME not in user_list(db)

        def insert_default_user(db: DatabaseAdapter):
            encrypted_password = self.encrypt_password(MinumtiumSimpleJwtAuthentication.DEFAULT_PASSWORD)
            user = {'username': MinumtiumSimpleJwtAuthentication.DEFAULT_USERNAME,
                    'encrypted_password': encrypted_password}
            db.insert(user)

        if has_default_user(self.db):
            insert_default_user(self.db)

    def validate_token(self, token: str) -> Session:
        try:
            token_data = jwt.decode(token.encode('utf-8'),
                                    self.secret,
                                    algorithms=MinumtiumSimpleJwtAuthentication.ALGORITHM)
            token_expiration_date = token_data['expiration_date']
            token_username = token_data['username']
            token_user_id = token_data['userid']

            user = self.db.find_by_id(token_user_id)
            if self.__is_session_expired(token_expiration_date):
                raise RuntimeError('Session expired.')

            if user['username'] != token_username:
                raise RuntimeError('Invalid username.')

            return Session(
                user_id=user['id'],
                username=user['username'],
                expiration_date=self.__parse_expiration_date(token_expiration_date))

        except Exception as e:
            raise AuthenticationException(
                'Invalid authentication token provided.') from e

    def __is_session_expired(self, expiration_date: str) -> bool:
        return self.__parse_expiration_date(expiration_date) < datetime.now()

    @staticmethod
    def __parse_expiration_date(expiration_date: str) -> datetime:
        return datetime.strptime(expiration_date, MinumtiumSimpleJwtAuthentication.SESSION_DURATION_FORMAT)

    def authenticate(self, username: str, password: str) -> str:
        try:
            user = self.db.find_by_criteria({'username': username})[0]
        except DataNotFoundException as e:
            raise AuthenticationException(
                'Invalid username and/or password.') from e

        self.__count_login_trial(username)
        if self.__is_allowed_to_login(username, password, user['encrypted_password']):
            return self.__generate_token(username, user['id'], self.secret)
        raise AuthenticationException('Invalid username and/or password.')

    def __is_allowed_to_login(self, username: str, password: str, encrypted_password: str):
        if self.__is_valid_password(password, encrypted_password) and not self._is_max_trials_expired(username):
            self.__initialize_trial(username)
            return True
        return False

    def _is_max_trials_expired(self, username: str):
        if username not in self.trials:
            return False

        count = self.trials[username]['count']
        timestamp = self.trials[username]['timestamp']
        return count > MAX_LOGIN_TRIALS and timestamp + timedelta(minutes=LOGIN_COOLDOWN_MINUTES) > datetime.now()

    def __count_login_trial(self, username: str):
        if username not in self.trials:
            self.__initialize_trial(username)
        self.trials[username]['count'] += 1
        self.trials[username]['timestamp'] = datetime.now()

    def __initialize_trial(self, username: str):
        self.trials[username] = {'count': 0, 'last_trial': datetime.now()}

    @staticmethod
    def __is_valid_password(provided: str, expected: str):
        return bcrypt.checkpw(provided.encode('utf-8'), expected.encode('utf-8'))

    def __generate_token(self, username: str, user_id: str, secret: str):
        return jwt.encode({
            'username': username,
            'userid': user_id,
            'expiration_date': self.__generate_expiration_date().strftime(
                MinumtiumSimpleJwtAuthentication.SESSION_DURATION_FORMAT)
        }, secret, algorithm=MinumtiumSimpleJwtAuthentication.ALGORITHM)

    def __generate_expiration_date(self):
        return datetime.now() + timedelta(hours=self.session_duration)

    def encrypt_password(self, password: str) -> str:
        password = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=14)
        hashed_password = bcrypt.hashpw(password, salt)
        return hashed_password.decode('utf-8')

    def is_valid_password(self, password: str) -> bool:
        return len(password) >= MinumtiumSimpleJwtAuthentication.PASSWORD_CHARS and \
               any(char.islower() for char in password) and \
               any(char.isupper() for char in password) and \
               any(char.isdigit() for char in password) and \
               any(char in punctuation for char in password)

    def get_password_criteria(self):
        return f'minimum of {MinumtiumSimpleJwtAuthentication.PASSWORD_CHARS} chars, at least 1 uppercase, ' \
               f'1 lowercase, a number and a symbol '
