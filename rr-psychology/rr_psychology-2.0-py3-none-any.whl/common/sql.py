from rr_psychology.by.common.constants import Keys


class Get:
    @staticmethod
    def original_rank(main_data: dict, by_team_id: bool=False):
        if by_team_id:
            by_team_id = f" and ts.team_id = {main_data.get(Keys.TEAM_ID)}"
        return "select distinct ts.team_id, ts.team_name, " \
               "(CASE WHEN ts.total_games_avg_rank < 1.7 THEN 1 WHEN ts.total_games_avg_rank < 2.20  THEN 1.5 " \
               "WHEN ts.total_games_avg_rank < 2.5 THEN 2 WHEN ts.total_games_avg_rank < 3 THEN 2.5 " \
               "WHEN ts.total_games_avg_rank < 3.5 THEN 3 WHEN ts.total_games_avg_rank < 4 THEN 3.5 " \
               "WHEN ts.total_games_avg_rank < 4.5 THEN 4 WHEN ts.total_games_avg_rank < 5 THEN 4.5 " \
               "WHEN ts.total_games_avg_rank < 5.5 THEN 5  " \
               "ELSE 5.5 END) as general_rank, " \
               " cast((ts.sum_home_line + ts.sum_away_line) as decimal(10,2)) as sum_line " \
               " from events_data as ed, team_stock as ts " \
               f" where ed.tour_id = {main_data.get(Keys.TOUR_ID)} " \
               f" and ed.season = '{main_data.get(Keys.SEASON)}' " \
               " and ts.team_id = ed.home_team_id " \
               " and ts.tour_id = ed.tour_id " \
               " and ts.season = ed.season " \
               f"{by_team_id}" \
               f" or ed.tour_id = {main_data.get(Keys.TOUR_ID)} " \
               f" and ed.season = '{main_data.get(Keys.SEASON)}' " \
               f"{by_team_id}" \
               " and ts.team_id = ed.away_team_id " \
               " and ts.tour_id = ed.tour_id " \
               " and ts.season = ed.season " \
               " group rr_psychology ts.team_id, ts.team_name, ts.sum_home_line, " \
               " ts.sum_away_line, ts.home_success_rate_in_percent, " \
               " ts.away_success_rate_in_percent, ts.total_games_avg_rank " \
               " order rr_psychology general_rank asc;"

    @staticmethod
    def basic_psychology(main_data: dict, query_table: str, home_games: bool = True):
        if home_games:
            db_field = "home_team_id"
        else:
            db_field = "away_team_id"
        return " select ed.tour_id, ed.round, ed.home_team_id, ed.home_team_name," \
               " ed.away_team_id, ed.away_team_name, " \
               " ed.winner_code, ind.home, ind.away, ind.time_unit," \
               "(CASE WHEN time_unit <= 20 THEN 100 " \
               "WHEN time_unit > 20 and time_unit <= 35 THEN 101 " \
               "WHEN time_unit > 35 and time_unit <= 60 THEN 102 " \
               "WHEN time_unit > 60 and time_unit <= 75 THEN 103 " \
               "WHEN time_unit > 75 THEN 104 " \
               "ELSE 0 END) as time_unit_significance," \
               " ind.significance_home, " \
               " ind.significance_away, ind.object_id, ind.object_name," \
               " ind.is_home, ed.season, ed.start_time, ed.event_id " \
               f" from {query_table} as ed, indicates as ind " \
               f" where ed.tour_id = {main_data.get(Keys.TOUR_ID)} " \
               f" and ed.season = '{main_data.get(Keys.SEASON)}' " \
               f" and ed.{db_field} = {main_data.get(Keys.TEAM_ID)} " \
               f" and ed.event_id = ind.event_id " \
               " and ed.event_id = ind.event_id order rr_psychology round desc "

    @staticmethod
    def team_games(main_data: dict, pressure_view: bool):
        team_id = main_data.get(Keys.TEAM_ID)
        tour_id = main_data.get(Keys.TOUR_ID)
        season = main_data.get(Keys.SEASON)
        if not pressure_view:
            return "select ed.event_id, ed.tour_id, ed.round, ed.home_team_id, ed.home_team_name, ed.away_team_name," \
                   "ed.away_team_id, ed.winner_code, od.initial_favorite, od.final_favorite, od.initial_home, " \
                   "od.initial_drew, od.initial_away, od.initial_line_id, od.final_line_id, " \
                   " (CASE" \
                   f" WHEN ed.home_team_id = {team_id} THEN 1" \
                   " ELSE 2" \
                   " END) as home_away," \
                   " (CASE" \
                   f" WHEN ed.home_team_id = {team_id} and ed.winner_code = 1 THEN 3" \
                   f" WHEN ed.home_team_id = {team_id} and ed.winner_code = 3 THEN 1" \
                   f" WHEN ed.away_team_id = {team_id} and ed.winner_code = 2 THEN 3" \
                   f" WHEN ed.away_team_id = {team_id} and ed.winner_code = 3 THEN 1" \
                   " ELSE 0" \
                   " END) as points," \
                   "  ed.start_time from events_data as ed, odds_data as od" \
                   f" where ed.tour_id = {tour_id} " \
                   f" and ed.season = '{season}' " \
                   f" and ed.home_team_id = {team_id}" \
                   " and ed.event_id = od.event_id" \
                   f" or ed.tour_id = {tour_id} " \
                   f" and ed.season = '{season}' " \
                   f" and ed.away_team_id = {team_id}" \
                   " and ed.event_id = od.event_id" \
                   " order rr_psychology ed.start_time asc;"

        else:
            return "select event_id, tour_id, season, round," \
                   "season_level, home_team_id, home_team_name," \
                   "home_team_rank, home_level_pressure, home_level_pressure_in_percent, home_last_game_pressure," \
                   " away_team_id, away_team_name, away_team_rank," \
                   "away_level_pressure, away_level_pressure_in_percent," \
                   "away_last_game_pressure, " \
                   "favorite_by_rank, favorite_by_line, initial_line_id," \
                   "final_line_id, winner_code, start_time," \
                   "home_line_points_by_season,home_line_points_achieved_by_season, away_line_points_by_season," \
                   "away_line_points_achieved_by_season," \
                   " (CASE" \
                   f" WHEN home_team_id = {team_id} and winner_code = 1 THEN 3" \
                   f" WHEN home_team_id = {team_id} and winner_code = 3 THEN 1" \
                   f" WHEN away_team_id = {team_id} and winner_code = 2 THEN 3" \
                   f" WHEN away_team_id = {team_id} and winner_code = 3 THEN 1" \
                   " ELSE 0" \
                   " END) as points from events_pressure" \
                   f" WHERE tour_id = {tour_id} AND season = '{season}' and home_team_id = {team_id}" \
                   f" OR tour_id = {tour_id} AND season = '{season}' and away_team_id = {team_id}" \
                   " ORDER BY start_time ASC;"
