import pandas as pd
from rankset.common import my_sql
from rr_psychology import common
from rr_psychology.by.common import Keys


class ExportData(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, current_pressure: bool = False):
        # initiate db instance
        super().__init__(database=common.General.DATABASE)
        # objects - part 1
        self.__main_data = main_data
        if current_pressure:
            self.__query_table = common.Tables.EVENTS_PRESSURE_DATA
        else:
            self.__query_table = common.Tables.EVENTS_PRESSURE_DATA

    @property
    def get_all_history_data(self):
        data = self.__psy_basic_data
        self.close_connection()
        if data is not None and len(data) > 0:
            return data

    @property
    def __psy_basic_data(self):
        games_data_df = self.get_data(
            query=common.sql.Get.basic_psychology(main_data=self.__main_data, query_table=self.__query_table),
            return_data_frame=True)
        temp_games_data_df = self.get_data(query=common.sql.Get.basic_psychology(main_data=self.__main_data,
                                                                                 query_table=self.__query_table,
                                                                                 home_games=False),
                                           return_data_frame=True)
        # todo: attention: the append options will be deprecated in the next pandas version
        games_data_df = games_data_df.append(temp_games_data_df, ignore_index=True).sort_values(by=Keys.START_TIME)
        return games_data_df


class Calculate(my_sql.MySqlConnection):
    def __init__(self, main_data: dict, games_df: pd.DataFrame):
        # initiate db instance and set main data
        super().__init__(database=common.General.DATABASE)
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
            if self.__games_df['round'].max() > 5:
                date_filter = self.__games_df.start_time.unique()
                last_five_dates = date_filter[len(date_filter) - 5: len(date_filter)]
                last_five_df = pd.DataFrame(data=[], columns=self.__games_df.columns)
                for date in last_five_dates:
                    # add data
                    # todo: attention: the append options will be deprecated in the next pandas version
                    last_five_df = last_five_df.append(self.__games_df[self.__games_df[Keys.START_TIME] == date])
                    # delete from main
                    self.__games_df = self.__games_df.drop(
                        self.__games_df[self.__games_df[Keys.START_TIME] == date].index)
                return last_five_df

    @property
    def __get_significance_dict(self):
        return {
            "come_back_positive": 1,
            "come_back_negative": 2,
            "get_the_lead_positive": 3,
            "get_the_lead_negative": 4,
            "come_back_to_game_positive": 5,
            "come_back_to_game_negative": 4,
            "double_lead_positive": 6,
            "double_lead_negative": 7,
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
                winner=int(objects[0][objects[0]['event_id'] == str(e)]['winner_code']
                           .values[0]), home_away=1)
        for e in away_events:
            self.__final_result(
                winner=int(objects[1][objects[1]['event_id'] == str(e)]['winner_code']
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
            'cases': self.__cases,
            'total_cases': self.__total,
            'in_percent': '{:.2f}'.format(in_percent),
            'total_games': total_games,
            'win': self.__win,
            'drew': self.__drew,
            'lost': self.__lost,
            'potential_points': total_games * 3,
            'achieved_points': (self.__win * 3) + self.__drew
        }

    def __calculate_winner_code(self):
        home_events = self.__home_positive.event_id.unique()
        away_events = self.__away_positive.event_id.unique()
        for e in home_events:
            self.__final_result(
                winner=int(self.__home_positive[self.__home_positive['event_id'] == str(e)]['winner_code']
                           .values[0]), home_away=1)
        for e in away_events:
            self.__final_result(
                winner=int(self.__away_positive[self.__away_positive['event_id'] == str(e)]['winner_code']
                           .values[0]), home_away=2)

    def __filter_basic_data(self, significance, rival_significance, home_games, away_games):
        significance = str(significance)
        self.__home_positive = home_games[home_games['significance_home'] == significance]
        self.__away_positive = away_games[away_games['significance_away'] == significance]
        rival_significance = str(rival_significance)
        self.__home_negative = home_games[home_games['significance_away'] == rival_significance]
        self.__away_negative = away_games[away_games['significance_home'] == rival_significance]
        self.__cases = len(self.__home_positive) + len(self.__away_positive)
        self.__total = len(self.__home_negative) + len(self.__away_negative)
        return self.__set_results

    @staticmethod
    def get_rating(sections: list):
        potential_points = 0
        achieved_points = 0
        for sec in sections:
            potential_points += sec.get('potential_points')
            achieved_points += sec.get('achieved_points')
        if potential_points > 0 and achieved_points > 0:
            return float('{:.2f}'.format(potential_points / achieved_points))

    def calculate(self):
        self.close_connection()
        total_rating = 0
        data = {}
        if len(self.__games_df) > 0:
            total_rating = 0
            objects = [('all season',
                        self.__games_df[self.__games_df[Keys.HOME_TEAM_ID] == self.__main_data.get(Keys.TEAM_ID)],
                        self.__games_df[self.__games_df[Keys.AWAY_TEAM_ID] == self.__main_data.get(Keys.TEAM_ID)])]
            if self.__last_five_events is not None:
                objects.append(('last 5 games', self.__last_five_events[
                    self.__last_five_events[Keys.HOME_TEAM_ID] == self.__main_data.get(Keys.TEAM_ID)],
                                self.__last_five_events[
                                    self.__last_five_events[Keys.AWAY_TEAM_ID] == self.__main_data.get(Keys.TEAM_ID)]))

            for obj in objects:
                come_back_from_losing_position = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get('come_back_positive'),
                    rival_significance=self.__get_significance_dict.get('get_the_lead_positive'), home_games=obj[1],
                    away_games=obj[2])

                lost_the_lead = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get('get_the_lead_positive'),
                    rival_significance=self.__get_significance_dict.get(
                        'come_back_positive'), home_games=obj[1], away_games=obj[2])

                double_lead = self.__filter_basic_data(
                    significance=self.__get_significance_dict.get('double_lead_positive'),
                    rival_significance=self.__get_significance_dict.get(
                        'double_lead_negative'), home_games=obj[1], away_games=obj[2])

                section_result = self.get_rating(sections=[come_back_from_losing_position, lost_the_lead])
                if section_result is not None:
                    total_rating += section_result

                data.setdefault(f'{obj[0]}', {'id': self.__main_data.get(Keys.TEAM_ID),
                                              'name': self.__main_data.get(Keys.TEAM_NAME),
                                              'tour': self.__main_data.get(Keys.TOUR_ID),
                                              'season': self.__main_data.get(Keys.SEASON),
                                              'come_back_from_losing_position': come_back_from_losing_position,
                                              'lost_the_lead': lost_the_lead,
                                              'double_lead': double_lead,
                                              'section_result': section_result})
        data.setdefault('total_rating', float('{:.2f}'.format(total_rating)))
        return data
