import json
import ast

from rr_psychology.by.common.constants import Keys


def main_data_dict(tour_id, team_id, team_name, season):
    return {Keys.TOUR_ID: tour_id, Keys.TEAM_ID: team_id, Keys.TEAM_NAME: team_name, Keys.SEASON: season}


def get_favorite_by_rank(home_rank, away_rank):
    if home_rank < away_rank:
        return 1

    elif home_rank > away_rank:
        return 2
    else:
        return 3


def get_season_level(round_number):
    if round_number <= 20:
        return 1
    elif round_number < 30:
        return 2
    else:
        return 3


def get_pressure(state, rank):
    if state == -1:
        return 75

    elif rank == 4:
        state += 5
    elif state < 80 and rank < 3:
        state += -5

    if state >= 99:
        return 0
    elif state >= 80:
        return 1
    elif state >= 70:
        return 2
    elif state >= 60:
        return 4
    else:
        return 5


def calculate_achieved_points(home_away: int, odd: float, total_odds: float, winner_code: int):
    if home_away == 1:
        if winner_code == 1:
            res = 100 * ((odd + total_odds) / (odd + total_odds))
        elif winner_code == 3:
            res = 100 * (((odd * 0.3) + total_odds) / (odd + total_odds))
        else:
            res = 100 * (total_odds / (odd + total_odds))
    else:
        if winner_code == 2:
            res = 100 * ((odd + total_odds) / (odd + total_odds))
        elif winner_code == 3:
            res = 100 * (((odd * 0.3) + total_odds) / (odd + total_odds))
        else:
            res = 100 * (total_odds / (odd + total_odds))

    return '{:.2f}'.format(res)


def get_value(value, value_type: int = 1):
    """ value type: 1 - int, 2 - float"""
    try:
        if value_type == 1:
            return int(value)
        else:
            return float(value)
    except:
        return 0


def get_metric_data(data):
    return [(f"Balance ({data.get('total_events')} events)", '$', data.get('balance'), 0),
            (f"Success rate {data.get('success') - data.get('backup')} / {data.get('failed')}", '',
             data.get('success') - data.get('failed'), 0),
            (f"Total success rate (with backup) {data.get('success') + data.get('backup')}"
             f" / {data.get('failed')}", '',
             (data.get('success') + data.get('backup') - + data.get('failed')), 0)]


# ---------------------------- files actions ------------------------------------#
def dict_to_json(string_content):
    return json.dumps(str_to_dict(string_content))


def str_to_dict(string_content):
    return ast.literal_eval(str(string_content))


def load_json(json_content):
    return json.loads(json_content)


def create_json_object(file_path, data):
    json_file = open(file_path, "w")
    json_file.write(data)
    json_file.close()


def read_json_object(path):
    file = open(path, 'r')
    json_object = json.load(file)
    file.close()
    return json_object
