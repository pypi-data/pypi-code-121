import rankset
from rr_psychology.by.unconditional_situations import ExportData
from rr_batch import constants, sql
from rr_psychology.by.pressure import Pressure
from rr_psychology.by.common import utilities

from rr_batch.process.rating import CalculateRating


class Run(rankset.common.my_sql.MySqlConnection):
    def __init__(self, main_data: dict):
        super().__init__(database=constants.General.SOFA_SCORE_DB_NAME)
        self.__main_data = main_data
        self.__events = self.__get_events_df
        self.__rank_df = self.__get_rank_df
        self.__home_object = {}
        self.__away_object = {}
        self.__last_game_result = None
        self.__two_games_flow = None
        self.__update_line_points = []
        self.__line_points_percent = None
        self.__season_level = None
        self.__favorite_by_rank = None
        self.__last_game_data = None
        self.__game_item = None
        self.__pressure_data = None
        self.__h2h_rating_data = None

    @property
    def __get_events_df(self):
        return self.get_data(query=sql.Get.get_events(tour_id=self.__main_data[constants.Keys.TOUR_ID],
                                                      season=self.__main_data[constants.Keys.SEASON],
                                                      main_table=constants.Tables.EVENTS_ORIGINAL),
                             return_data_frame=True)

    @property
    def __get_rank_df(self):
        return self.get_data(query=sql.Get.get_original_rank(tour_id=self.__main_data[constants.Keys.TOUR_ID],
                                                             season=self.__main_data[constants.Keys.SEASON]),
                             return_data_frame=True)

    @property
    def __get_simulation_events_data(self):
        return self.get_data(query=sql.Get.get_events(tour_id=self.__main_data[constants.Keys.TOUR_ID],
                                                      season=self.__main_data[constants.Keys.SEASON],
                                                      main_table=constants.Tables.EVENTS_PRESSURE),
                             return_data_frame=True)

    @property
    def __get_base_data(self):
        try:
            last_date = list(self.__events.start_time.unique())
            if len(last_date) > 0:
                last_date = last_date[len(last_date) - 1]
                round_data = self.__events[constants.Keys.ROUND]
                return last_date, round_data.min(), round_data.max()
        except Exception as e:
            print(e)

    def __get_pressure_df(self, obj: dict):
        keys = [constants.Keys.TOUR_ID, constants.Keys.TEAM_ID, constants.Keys.TEAM_NAME, constants.Keys.SEASON]
        # set home team values
        values = [self.__main_data[constants.Keys.TOUR_ID], obj[constants.Keys.TEAM_ID],
                  obj[constants.Keys.TEAM_NAME], self.__main_data[constants.Keys.SEASON]]
        main_data = utilities.main_data_dict(keys=keys, values=values)
        games_df = ExportData(main_data=main_data, current_pressure=False).get_all_history_data
        if games_df is not None:
            return Pressure(main_data=main_data,
                            psy_games_df=games_df).calculate_pressure()

    def __get_event_pressure(self):
        home_data = self.__get_pressure_df(obj=self.__home_object)
        away_data = self.__get_pressure_df(obj=self.__away_object)
        # value_when_true if condition else value_when_false
        return {constants.Keys.HOME: home_data if home_data is not None else {},
                constants.Keys.AWAY: away_data if away_data is not None else {}}

    def __get_h2h_rating(self):
        home_data = CalculateRating(tour_id=self.__main_data[constants.Keys.TOUR_ID],
                                    team_id=self.__home_object.get(constants.Keys.TEAM_ID),
                                    rival_team_name=self.__away_object.get(constants.Keys.TEAM_NAME)).get_team_flow()
        away_data = CalculateRating(tour_id=self.__main_data[constants.Keys.TOUR_ID],
                                    team_id=self.__away_object.get(constants.Keys.TEAM_ID),
                                    rival_team_name=self.__home_object.get(constants.Keys.TEAM_NAME)).get_team_flow()
        # value_when_true if condition else value_when_false
        return {constants.Keys.HOME: home_data if home_data is not None else {},
                constants.Keys.AWAY: away_data if away_data is not None else {}}

    def __last_game_update(self, result):
        base_flow = f" - {result[0][0][6]} - {result[0][0][7]} - {result[0][0][2]}"
        if result[0][0][2] == 'H':
            first_game = f"{result[0][0][1]}{base_flow}"
        else:
            first_game = f"{result[0][0][0]}{base_flow}"

        if len(result[0]) > 1:
            base_flow = f" - {result[0][1][6]} - {result[0][1][7]} - {result[0][1][2]}"
            if result[0][1][2] == 'H':
                second_game = f"F - {first_game} || S - {result[0][1][1]}{base_flow}"
            else:
                second_game = f"F - {first_game} || S - {result[0][1][0]}{base_flow}"
        else:
            second_game = constants.General.FIRST_ROUND

        self.__two_games_flow.append(first_game)
        self.__two_games_flow.append(second_game)

    def __pressure_by_last_game(self, team_id):
        result = self.get_data(query=sql.Get.get_momentum(self.__main_data[constants.Keys.TOUR_ID], team_id,
                                                          self.__main_data[constants.Keys.SEASON]))
        if len(result[0]) > 0:
            self.__last_game_result = f"{result[0][0][6]}{result[0][0][3]}{result[0][0][2]}"
            self.__update_line_points.append(result[0][0][10])
            self.__last_game_data.append(result)
            self.__last_game_update(result=result)
            return result[0][0][4]
        else:
            self.__last_game_result = constants.General.FIRST_ROUND
            self.__last_game_data.append(self.__last_game_result)
            self.__two_games_flow.append(self.__last_game_result)
            self.__two_games_flow.append(self.__last_game_result)
            self.__update_line_points.append(0)
            return 0

    def __pressure_by_line_points(self, odd, home_away, winner_code, total_odds):
        self.__line_points_percent = utilities.calculate_achieved_points(home_away, float(odd),
                                                                         float(total_odds),
                                                                         int(winner_code))
        return constants.General.DECIMAL_FORMAT.format(float(total_odds) + float(odd))

    def __update_two_last_game_obj(self):
        # update two games flow
        self.__two_games_flow[
            0] = f"{self.__two_games_flow[0]} | {self.__game_item[1].away_team_id}" \
                 f" - {self.__game_item[1].winner_code} - H"
        self.__two_games_flow[
            1] = f"{self.__two_games_flow[1]} | {self.__game_item[1].away_team_id}" \
                 f" - {self.__game_item[1].winner_code} - H"
        self.__two_games_flow[
            2] = f"{self.__two_games_flow[2]} | {self.__game_item[1].home_team_id}" \
                 f" - {self.__game_item[1].winner_code} - A"
        self.__two_games_flow[
            3] = f"{self.__two_games_flow[3]} | {self.__game_item[1].home_team_id}" \
                 f" - {self.__game_item[1].winner_code} - A"
        self.__last_game_data = {constants.Keys.HOME: self.__last_game_data[0],
                                 constants.Keys.AWAY: self.__last_game_data[1]}

    def __get_rank(self, team_id):
        if str(team_id) in list(self.__rank_df.team_id.unique()):
            return self.__rank_df[
                self.__rank_df[constants.Keys.TEAM_ID] == str(team_id)].general_rank.values[0]
        else:
            return 5

    def __initiate_game_object(self, current_round: int):
        home_team_id = self.__game_item[1].home_team_id
        away_team_id = self.__game_item[1].away_team_id
        self.__home_object = {constants.Keys.TEAM_ID: home_team_id,
                              constants.Keys.TEAM_NAME: self.__game_item[1].home_team_name,
                              constants.Keys.RANK: self.__get_rank(team_id=home_team_id)}
        self.__away_object = {constants.Keys.TEAM_ID: away_team_id,
                              constants.Keys.TEAM_NAME: self.__game_item[1].away_team_name,
                              constants.Keys.RANK: self.__get_rank(team_id=away_team_id)}

        self.__last_game_data = []
        self.__two_games_flow = []
        self.__update_line_points = []
        self.__season_level = utilities.get_season_level(current_round)
        self.__pressure_data = self.__get_event_pressure()
        self.__h2h_rating_data = self.__get_h2h_rating()

        self.__favorite_by_rank = utilities.get_favorite_by_rank(self.__home_object[constants.Keys.RANK],
                                                                 self.__away_object[constants.Keys.RANK])

    @staticmethod
    def get_value(obj: dict, keys: list):

        value = obj
        for k in keys:
            if value is not None and k in value:
                value = value[k]
                if type(value) is dict and len(value) == 0:
                    return -1
            else:
                return -1
        return value

    def __order_data(self, current_round, round_games):
        data = []
        for self.__game_item in round_games.iterrows():
            self.__initiate_game_object(current_round=current_round)
            game_data = [(self.__game_item[1].event_id, self.__game_item[1].tour_id, self.__game_item[1].season,
                          current_round, self.__season_level, self.__home_object[constants.Keys.TEAM_ID],
                          self.__home_object[constants.Keys.TEAM_NAME], self.__home_object[constants.Keys.RANK],
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.HOME, constants.Keys.RESULT, constants.Keys.BALANCE]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.HOME, constants.Keys.PSYCHOLOGY,
                                          constants.Keys.UPDATE_RATING]),
                          self.get_value(self.__h2h_rating_data, [constants.Keys.HOME]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.HOME, constants.Keys.RESULT, constants.Keys.PRESSURE_LEVEL]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.HOME, constants.Keys.RESULT, constants.Keys.IN_PERCENT]),
                          self.__pressure_by_last_game(team_id=self.__game_item[1].home_team_id),
                          str(self.__pressure_data.get(constants.Keys.HOME)),
                          self.__away_object[constants.Keys.TEAM_ID],
                          self.__away_object[constants.Keys.TEAM_NAME], self.__away_object[constants.Keys.RANK],
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.AWAY, constants.Keys.RESULT, constants.Keys.BALANCE]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.AWAY, constants.Keys.PSYCHOLOGY,
                                          constants.Keys.UPDATE_RATING]),
                          self.get_value(self.__h2h_rating_data, [constants.Keys.AWAY]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.AWAY, constants.Keys.RESULT, constants.Keys.PRESSURE_LEVEL]),
                          self.get_value(self.__pressure_data,
                                         [constants.Keys.AWAY, constants.Keys.RESULT, constants.Keys.IN_PERCENT]),
                          self.__pressure_by_last_game(team_id=self.__game_item[1].away_team_id),
                          str(self.__pressure_data.get(constants.Keys.AWAY)), self.__favorite_by_rank,
                          self.__game_item[1].favorite_by_line,
                          self.__game_item[1].initial_line_id, self.__game_item[1].final_line_id,
                          self.__game_item[1].winner_code, self.__game_item[1].start_time,
                          self.__pressure_by_line_points(odd=self.__game_item[1].initial_option_1,
                                                         home_away=1, winner_code=self.__game_item[1].winner_code,
                                                         total_odds=self.__update_line_points[0]),
                          self.__line_points_percent,
                          self.__pressure_by_line_points(odd=self.__game_item[1].initial_option_3,
                                                         home_away=2,
                                                         winner_code=self.__game_item[1].winner_code,
                                                         total_odds=self.__update_line_points[1]),
                          self.__line_points_percent,
                          f"{self.__home_object[constants.Keys.RANK]} vs {self.__away_object[constants.Keys.RANK]}")]
            data.append(game_data[0])
        if len(data) > 0:
            return data

    def run(self, specific_round: int = None):
        base_data = self.__get_base_data
        if base_data is None:
            return
        last_date = base_data[0]
        current_round = int(base_data[1])
        last_round = int(base_data[2])
        if specific_round is not None:
            current_round = specific_round
            last_round = specific_round
        while current_round <= last_round:
            round_games = self.__events[self.__events[constants.Keys.ROUND] == current_round]
            round_data = self.__order_data(current_round=current_round, round_games=round_games)
            if round_data is not None:
                self.manipulate_data(query=sql.Insert.pressure_state_template(), data=round_data)
                print(
                    f"{self.__main_data[constants.Keys.SEASON]}-R-{current_round} "
                    f"Current Round for competition id {self.__main_data[constants.Keys.TOUR_ID]}: {current_round},"
                    f" count of games for this round {len(round_data)}."
                    f" {self.__main_data[constants.Keys.SEASON]}. {current_round}/{last_round}")
            current_round += 1
