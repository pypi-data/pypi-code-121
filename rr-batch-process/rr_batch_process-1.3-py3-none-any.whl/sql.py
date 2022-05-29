class Get:
    @staticmethod
    def get_events(tour_id: int, season: str, main_table: str, team_id: int = None):
        if not team_id:
            return " SELECT a.event_id, a.tour_id, a.season, a.round, a.home_team_id, a.home_team_name, " \
                   " a.away_team_id, a.away_team_name, b.initial_favorite as favorite_by_line," \
                   " b.initial_option_1, b.initial_option_2, b.initial_option_3, b.initial_line_id, b.final_line_id, " \
                   f" a.winner_code, a.start_time FROM odds AS b, {main_table} AS a " \
                   f" WHERE a.tour_id = {tour_id} AND a.season = '{season}' and b.market_id = 1 " \
                   " AND a.event_id = b.event_id AND a.start_time = b.start_time " \
                   " ORDER BY a.start_time ASC;"
        else:
            return " SELECT a.event_id, a.tour_id, a.season, a.round, a.home_team_id, a.home_team_name, " \
                   " a.away_team_id, a.away_team_name, b.initial_favorite as favorite_by_line," \
                   " b.initial_option_1, b.initial_option_2, b.initial_option_3, b.initial_line_id, b.final_line_id, " \
                   f" a.winner_code, a.start_time FROM odds_data AS b, {main_table} AS a " \
                   f" WHERE a.tour_id = {tour_id} AND a.season = '{season}' and b.market_id = 1 " \
                   f" AND a.home_team_id = {team_id} AND a.event_id = b.event_id AND a.start_time = b.start_time " \
                   f" OR a.tour_id = {tour_id} AND a.season = '{season}' and b.market_id = 1 " \
                   f" AND a.away_team_id = {team_id}  AND a.event_id = b.event_id " \
                   " AND a.start_time = b.start_time ORDER BY a.start_time ASC;"

    @staticmethod
    def get_original_rank(tour_id: int, season: str = '21/22'):
        return "select distinct ts.team_id, ts.team_name, " \
               "(CASE WHEN ts.total_games_avg_rank < 1.7 THEN 1 WHEN ts.total_games_avg_rank < 2.20  THEN 1.5 " \
               "WHEN ts.total_games_avg_rank < 2.5 THEN 2 WHEN ts.total_games_avg_rank < 3 THEN 2.5 " \
               "WHEN ts.total_games_avg_rank < 3.5 THEN 3 WHEN ts.total_games_avg_rank < 4 THEN 3.5 " \
               "WHEN ts.total_games_avg_rank < 4.5 THEN 4 WHEN ts.total_games_avg_rank < 5 THEN 4.5 " \
               "WHEN ts.total_games_avg_rank < 5.5 THEN 5  " \
               "ELSE 5.5 END) as general_rank, " \
               " cast((ts.sum_home_line + ts.sum_away_line) as decimal(10,2)) as sum_line " \
               " from events_data as ed, team_stock as ts " \
               f" where ed.tour_id = {tour_id} " \
               f" and ed.season = '{season}' " \
               " and ts.team_id = ed.home_team_id " \
               " and ts.tour_id = ed.tour_id " \
               " and ts.season = ed.season " \
               f" or ed.tour_id = {tour_id} " \
               f" and ed.season = '{season}' " \
               " and ts.team_id = ed.away_team_id " \
               " and ts.tour_id = ed.tour_id " \
               " and ts.season = ed.season " \
               " group by ts.team_id, ts.team_name, ts.sum_home_line, " \
               " ts.sum_away_line, ts.home_success_rate_in_percent, " \
               " ts.away_success_rate_in_percent, ts.total_games_avg_rank " \
               " order by general_rank asc;"

    @staticmethod
    def get_momentum(tour_id: int, team_id: int, season: str):
        return "select home_team_id, away_team_id, " \
               f"(CASE WHEN home_team_id = {team_id} THEN 'H' ELSE 'A' END) as home_or_away, " \
               f"(CASE WHEN home_team_id = {team_id} THEN away_team_rank ELSE home_team_rank END) as against_rank," \
               f"(CASE WHEN home_team_id = {team_id} and favorite_by_rank = 1 and winner_code = 1 THEN 0 " \
               f"WHEN away_team_id = {team_id} and favorite_by_rank = 2 and winner_code = 2 THEN 0 " \
               f"WHEN home_team_id = {team_id} and favorite_by_rank = 1 and winner_code != 1 THEN 2 " \
               f"WHEN away_team_id = {team_id} and favorite_by_rank = 2 and winner_code != 2 THEN 2 " \
               f"WHEN home_team_id = {team_id} and favorite_by_rank = 2 and winner_code = 2 THEN 1 " \
               f"WHEN away_team_id = {team_id} and favorite_by_rank = 1 and winner_code = 2 THEN 1 " \
               f"WHEN home_team_id = {team_id} and favorite_by_rank = 3 and winner_code = 2 THEN 2 " \
               f"WHEN away_team_id = {team_id} and favorite_by_rank = 3 and winner_code = 1 THEN 1 " \
               "ELSE 0 END) as pressure_level_by_rank, " \
               f"(CASE WHEN home_team_id = {team_id} and favorite_by_line = 1 and winner_code = 1 THEN 0 " \
               f"WHEN away_team_id = {team_id} and favorite_by_line = 2 and winner_code = 2 THEN 0 " \
               f"WHEN home_team_id = {team_id} and favorite_by_line = 1 and winner_code != 1 THEN 2 " \
               f"WHEN away_team_id = {team_id} and favorite_by_line = 2 and winner_code != 2 THEN 2 " \
               f"WHEN home_team_id = {team_id} and favorite_by_line = 2 and winner_code = 2 THEN 1 " \
               f"WHEN away_team_id = {team_id} and favorite_by_line = 1 and winner_code = 2 THEN 1 " \
               f"WHEN home_team_id = {team_id} and favorite_by_line = 3 and winner_code = 2 THEN 2 " \
               f"WHEN away_team_id = {team_id} and favorite_by_line = 3 and winner_code = 1 THEN 1 " \
               "ELSE 0 END) as pressure_level_by_line, " \
               f"(CASE WHEN home_team_id = {team_id} and winner_code = 1 THEN 'W' " \
               f"WHEN away_team_id = {team_id} and winner_code = 2 THEN 'W' " \
               f"WHEN home_team_id = {team_id} and winner_code = 2 THEN 'L' " \
               f"WHEN away_team_id = {team_id} and winner_code = 1 THEN 'L' " \
               "ELSE 'D' END) as momentum, " \
               " winner_code, season_level, round," \
               f"(CASE WHEN home_team_id = {team_id} THEN home_line_points_by_season " \
               "ELSE away_line_points_by_season END) as update_line_points," \
               f"start_time, (CASE WHEN home_team_id = {team_id} THEN home_level_pressure ELSE away_level_pressure END)" \
               f" as current_pressure from events_pressure " \
               f"where tour_id = {tour_id} " \
               f"and home_team_id = {team_id} " \
               f"and season = '{season}' " \
               f"or tour_id = {tour_id} " \
               f"and away_team_id = {team_id} " \
               f"and season = '{season}' " \
               "order by start_time desc " \
               "limit 2"

    @staticmethod
    def get_goals_data(tour_id: int, team_id: int):
        return "select ed.start_time, ed.tour_id," \
               f"CONCAT(ed.home_team_name,' vs ', ed.away_team_name) as team_name," \
               f"(CASE WHEN ed.home_team_id != {team_id} THEN ed.home_team_name " \
               "ELSE ed.away_team_name END) as rival_name," \
               f"(CASE WHEN ed.home_team_id = {team_id} THEN CONVERT(SUBSTRING(ed.full_time, 1, 1), UNSIGNED INTEGER) " \
               "ELSE CONVERT(SUBSTRING(ed.full_time, 3, 1), UNSIGNED INTEGER) END) as team_goals, " \
               f"(CASE WHEN ed.home_team_id != {team_id} THEN CONVERT(SUBSTRING(ed.full_time, 1, 1), UNSIGNED INTEGER) " \
               "ELSE CONVERT(SUBSTRING(ed.full_time, 3, 1), UNSIGNED INTEGER) END) as rival_goals, ed.winner_code " \
               "from events_data as ed, events_pressure as ep " \
               f"where ep.event_id = ed.event_id and ed.tour_id = {tour_id} and ed.home_team_id = {team_id} " \
               "group by ed.start_time, ed.tour_id, ed.home_team_id," \
               " ed.away_team_id, ed.home_team_name, ed.away_team_name, ed.full_time, ed.winner_code " \
               "order by ed.start_time asc"


class Insert:
    @staticmethod
    def pressure_state_template():
        return "INSERT INTO events_pressure (event_id, tour_id, season, round," \
               "season_level, home_team_id, home_team_name," \
               "home_team_rank, home_pressure_balance, home_total_psy_rating, home_h2h_rating," \
               "home_level_pressure, home_level_pressure_in_percent, home_last_game_pressure," \
               "home_rank_pressure, away_team_id, away_team_name," \
               "away_team_rank, away_pressure_balance, away_total_psy_rating, away_h2h_rating," \
               "away_level_pressure, away_level_pressure_in_percent," \
               "away_last_game_pressure, away_rank_pressure, favorite_by_rank, favorite_by_line, initial_line_id," \
               "final_line_id, winner_code, start_time," \
               "home_line_points_by_season,home_line_points_achieved_by_season, away_line_points_by_season," \
               "away_line_points_achieved_by_season, rank_vs_rank_description)" \
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" \
               ",%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    @staticmethod
    def pressure_patterns_template():
        return "INSERT INTO event_pattern (event_id, tour_id, season," \
               "home_team_id, away_team_id, winner_code, pattern_type, pattern_desc, final_pattern," \
               " rank_vs_rank_description, home_psy, away_psy) " \
               "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    @staticmethod
    def pressure_simulations_template():
        return "INSERT INTO simulation (tour_id, tour_name, event_id, event_obj, start_time) " \
               "VALUES (%s,%s,%s,%s,%s)"
