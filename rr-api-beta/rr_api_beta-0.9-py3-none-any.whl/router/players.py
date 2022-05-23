from api_utils import Routs, Keys, query, base_model, FilterData
from fastapi import APIRouter
import ast


class PlayersModel(base_model.BaseModel):
    """
    Initiate entities model
    """
    pass


router_players = APIRouter(
    prefix=f"/{Routs.PLAYERS}",
    tags=[Routs.PLAYERS]
)


@router_players.get(path="/overview/{player_id}", summary="Returns player overview")
async def overview(player_id: int):
    """
    Returns player overview by unique player_id
    """
    data = PlayersModel.Meta.database.get_data(query=query.Players.overview_base(player_id=player_id),
                                               return_data_frame=True)
    response_data = {}
    if len(data) == 1:
        response_data.setdefault(Keys.OVERVIEW, ast.literal_eval(data.overview.values[0]))
        response_data.setdefault(Keys.ACHIEVEMENTS, ast.literal_eval(data.achievements.values[0]))
        response_data.setdefault(Keys.TM_HISTORY, ast.literal_eval(data.transfer_history.values[0]))
        response_data.setdefault(Keys.ATTRIBUTES, ast.literal_eval(data.player_attributes.values[0]))
        return {Keys.DATA_TYPE: Keys.OVERVIEW,
                Keys.BASE_DATA: [response_data],
                Keys.MARKET_VALUE: data.market_value.values[0],
                Keys.TEAM_ID: int(data.team_id.values[0]),
                Keys.NAME: data.player_name.values[0],
                Keys.STATUS_CODE: 200}
    else:
        return {Keys.ERROR: Keys.NOT_FOUND_DATA}


@router_players.post(path="/stats/{player_id}", summary="Returns player overview")
async def stats(player_id: int, required_stats: list = FilterData.DEFAULT_STATS):
    """
    Returns player stays by unique player_id
    """
    return {Keys.DATA_TYPE: Keys.STATS,
            Keys.DATA:
                PlayersModel.Meta.database.get_data(query=query.Players.stats(player_id=player_id,
                                                                              required_stats=required_stats))[0],
            Keys.POSITION:
                PlayersModel.Meta.database.get_data(query=query.Players.position(player_id=player_id))[0],
            Keys.COUNT_OF_GAMES:
                PlayersModel.Meta.database.get_data(query=query.Players.count_of_games(player_id=player_id))[0],
            Keys.STATUS_CODE: 200}


@router_players.get(path="/filter/{data_type}/{object_id}", summary="Returns all players by data type")
async def compare_players(object_id: int, data_type: int = 1):
    """
        data_type:
        - current player team id: 1
        - country id: 2

        object_id:
        - the main id, need to be unique.
    """
    return {Keys.DATA_TYPE: Keys.PLAYERS,
            Keys.DATA:
                PlayersModel.Meta.database.get_data(
                    query=query.Players.players_filter(object_id=object_id, data_type=data_type))[0],
            Keys.STATUS_CODE: 200}
