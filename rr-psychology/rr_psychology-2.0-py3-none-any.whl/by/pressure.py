from rankset.common import my_sql
import rr_psychology
import pandas as pd

from rr_psychology import common
from rr_psychology.by.common import Keys, sql
from rr_psychology.by.common import utilities


class Pressure(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, pressure_view: bool = False, psy_games_df: pd.DataFrame = None):
        # initiate db instance
        super().__init__(database=common.General.DATABASE)
        # objects - part 1
        self.__main_data = main_data
        self.__pressure_view = pressure_view
        self.__psy_games_df = psy_games_df
        self.__team_games = self.__get_team_games
        self.__team_rank = self.__general_rank
        self.__rival_rank = None
        self.__total_points = 0
        self.__period_situation = None
        self.__pressure_flow = None
        self.__psy_flow = None
        self.__winner_code = None
        self.__points = None
        self.__expected_points = None
        self.__home_game = None
        self.__home_team_id = None
        self.__away_team_id = None
        self.__results = []
        self.__state_result = None
        self.__favorite_data = [['favorite', 0, 0], ['underdog', 0, 0], ['equal', 0, 0]]

    @property
    def __get_results_data(self):
        state_percent = 0
        try:
            if '0.00/0.00' not in self.__state_result:
                state_split = self.__state_result.split('/')
                state_percent = ((float(state_split[0]) / float(state_split[1])) * 100)
        except Exception as e:
            print(e)
        columns = 'rank', 'against rank', 'count', 'current_result', 'expected', 'balance'
        result = pd.DataFrame(data=self.__results, columns=columns).set_index('rank')
        return {'id': self.__main_data.get(Keys.TEAM_ID),
                'name': self.__main_data.get(Keys.TEAM_NAME),
                'rank': self.__team_rank,
                'tour': self.__main_data.get(Keys.TOUR_ID),
                'season': self.__main_data.get(Keys.SEASON),
                'in_percent': '{: .2f}'.format(state_percent),
                'pressure_level': utilities.get_pressure(state_percent, self.__team_rank),
                'state': self.__state_result, 'data': result}

    @property
    def __get_team_games(self):
        return self.get_data(
            query=sql.Get.team_games(main_data=self.__main_data, pressure_view=self.__pressure_view),
            return_data_frame=True, close_connection=True)

    # @property
    # def __get_psychology_data(self):
    #     return Psy(db_conn=self.__db, tour_id=self.__tour_id, season=self.__season, game_object=self.__game_object)

    @property
    def __initiate_period_situation_list(self):
        return [[0, 0, self.__expected_points[0], 1], [0, 0, self.__expected_points[1], 2],
                [0, 0, self.__expected_points[2], 3],
                [0, 0, self.__expected_points[3], 4], [0, 0, self.__expected_points[3], 5]]

    @property
    def __general_rank(self):
        try:
            return float(
                self.get_data(query=common.sql.Get.original_rank(main_data=self.__main_data, by_team_id=True))[0][0][2])
        except Exception:
            return 5

    def __update_expected_points_by_rank(self):
        rank = self.__team_rank
        if rank < 2:
            self.__expected_points = 50, 65, 75, 100, 100
        elif rank < 3:
            self.__expected_points = 25, 65, 75, 100, 100
        elif rank < 4:
            self.__expected_points = 0, 25, 70, 65, 65
        else:
            self.__expected_points = 0, 0, 60, 60, 60

    def __update_rival_rank_target(self):
        if self.__rival_rank < 2:
            self.__rival_rank = 1
        elif self.__rival_rank < 3:
            self.__rival_rank = 2
        elif self.__rival_rank < 4:
            self.__rival_rank = 3
        else:
            self.__rival_rank = 4

    def __set_favorite_by_rank(self, success):
        if self.__team_rank < self.__rival_rank:
            self.__favorite_data[0][1] = (self.__favorite_data[0][1] + 1)
            self.__favorite_data[0][2] = (self.__favorite_data[0][2] + success)
        elif self.__team_rank > self.__rival_rank:
            self.__favorite_data[1][1] = (self.__favorite_data[1][1] + 1)
            self.__favorite_data[1][2] = (self.__favorite_data[1][2] + success)
        else:
            self.__favorite_data[2][1] = (self.__favorite_data[2][1] + 1)
            self.__favorite_data[2][2] = (self.__favorite_data[2][2] + success)

    def __update_data(self):
        self.__update_rival_rank_target()
        self.__period_situation[self.__rival_rank - 1][0] = (self.__period_situation[self.__rival_rank - 1][0] + 1)
        if self.__points == 3:
            self.__period_situation[self.__rival_rank - 1][1] = (
                    100 + self.__period_situation[self.__rival_rank - 1][1])
            self.__set_favorite_by_rank(1)
        elif self.__points == 1:
            self.__period_situation[self.__rival_rank - 1][1] = (33 + self.__period_situation[self.__rival_rank - 1][1])
            self.__set_favorite_by_rank(0.5)
        else:
            self.__set_favorite_by_rank(0)

    @staticmethod
    def __divide(num1, num2):
        if num1 == 0 or num2 == 0:
            return 0
        else:
            return float('{:.2f}'.format(num1 / num2))

    def __read_results(self, game_obj=None):
        current = 0
        possible = 0
        count_of_games = 0
        results = []
        for r, res in enumerate(self.__period_situation):
            count_of_games += res[0]
            current_result = self.__divide(res[1], res[0])
            current_points = float('{: .2f}'.format((3 * res[0]) * (self.__divide(float(current_result), 100))))
            possible_points = float('{: .2f}'.format((3 * res[0]) * (self.__divide(res[2], 100))))
            current += current_points
            possible += possible_points
            results.append(
                (res[3], res[3], res[0], float(current_points), possible_points,
                 float('{: .2f}'.format(current_points - possible_points))))
            self.__state_result = f"'{r + 1}':  'current result = {current_result}%, expected result = {res[2]}%," \
                                  f" possible points {'{:.2f}'.format(current_points)}/" \
                                  f"{'{:.2f}'.format(possible_points)} (from {res[0]} games)',"
        results.append(('total', 'total', count_of_games, float('{: .2f}'.format(current)),
                        float('{: .2f}'.format(possible)), float('{: .2f}'.format(current - possible))))
        self.__state_result = f"{'{:.2f}'.format(current)}/{'{:.2f}'.format(possible)}"
        if game_obj is not None:
            results.append({'rival_rank': self.__rival_rank, 'game_object': game_obj})
        return results

    def __set_rival_rank(self, game_obj):
        try:
            if self.__main_data.get(Keys.TEAM_ID) == game_obj['home_team_id']:
                self.__rival_rank = game_obj['away_team_rank']
            elif self.__main_data.get(Keys.TEAM_ID) == game_obj['away_team_id']:
                self.__rival_rank = game_obj['home_team_rank']
            else:
                self.__rival_rank = 5
        except Exception:
            self.__rival_rank = 5

    def __calculate_data(self, pressure_flow: bool):
        for game_obj in self.__team_games.iterrows():
            game_obj = game_obj[1]
            current_round = game_obj['round']
            self.__winner_code = game_obj['winner_code']
            self.__points = game_obj['points']
            self.__home_team_id = game_obj['home_team_id']
            self.__away_team_id = game_obj['away_team_id']
            self.__set_rival_rank(game_obj)
            self.__update_data()
            self.__total_points += self.__points
            if pressure_flow:
                self.__pressure_flow.setdefault(f"{current_round}", self.__read_results(game_obj=game_obj))
                games = self.__psy_games_df[self.__psy_games_df['round'] < current_round]
                cal = rr_psychology.us.Calculate(main_data=self.__main_data, games_df=games).calculate()
                self.__psy_flow.setdefault(f"{current_round}", cal)

    def calculate_pressure(self, pressure_flow: bool = True):
        if pressure_flow:
            self.__pressure_flow = {}
            self.__psy_flow = {}
        self.__update_expected_points_by_rank()
        self.__period_situation = self.__initiate_period_situation_list
        self.__calculate_data(pressure_flow=pressure_flow)
        self.__results = self.__read_results()
        return {'result': self.__get_results_data, 'flow': self.__pressure_flow, 'psychology': self.__psy_flow}
