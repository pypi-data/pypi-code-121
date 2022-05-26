class BaseEntities:
    @staticmethod
    def countries():
        return "select rc.wyscout_id as id, rc.rankset_name as name from rankset.countries as rc " \
               "where rc.wyscout_id != 0 order by name asc;"

    @staticmethod
    def competitions(country_id: int):
        return f"select * from wyscout.competitions where country_id = {country_id};"

    @staticmethod
    def teams(competition_id: int):
        return f"select yt.competition_id, rt.rankset_id as id, rt.rankset_name as name from rankset.teams as rt, wyscout.teams as yt " \
               f"where rt.wyscout_id = yt.id and yt.competition_id = {competition_id};"

    @staticmethod
    def players(team_id: int):
        return "select distinct yp.team_id, rp.wyscout_id as id, rp.rankset_name as name from rankset.players as rp, wyscout.player_object as yp " \
               f" where rp.wyscout_id = yp.player_id and rp.main_id = {team_id};"


class Players:
    @staticmethod
    def players_filter(object_id: int, data_type: int, argument: list = None):
        """  Returns all players by data type "
            - **current player team id **: 1
            - **country id **: 2
        """
        match data_type:
            case 1:
                return "select distinct rp.wyscout_id as id, rp.rankset_name as name from rankset.players as rp, wyscout.player_object as yp " \
                       f"where rp.wyscout_id = yp.player_id and rp.main_id = {object_id};"
            case 2:
                return f"select distinct player_id, player_name from wyscout.player_object where country_id = {object_id};"
            case 3 | 4:
                if len(argument) == 1:
                    argument = f"('{argument[0]}')"
                else:
                    argument = tuple(argument)
                return "select distinct player_id, player_name from wyscout.player_object as wp " \
                       f"where wp.{get_field(data_type)} = {object_id} and exists (select * from rankset.position_metadata rp " \
                       f"where rp.player_id = wp.player_id and rp.position != 'n' and rp.position in {str(argument)}) " \
                       "group by player_id, player_name;"

    @staticmethod
    def overview_base(player_id: int):
        return f"select player_name, market_value, overview, achievements, transfer_history, injury_history, player_attributes, team_id " \
               f"from rankset.player_metadata as rpm " \
               f"where exists (select * from rankset.players as rp where rp.wyscout_id = {player_id} " \
               "and rpm.player_id = rp.rankset_id) limit 1;"

    @staticmethod
    def stats(player_id: int, required_stats: list):
        required_stat = str(required_stats).replace('[', '(').replace(']', ')')
        return "select distinct stat_name, " \
               "cast(sum(stat_value) / (select count(distinct event_id) from wyscout.player_statistics " \
               f"where object_id = {player_id}) as decimal(10,2)) as stat_value " \
               f"from wyscout.player_statistics where object_id = {player_id} " \
               f"and stat_name in {required_stat} group by stat_name order by stat_name asc;"

    @staticmethod
    def count_of_games(player_id: int):
        return f"select count(distinct event_id) from wyscout.player_statistics where object_id = {player_id};"

    @staticmethod
    def position(player_id: int):
        return f"select stat_value from wyscout.player_statistics where object_id = {player_id} " \
               "and stat_name = 'positions' order by date desc limit 1;"


def get_field(num):
    cal = num % 2
    if cal != 0:
        return 'team_id'
    else:
        return 'country_id'
