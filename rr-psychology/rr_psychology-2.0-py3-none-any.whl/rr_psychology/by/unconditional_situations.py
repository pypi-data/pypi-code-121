import pandas as pd
from rr import my_sql
import rr_psychology


class ExportData(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, current_pressure: bool = False):
        # initiate db instance
        super().__init__(database=rr_psychology.by.common.General.DATABASE)
        # objects - part 1
        self.__main_data = main_data
        if current_pressure:
            self.__query_table = rr_psychology.by.common.Tables.EVENTS_PRESSURE_DATA
        else:
            self.__query_table = rr_psychology.by.common.Tables.EVENTS_PRESSURE_DATA

    @property
    def get_all_history_data(self):
        data = self.__psy_basic_data
        self.close_connection()
        if data is not None and len(data) > 0:
            return data

    @property
    def __psy_basic_data(self):
        home_games_df = self.get_data(
            query=rr_psychology.by.common.sql.Get.basic_psychology(main_data=self.__main_data,
                                                                   query_table=self.__query_table),
            return_data_frame=True)
        away_games_df = self.get_data(query=rr_psychology.by.common.sql.Get.basic_psychology(main_data=self.__main_data,
                                                                                             query_table=self.__query_table,
                                                                                             home_games=False),
                                      return_data_frame=True)
        return pd.concat([home_games_df, away_games_df], ignore_index=True).sort_values(
            by=rr_psychology.by.common.Keys.START_TIME)


class Calculate(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, games_df: pd.DataFrame):
        # initiate db instance and set main data
        super().__init__(database=rr_psychology.by.common.General.DATABASE)
        self.__main_data = main_data
        self.__games_df = games_df
        # part 1 - set base games objects
        self.__last_five_events = self.__export_last_five_games
        self.__df = None
        self.__home_positive = None
        self.__home_negative = None
        self.__away_positive = None
        self.__away_negative = None
        self.__cases = None
        self.__total = None
        self.__win = None
        self.__drew = None
        self.__lost = None
        self.__live = False
        self.__positive = False

    @property
    def __export_last_five_games(self):
        if len(self.__games_df) > 0:
            if self.__games_df[rr_psychology.by.common.Keys.ROUND].max() > 5:
                date_filter = self.__games_df.start_time.unique()
                last_five_dates = date_filter[len(date_filter) - 5: len(date_filter)]
                last_five_df = pd.DataFrame(data=[], columns=self.__games_df.columns)
                for date in last_five_dates:
                    temp = self.__games_df[self.__games_df[rr_psychology.by.common.Keys.START_TIME] == date]
                    last_five_df = pd.concat([last_five_df, temp], ignore_index=True).sort_values(
                        by=rr_psychology.by.common.Keys.START_TIME)
                    # delete from main
                    self.__games_df = self.__games_df.drop(
                        self.__games_df[self.__games_df[rr_psychology.by.common.Keys.START_TIME] == date].index)
                return last_five_df

    @property
    def __get_significance_dict(self):
        return {
            rr_psychology.by.common.Keys.COME_BACK_POSITIVE: 1,
            rr_psychology.by.common.Keys.COME_BACK_NEGATIVE: 2,
            rr_psychology.by.common.Keys.GET_THE_LEAD_POSITIVE: 3,
            rr_psychology.by.common.Keys.GET_THE_LEAD_NEGATIVE: 4,
            rr_psychology.by.common.Keys.COME_BACK_TO_THE_GAME_POSITIVE: 5,
            rr_psychology.by.common.Keys.COME_BACK_TO_THE_GAME_NEGATIVE: 4,
            rr_psychology.by.common.Keys.DOUBLE_LEAD_POSITIVE: 6,
            rr_psychology.by.common.Keys.DOUBLE_LEAD_NEGATIVE: 7,
        }

    def __final_result(self, winner: int, home_away: int):
        if home_away == 1:
            if winner == 1:
                self.__win += 1
            elif winner == 2:
                self.__lost += 1
            else:
                self.__drew += 1

        else:
            if winner == 2:
                self.__win += 1
            elif winner == 1:
                self.__lost += 1
            else:
                self.__drew += 1

    def __calculate_winner_code_live(self):
        if self.__positive:
            home_events = self.__home_positive.event_id.unique()
            away_events = self.__away_positive.event_id.unique()
            objects = self.__home_positive, self.__away_positive
        else:
            home_events = self.__home_negative.event_id.unique()
            away_events = self.__away_negative.event_id.unique()
            objects = self.__home_negative, self.__away_negative

        for e in home_events:
            self.__final_result(
                winner=int(objects[0][objects[0][rr_psychology.by.common.Keys.EVENT_ID] == str(e)][
                               rr_psychology.by.common.Keys.WINNER_CODE]
                           .values[0]), home_away=1)
        for e in away_events:
            self.__final_result(
                winner=int(objects[1][objects[1][rr_psychology.by.common.Keys.EVENT_ID] == str(e)][
                               rr_psychology.by.common.Keys.WINNER_CODE]
                           .values[0]), home_away=2)

    @property
    def __set_results(self):
        self.__win = 0
        self.__drew = 0
        self.__lost = 0
        self.__calculate_winner_code()
        if self.__total < self.__cases:
            temp = self.__cases
            self.__cases = self.__total
            self.__total = temp

        if self.__total == 0 or self.__cases == 0:
            in_percent = 0
        else:
            in_percent = (self.__cases / self.__total) * 100

        total_games = self.__win + self.__drew + self.__lost
        return {
            rr_psychology.by.common.Keys.CASES: self.__cases,
            rr_psychology.by.common.Keys.TOTAL_CASES: self.__total,
            rr_psychology.by.common.Keys.IN_PERCENT: rr_psychology.by.common.General.DECIMAL_FORMAT.format(in_percent),
            rr_psychology.by.common.Keys.TOTAL_GAMES: total_games,
            rr_psychology.by.common.Keys.WIN: self.__win,
            rr_psychology.by.common.Keys.DREW: self.__drew,
            rr_psychology.by.common.Keys.LOST: self.__lost,
            rr_psychology.by.common.Keys.POTENTIAL_POINTS: total_games * 3,
            rr_psychology.by.common.Keys.ACHIEVED_POINTS: (self.__win * 3) + self.__drew

        }

    def __calculate_winner_code(self):
        home_events = self.__home_positive.event_id.unique()
        away_events = self.__away_positive.event_id.unique()
        for e in home_events:
            self.__final_result(
                winner=int(self.__home_positive[self.__home_positive[rr_psychology.by.common.Keys.EVENT_ID] == str(e)][
                               rr_psychology.by.common.Keys.WINNER_CODE]
                           .values[0]), home_away=1)
        for e in away_events:
            self.__final_result(
                winner=int(self.__away_positive[self.__away_positive[rr_psychology.by.common.Keys.EVENT_ID] == str(e)][
                               rr_psychology.by.common.Keys.WINNER_CODE]
                           .values[0]), home_away=2)

    def __filter_basic_data(self, significance, rival_significance, home_games, away_games):
        significance = str(significance)
        self.__home_positive = home_games[home_games[rr_psychology.by.common.Keys.SIGNIFICANCE_HOME] == significance]
        self.__away_positive = away_games[away_games[rr_psychology.by.common.Keys.SIGNIFICANCE_AWAY] == significance]
        rival_significance = str(rival_significance)
        self.__home_negative = home_games[
            home_games[rr_psychology.by.common.Keys.SIGNIFICANCE_AWAY] == rival_significance]
        self.__away_negative = away_games[
            away_games[rr_psychology.by.common.Keys.SIGNIFICANCE_HOME] == rival_significance]
        self.__cases = len(self.__home_positive) + len(self.__away_positive)
        self.__total = len(self.__home_negative) + len(self.__away_negative)
        return self.__set_results

    @staticmethod
    def get_rating(sections: list):
        potential_points = 0
        achieved_points = 0
        for sec in sections:
            potential_points += sec.get(rr_psychology.by.common.Keys.POTENTIAL_POINTS)
            achieved_points += sec.get(rr_psychology.by.common.Keys.ACHIEVED_POINTS)
        if potential_points > 0 and achieved_points > 0:
            return float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(potential_points / achieved_points))

    def calculate(self):
        self.close_connection()
        total_rating = 0
        data = {}
        if len(self.__games_df) > 0:
            total_rating = 0
            objects = [(rr_psychology.by.common.Keys.ALL_SEASON,
                        self.__games_df[
                            self.__games_df[rr_psychology.by.common.Keys.HOME_TEAM_ID] == self.__main_data.get(
                                rr_psychology.by.common.Keys.TEAM_ID)],
                        self.__games_df[
                            self.__games_df[rr_psychology.by.common.Keys.AWAY_TEAM_ID] == self.__main_data.get(
                                rr_psychology.by.common.Keys.TEAM_ID)])]
            if self.__last_five_events is not None:
                objects.append((rr_psychology.by.common.Keys.LAST_5_GAMES, self.__last_five_events[
                    self.__last_five_events[rr_psychology.by.common.Keys.HOME_TEAM_ID] == self.__main_data.get(
                        rr_psychology.by.common.Keys.TEAM_ID)],
                                self.__last_five_events[
                                    self.__last_five_events[
                                        rr_psychology.by.common.Keys.AWAY_TEAM_ID] == self.__main_data.get(
                                        rr_psychology.by.common.Keys.TEAM_ID)]))

            for obj in objects:
                come_back_from_losing_position = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get(rr_psychology.by.common.Keys.COME_BACK_POSITIVE),
                    rival_significance=self.__get_significance_dict.get(
                        rr_psychology.by.common.Keys.GET_THE_LEAD_POSITIVE),
                    home_games=obj[1],
                    away_games=obj[2])

                lost_the_lead = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get(rr_psychology.by.common.Keys.GET_THE_LEAD_POSITIVE),
                    rival_significance=self.__get_significance_dict.get(
                        rr_psychology.by.common.Keys.COME_BACK_POSITIVE), home_games=obj[1], away_games=obj[2])

                double_lead = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get(rr_psychology.by.common.Keys.DOUBLE_LEAD_POSITIVE),
                    rival_significance=self.__get_significance_dict.get(
                        rr_psychology.by.common.Keys.DOUBLE_LEAD_NEGATIVE), home_games=obj[1], away_games=obj[2])

                section_result = self.get_rating(sections=[come_back_from_losing_position, lost_the_lead])
                if section_result is not None:
                    total_rating += section_result
                data.setdefault(obj[0], {
                    rr_psychology.by.common.Keys.ID: self.__main_data.get(rr_psychology.by.common.Keys.TEAM_ID),
                    rr_psychology.by.common.Keys.NAME: self.__main_data.get(rr_psychology.by.common.Keys.TEAM_NAME),
                    rr_psychology.by.common.Keys.TOUR: self.__main_data.get(rr_psychology.by.common.Keys.TOUR_ID),
                    rr_psychology.by.common.Keys.SEASON: self.__main_data.get(rr_psychology.by.common.Keys.SEASON),
                    rr_psychology.by.common.Keys.COME_BACK_FROM_LOSING_POSITION: come_back_from_losing_position,
                    rr_psychology.by.common.Keys.LOST_THE_LEAD: lost_the_lead,
                    rr_psychology.by.common.Keys.DOUBLE_LEAD: double_lead,
                    rr_psychology.by.common.Keys.SECTION_RESULT: section_result})
        total_rating = float(rr_psychology.by.common.General.DECIMAL_FORMAT.format(total_rating))
        data.setdefault(rr_psychology.by.common.Keys.TOTAL_RATING, total_rating)
        return data, total_rating
