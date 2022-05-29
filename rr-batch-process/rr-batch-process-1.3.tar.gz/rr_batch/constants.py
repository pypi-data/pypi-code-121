class General:
    TRUNCATE = True
    SOFA_SCORE_DB_NAME = 'sofa_score'
    FIRST_ROUND = 'First Round'
    DECIMAL_FORMAT = '{: .2f}'
    SEASONS = '16/17', '17/18', '18/19', '19/20', '20/21'
    # SEASONS = '21/22',
    DEFAULT_TOURNAMENTS = [(266, 'Israel - Premier League'), (17, 'England - Premier League')]
    # DEFAULT_TOURNAMENTS = [(266, 'Israel - Premier League'), (17, 'England - Premier League'),
    #                        (18, 'England - Championship'), (24, 'England - League One'), (8, 'Spain - LaLiga'),
    #                        (54, 'Spain - LaLiga 2'),
    #                        (35, 'Germany - Bundesliga'), (44, 'Germany - 2. Bundesliga'),
    #                        (23, 'Italy - Serie A'), (53, 'Italy - Serie B'),
    #                        (34, 'France - Ligue 1'), (182, 'France - Ligue 2'),
    #                        (37, 'Netherlands - Eredivisie'), (62, 'Turkey - Süper Lig'),
    #                        (238, 'Portugal - Primeira Liga'), (38, 'Belgium - Pro League'),
    #                        (11620, 'Mexico - Liga MX Clausura'), (202, 'Poland - Ekstraklasa'),
    #                        (185, 'Greece - Super League'), (210, 'Serbia - Superliga'),
    #                        (45, 'Austria - Bundesliga'), (170, 'Croatia - 1. HNL'), (36, 'Scotland - Premiership'),
    #                        (247, 'Bulgaria - Parva Liga')]


class Tables:
    EVENTS_ORIGINAL = 'events_data'
    ODDS_DATA = 'odds_data'
    EVENTS_PRESSURE = 'events_pressure'
    EVENT_PATTERN = 'event_pattern'
    SIMULATION = 'simulation'


class Keys:
    TOUR_ID = 'tour_id'
    TOUR_NAME = 'tour_name'
    SEASON = 'season'
    TEAM_ID = 'team_id'
    TEAM = 'team'
    TEAM_NAME = 'team_name'
    START_TIME = 'start_time'
    ROUND = 'round'
    RANK = 'rank'
    HOME = 'home'
    AWAY = 'away'
    RESULT = 'result'
    IN_PERCENT = 'in_percent'
    PRESSURE_LEVEL = 'pressure_level'
    GENERAL_RANK = 'general_rank'
    WIN = 'win'
    DREW = 'drew'
    LOST = 'lost'
    BALANCE = 'balance'
    UPDATE_RATING = 'update_rating'
    PSYCHOLOGY = 'psychology'
