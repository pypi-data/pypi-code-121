import random
from datetime import timedelta
import numpy as np
from pygdg.common import *

def random_gauss_clamp(mu, sigma, factor=3):
    return min(mu+factor*sigma, max(mu-factor*sigma, random.gauss(mu, sigma)))

class Interpolator:
    def __init__(self, dictionary):
        self.keys = []
        self.values = []

        for key in dictionary:
            self.keys.append(float(key))
            self.values.append(float(dictionary[key]))

    def __getitem__(self, key):
        return np.interp(key, self.keys, self.values)

    def __mul__(self, value):
        return Interpolator(dict(zip(self.keys, (v * value for v in self.values))))

    __rmul__ = __mul__

class SessionOptions:
    """A session options class."""

    def __init__(self, time_mu, time_sigma, 
                        duration_mu, duration_sigma):
        self.time_mu = time_mu
        self.time_sigma = time_sigma
        self.duration_mu = duration_mu
        self.duration_sigma = duration_sigma

    def time(self):
        return timedelta(seconds=random.gauss(self.time_mu.total_seconds(), self.time_sigma.total_seconds()))

    def duration(self):
        return timedelta(seconds=random_gauss_clamp(self.duration_mu.total_seconds(), self.duration_sigma.total_seconds()))

class PlayerOptions:
    """A player options class."""   
     
    def __init__(self, player_type, 
                        sessions_options,
                        lifetime):
        self.player_type = player_type
        self.sessions_options = sessions_options
        self.lifetime = lifetime

class GameOptions:
    """A game options class."""

    def __init__(self, players_options, players_acquisition, simulation_days):
        self.players_options = {k: v for k, v in sorted(players_options.items(), key=lambda item: item[1])}
        self.players_acquisition = players_acquisition
        self.simulation_days = simulation_days

    def __getitem__(self, p):
        for key, value in self.players_options.items():
            if p < value:
                return key
            else:
                last_key = key
        return last_key

def default_game_options(players, days):

    morning_session_options = SessionOptions(
        timedelta(hours=7), # session time mean
        timedelta(minutes=30), # session time standard deviation
        timedelta(minutes=30), # session duration mean
        timedelta(minutes=10), # session duration standard deviation
    )

    noon_session_options = SessionOptions(
        timedelta(hours=12), # session time mean
        timedelta(hours=30), # session time standard deviation
        timedelta(minutes=45), # session duration mean
        timedelta(minutes=15), # session duration standard deviation
    )

    afternoon_session_options = SessionOptions(
        timedelta(hours=17), # session time mean
        timedelta(hours=1), # session time standard deviation
        timedelta(minutes=30), # session duration mean
        timedelta(minutes=20), # session duration standard deviation
    )

    night_session_options = SessionOptions(
        timedelta(hours=20), # session time mean
        timedelta(hours=3), # session time standard deviation
        timedelta(hours=2), # session duration mean
        timedelta(minutes=1), # session duration standard deviation
    )

    bot_player = PlayerOptions(
        'bot',
        {
            WeekDay.MONDAY: {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.TUESDAY: {
                morning_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.WEDNESDAY:  {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.THURSDAY:  {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.FRIDAY:  {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.SATURDAY:  {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.SATURDAY: {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            },
            WeekDay.SUNDAY: {
                night_session_options: 1.0,
                noon_session_options: 1.0,
                afternoon_session_options: 1.0,
                night_session_options: 1.0
            }
        }, 
        Interpolator({
            0: 1.0
        })
    )

    hardcore_player_options = PlayerOptions(
        'hardcore',
        {
            WeekDay.MONDAY: {
                night_session_options: 0.5  # 50% chance to play a night session on monday
            },
            WeekDay.TUESDAY: {
                morning_session_options: 0.3,
                noon_session_options: 0.5,
                night_session_options: 1.0
            },
            WeekDay.WEDNESDAY:  {
                morning_session_options: 0.3,
                noon_session_options: 0.5,
                night_session_options: 1.0
            },
            WeekDay.THURSDAY:  {
                morning_session_options: 0.3,
                noon_session_options: 0.5,
                night_session_options: 1.0
            },
            WeekDay.FRIDAY:  {
                morning_session_options: 0.3,
                noon_session_options: 0.5,
                night_session_options: 1.0
            },
            WeekDay.SATURDAY:  {
                morning_session_options: 0.3,
                noon_session_options: 0.5,
                night_session_options: 1.0
            },
            WeekDay.SATURDAY: {
                morning_session_options: 0.5
            },
            WeekDay.SUNDAY: {
                afternoon_session_options: 0.8
            }
        }, Interpolator({
            0: 0.7, # day 1 modifier for session probability
            6: 1.0,
            13: 0.7,
            27: 0.5
        })
    )

    casual_player_options = PlayerOptions(
        'casual',
        {
            WeekDay.TUESDAY: {
                noon_session_options: 0.5,
                night_session_options: 0.5
            },
            WeekDay.WEDNESDAY:  {
                noon_session_options: 0.5,
                night_session_options: 0.5
            },
            WeekDay.THURSDAY:  {
                noon_session_options: 0.5,
                night_session_options: 0.5
            },
            WeekDay.FRIDAY:  {
                noon_session_options: 0.5,
                night_session_options: 0.5
            }
        }, Interpolator({
            0: 0.7, # day 1 modifier for session probability
            6: 1.0,
            13: 0.3
        })
    )    

    churner_player_options = PlayerOptions(
        'churner',
        {
            WeekDay.TUESDAY: {
                night_session_options: 1.0
            },
            WeekDay.WEDNESDAY:  {
                night_session_options: 1.0
            },
            WeekDay.THURSDAY:  {
                night_session_options: 1.0
            },
            WeekDay.FRIDAY:  {
                night_session_options: 1.0
            },
            WeekDay.SUNDAY:  {
                night_session_options: 1.0
            }
        }, Interpolator({
            0: 1.0, # day 1 modifier for session probability
            1: 1.0,
            2: 0.5,
            6: 0.3,
            13: 0
        })
    )

    game_options = GameOptions(
        players_options = {
            # bot_player: 1.0,
            hardcore_player_options: 0.05,
            casual_player_options: 0.1,
            churner_player_options: 1.0,
        }, 
        players_acquisition = players * Interpolator({
            0: 1, # one player acquired day one
            6: 2,
            7: 0,

            13: 0,
            14: 1,
            20: 2,
            21: 0,

            27: 0,
            28: 2,
            34: 5,
            35: 0,

            41: 0,
            42: 3,
            48: 7,
            49: 0,

            55: 0,
            56: 1,
            62: 2,
            63: 0
        }),
        simulation_days = days # simulation days
    )

    return game_options