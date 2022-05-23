class BaseEntities:
    @staticmethod
    def countries():
        return "select * from wyscout.countries;"

    @staticmethod
    def competitions(country_id: int):
        return f"select * from wyscout.competitions where country_id = {country_id};"

    @staticmethod
    def teams(competition_id: int):
        return f"select * from wyscout.teams where competition_id = {competition_id};"

    @staticmethod
    def players(team_id: int):
        return f"select distinct team_id, player_id, player_name from player_object where team_id = {team_id};"


class Data:
    @staticmethod
    def players_overview(player_id: int):
        return f"select overview_object from wyscout.player_object where player_id = {player_id} limit 1;"
