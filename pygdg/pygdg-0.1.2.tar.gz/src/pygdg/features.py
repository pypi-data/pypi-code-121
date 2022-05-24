from os.path import exists
import random
import pandas as pd
from enum import Enum
from functools import reduce, partial
from pygdg.common import *

ONE_MINUTE_IN_SECONDS = 60
ONE_HOUR_IN_SECONDS = ONE_MINUTE_IN_SECONDS * 60
ONE_DAY_IN_SECONDS = ONE_HOUR_IN_SECONDS * 24
ONE_WEEK_IN_SECONDS = ONE_DAY_IN_SECONDS * 7
ONE_MONTH_IN_SECONDS = ONE_WEEK_IN_SECONDS * 4

class Counter:
    def __init__(self, count, total):
        self.count = count
        self.total = total

    def __iadd__(self, increment):
        self.count += increment
        return self    

class FeatureName(Enum):
    cohort_id = 0
    player_id = 1
    player_type = 2
    player_lifetime = 3
    player_churn = 4
    session_count = 5

    def event_count_day(day):
        return f'_count[day-{day+1}]'

    def event_count_week(week):
        return f'_count[week-{week+1}]'

    def event_count_month(month):
        return f'_count[month-{month+1}]'

def extract_player_type(player_events):
    player_type = player_events[PlayerEventField.player_type.name].iat[0]
    return {FeatureName.player_type.name: player_type}

def extract_player_session_count(player_events):
    player_session_count = player_events[PlayerEventField.session_id.name].drop_duplicates().size
    return {FeatureName.session_count.name: player_session_count}

def extract_player_lifetime(player_events):
    first_session_timestamp = player_events[PlayerEventField.timestamp.name].iat[0]
    last_session_timestamp = player_events[PlayerEventField.timestamp.name].iat[-1]
    player_lifetime = (last_session_timestamp - first_session_timestamp).total_seconds()
    return {FeatureName.player_lifetime.name: player_lifetime}  

def extract_player_event_count_by_time_period(player_events_by_elapsed_time_periods, time_period, suffixer):
    features = {}

    for time in range(0, time_period):
        feature_suffix = suffixer(time)
        if time in player_events_by_elapsed_time_periods.groups:
            player_events_by_elapsed_time_period = player_events_by_elapsed_time_periods.get_group(time).groupby(PlayerEventField.event_type.name)
            for event_type in PlayerEventType:
                feature_name = f'{event_type.name.lower()}{feature_suffix}'
                if event_type.name in player_events_by_elapsed_time_period.groups:  
                    player_events_by_elapsed_time_period_and_event_type = player_events_by_elapsed_time_period.get_group(event_type.name)
                    features[feature_name] = player_events_by_elapsed_time_period_and_event_type[PlayerEventField.id.name].count()
                else:
                    features[feature_name] = 0
        else:
            for event_type in PlayerEventType:
                features[f'{event_type.name.lower()}{feature_suffix}'] = 0
    
    return features

def extract_player_event_count(player_events, days, weeks, months):
    features = {}

    first_session_timestamp = player_events[PlayerEventField.timestamp.name].iat[0]
    features[FeatureName.cohort_id.name] = first_session_timestamp.strftime("%Y_%m_%d")
    last_session_timestamp = player_events[PlayerEventField.timestamp.name].iat[-1]

    elapsed_time_in_seconds = 'elapsed_time_in_seconds'
    elapsed_time_in_days = 'elapsed_time_in_days'
    elapsed_time_in_weeks = 'elapsed_time_in_weeks' 
    elapsed_time_in_months = 'elapsed_time_in_months' 

    player_events[elapsed_time_in_seconds] = player_events[PlayerEventField.timestamp.name].apply(lambda d: int((last_session_timestamp-d).total_seconds()))
    # player_events['elapsed_time_in_minutes'] = player_events[elapsed_time_in_seconds] // ONE_MINUTE_IN_SECONDS 
    # player_events['elapsed_time_in_hours'] = player_events[elapsed_time_in_seconds] // ONE_HOUR_IN_SECONDS
    player_events[elapsed_time_in_days] = player_events[elapsed_time_in_seconds] // ONE_DAY_IN_SECONDS
    player_events[elapsed_time_in_weeks] = player_events[elapsed_time_in_seconds] // ONE_WEEK_IN_SECONDS
    player_events[elapsed_time_in_months] = player_events[elapsed_time_in_seconds] // ONE_MONTH_IN_SECONDS

    features |= extract_player_event_count_by_time_period(player_events.groupby(elapsed_time_in_days), days, FeatureName.event_count_day)
    features |= extract_player_event_count_by_time_period(player_events.groupby(elapsed_time_in_weeks), weeks, FeatureName.event_count_week)
    features |= extract_player_event_count_by_time_period(player_events.groupby(elapsed_time_in_months), months, FeatureName.event_count_month)

    return features

def extract_player_churn(player_events, timestamp, days):
    features = {}
    
    last_session_timestamp = player_events[PlayerEventField.timestamp.name].iat[-1]
    inactive_days = (timestamp - last_session_timestamp).days
    if inactive_days > days:
        features[FeatureName.player_churn.name] = True
    else:
        features[FeatureName.player_churn.name] = False

    return features

def extract_features(player_events, extractors, counter):
    def extract(features, extractor):      
        return features | extractor(player_events)

    counter += 1
    print_progress_bar(counter.count, counter.total+1, prefix = 'generating features:', suffix = '', length = 50)
    
    return pd.Series(reduce(extract, extractors, {}));

def generate_player_features(game_events):

    game_events[PlayerEventField.timestamp.name] = pd.to_datetime(game_events[PlayerEventField.timestamp.name])
    game_events = game_events.sort_values(by=[PlayerEventField.timestamp.name])
    game_events_by_player_id = game_events.groupby(PlayerEventField.player_id.name)

    # add player ids

    player_count = len(game_events_by_player_id.indices)
    player_features = pd.DataFrame()
    player_features[FeatureName.player_id.name] = game_events[PlayerEventField.player_id.name].drop_duplicates()
    player_features.set_index(keys=FeatureName.player_id.name, inplace=True)

    # extract features

    event_count_days = 7
    event_count_weeks = 3
    event_count_months = 2
    churn_timestamp = game_events[PlayerEventField.timestamp.name].iat[-1]
    churn_days = 5

    counter = Counter(1, player_count)
    extractor = partial(
        extract_features, 
        extractors=[
            extract_player_type,
            extract_player_lifetime,
            extract_player_session_count,
            partial(extract_player_event_count, days=event_count_days, weeks=event_count_weeks, months=event_count_months),
            partial(extract_player_churn, timestamp=churn_timestamp, days=churn_days)
        ],
        counter = Counter(1, player_count)
    )
    
    print_progress_bar(counter.count, counter.total+1, prefix = 'generating features:', suffix = '', length = 50)
    
    extracted_features = game_events_by_player_id.apply(extractor)
    player_features = pd.merge(player_features, extracted_features, left_index=True, right_index=True)

    return player_features

def generate(filename, events, seed, debug):
    
    # set seed

    random.seed(seed)

    # load generated data

    print('loading events...')
    events_file = f'{events}.csv'
    if not exists(events_file):
        print(f'{events_file} does not exist!')
        return
    events_dataframe = pd.read_csv(events_file)
    print('events loaded!')

    # generate features

    features_file = f'{filename}.csv'
    features_dataframe = generate_player_features(events_dataframe)

    print('storing features...')
    features_dataframe.to_csv(features_file)
    print(f'features stored in {features_file}!')