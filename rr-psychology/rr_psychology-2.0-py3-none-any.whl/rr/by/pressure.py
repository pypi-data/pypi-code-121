import rr_psychology
import pandas as pd
from rankset.common import my_sql


class Pressure(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, psy_games_df: pd.DataFrame = None):
        # initiate db instance
        super().__init__(database=rr_psychology.by.common.General.DATABASE)
        # objects - part 1
        self.__main_data = main_data
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
        self.__favorite_data = [[rr_psychology.by.common.Keys.FAVORITE, 0, 0], [rr_psychology.by.common.Keys.UNDERDOG, 0, 0],
                                [rr_psychology.by.common.Keys.EQUAL, 0, 0]]

    @property
    def __get_results_data(self):
        state_percent = 0
        if '0.00/0.00' not in self.__state_result:
            state_split = self.__state_result.split('/')
            first = float(state_split[0])
            second = float(state_split[1])
            if first > 0 and second > 0:
                state_percent = (first / second) * 100
        result = pd.DataFrame(data=self.__results, columns=rr_psychology.by.common.Columns.PRESSURE).set_index(rr_psychology.by.common.Keys.RANK)
        return {rr_psychology.by.common.Keys.ID: self.__main_data.get(rr_psychology.by.common.Keys.TEAM_ID),
                rr_psychology.by.common.Keys.NAME: self.__main_data.get(rr_psychology.by.common.Keys.TEAM_NAME),
                rr_psychology.by.common.Keys.RANK: self.__team_rank,
                rr_psychology.by.common.Keys.TOUR: self.__main_data.get(rr_psychology.by.common.Keys.TOUR_ID),
                rr_psychology.by.common.Keys.SEASON: self.__main_data.get(rr_psychology.by.common.Keys.SEASON),
                rr_psychology.by.common.Keys.IN_PERCENT: rr_psychology.by.common.General.DECIMAL_FORMAT.format(state_percent),
                rr_psychology.by.common.Keys.PRESSURE_LEVEL: rr_psychology.by.common.utilities.get_pressure(state_percent, self.__team_rank),
                rr_psychology.by.common.Keys.STATE: self.__state_result, rr_psychology.by.common.Keys.DATA: result}

    @property
    def __get_team_games(self):
        return self.get_data(
            query=rr_psychology.by.common.sql.Get.team_games(main_data=self.__main_data),
            return_data_frame=True, close_connection=True)

    @property
    def __initiate_period_situation_list(self):
        return [[0, 0, self.__expected_points[0], 1], [0, 0, self.__expected_points[1], 2],
                [0, 0, self.__expected_points[2], 3],
                [0, 0, self.__expected_points[3], 4], [0, 0, self.__expected_points[3], 5]]

    @property
    def __general_rank(self):
        try:
            return float(
                self.get_data(query=rr_psychology.by.common.sql.Get.original_rank(main_data=self.__main_data, by_team_id=True))[0][0][
                    2])
        except Exception as e:
            print(e, f"\nfor {self.__main_data}")
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
            return float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(num1 / num2))

    def __read_results(self, game_obj=None):
        current = 0
        possible = 0
        count_of_games = 0
        results = []
        for r, res in enumerate(self.__period_situation):
            count_of_games += res[0]
            current_result = self.__divide(res[1], res[0])
            current_points = float(
                rr_psychology.by.common.General.DECIMAL_FORMAT.format((3 * res[0]) * (self.__divide(float(current_result), 100))))
            possible_points = float(
                rr_psychology.by.common.General.DECIMAL_FORMAT.format((3 * res[0]) * (self.__divide(res[2], 100))))
            current += current_points
            possible += possible_points
            results.append(
                (res[3], res[3], res[0], float(current_points), possible_points,
                 float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(current_points - possible_points))))
            self.__state_result = f"'{r + 1}':  'current result = {current_result}%, expected result = {res[2]}%," \
                                  f" possible points {rr_psychology.by.common.General.DECIMAL_FORMAT.format(current_points)}/" \
                                  f"{rr_psychology.by.common.General.DECIMAL_FORMAT.format(possible_points)} (from {res[0]} games)',"
        results.append((rr_psychology.by.common.Keys.TOTAL, rr_psychology.by.common.Keys.TOTAL, count_of_games,
                        float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(current)),
                        float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(possible)),
                        float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(current - possible))))
        self.__state_result = f"{rr_psychology.by.common.General.DECIMAL_FORMAT.format(current)}/{rr_psychology.by.common.General.DECIMAL_FORMAT.format(possible)}"
        if game_obj is not None:
            results.append({rr_psychology.by.common.Keys.RIVAL_RANK: self.__rival_rank, rr_psychology.by.common.Keys.GAME_OBJECT: game_obj})
        return results

    def __set_rival_rank(self, game_obj):
        try:
            if self.__main_data.get(rr_psychology.by.common.Keys.TEAM_ID) == game_obj[rr_psychology.by.common.Keys.HOME_TEAM_ID]:
                self.__rival_rank = game_obj[rr_psychology.by.common.Keys.AWAY_TEAM_RANK]
            elif self.__main_data.get(rr_psychology.by.common.Keys.TEAM_ID) == game_obj[rr_psychology.by.common.Keys.AWAY_TEAM_ID]:
                self.__rival_rank = game_obj[rr_psychology.by.common.Keys.HOME_TEAM_RANK]
            else:
                self.__rival_rank = 5
        except Exception:
            self.__rival_rank = 5

    def __calculate_data(self, pressure_flow: bool):
        for game_obj in self.__team_games.iterrows():
            game_obj = game_obj[1]
            current_round = game_obj[rr_psychology.by.common.Keys.ROUND]
            self.__winner_code = game_obj[rr_psychology.by.common.Keys.WINNER_CODE]
            self.__points = game_obj[rr_psychology.by.common.Keys.POINTS]
            self.__home_team_id = game_obj[rr_psychology.by.common.Keys.HOME_TEAM_ID]
            self.__away_team_id = game_obj[rr_psychology.by.common.Keys.AWAY_TEAM_ID]
            self.__set_rival_rank(game_obj)
            self.__update_data()
            self.__total_points += self.__points
            if pressure_flow:
                self.__pressure_flow.setdefault(f"{current_round}", self.__read_results(game_obj=game_obj))
                games = self.__psy_games_df[self.__psy_games_df[rr_psychology.by.common.Keys.ROUND] < current_round]
                cal = rr_psychology.by.unconditional_situations.Calculate(main_data=self.__main_data, games_df=games).calculate()
                self.__psy_flow.setdefault(f"{current_round}", cal)

    def calculate_pressure(self, pressure_flow: bool = True):
        if pressure_flow:
            self.__pressure_flow = {}
            self.__psy_flow = {}
        self.__update_expected_points_by_rank()
        self.__period_situation = self.__initiate_period_situation_list
        self.__calculate_data(pressure_flow=pressure_flow)
        self.__results = self.__read_results()
        return {rr_psychology.by.common.Keys.RESULT: self.__get_results_data,
                rr_psychology.by.common.Keys.FLOW: self.__pressure_flow, rr_psychology.by.common.Keys.PSYCHOLOGY: self.__psy_flow}
