class General:
    DATABASE = 'rankset'
    DEFAULT_USER = 'root'
    DEFAULT_PASSWORD = 'password'
    HOST = 'host'
    DEFAULT_HOST = '127.0.0.1'


class Keys:
    STATUS_CODE = 'status_code'
    DATA_TYPE = 'data_type_name'
    DATA = 'data'
    COUNTRIES = 'countries'
    COMPETITIONS = 'competitions'
    TEAMS = 'teams'
    PLAYERS = 'players'
    OVERVIEW = 'overview'
    STATS = 'stats'
    POSITION = 'position'
    COUNT_OF_GAMES = 'count_of_games'
    BASE_DATA = 'base_data'
    TM_DATA = 'tm_data'
    FM_DATA = 'fm_data'
    NAME = 'name'
    MARKET_VALUE = 'market_value'
    ACHIEVEMENTS = 'achievements'
    TM_HISTORY = 'transfer_history'
    TM_INJURY = 'injury_stats'
    ATTRIBUTES = 'player_attributes'
    TEAM_ID = 'team_id'
    NOT_FOUND_DATA = 'Not found data'
    ERROR = 'error'


class Routs:
    ENTITIES = 'entities'
    PLAYERS = 'players'


class FilterData:
    DEFAULT_STATS = ['minutes on field', 'goal', 'xg shot', 'assist', 'pre assist', 'shot assist', 'interception',
                     'yellow cards', 'red cards']
