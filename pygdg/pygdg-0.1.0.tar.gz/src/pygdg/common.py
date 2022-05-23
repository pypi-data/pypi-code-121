import random
from enum import Enum
import numpy as np

class WeekDay(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
class DayHour(Enum):
    TWELVE_AM = 0
    ONE_AM = 1
    TWO_AM = 2
    THREE_AM = 3
    FOUR_AM = 4
    FIVE_AM = 5
    SIX_AM = 6
    SEVEN_AM = 7
    EIGHT_AM = 8
    NINE_AM = 9
    TEN_AM = 10
    ELEVEN_AM = 11
    TWELVE_PM = 12
    ONE_PM = 13
    TWO_PM = 14
    THREE_PM = 15
    FOUR_PM = 16
    FIVE_PM = 17
    SIX_PM = 18
    SEVEN_PM = 19
    EIGHT_PM = 20
    NINE_PM = 21
    TEN_PM = 22
    ELEVEN_PM = 23

class PlayerEventType(Enum):
    BEGIN_SESSION = 0
    END_SESSION = 1
    #BEGIN_STAGE = 2
    #END_STAGE = 3
    #SEND_MESSAGE = 4
    #RECEIVE_MESSAGE = 5
    #ASK_FRIEND = 6
    #ACCEPT_FRIEND = 7
    #VIEW_LEADERBOARD = 8
    #BUY_CURRENCY = 9
    #BUY_ITEM = 10

class PlayerEventField(Enum):
    id = 0
    player_id = 1
    player_type = 2
    cohort_id = 3
    session_id = 4
    event_type = 5
    timestamp = 6
    #payload = 7
    #stage_id = 6
    #stage_result = 7
    #chat_message = 8
    #friend_id = 9
    #leaderboard_id = 10
    #currency_amount = 11
    #item_id = 12

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

def random_gauss_clamp(mu, sigma, factor=3):
    return min(mu+factor*sigma, max(mu-factor*sigma, random.gauss(mu, sigma)))

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

