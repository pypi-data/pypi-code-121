from api_utils import Routs, Keys, query, base_model, FilterData, utils
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
        response_data.setdefault(Keys.TM_INJURY, ast.literal_eval(data.injury_history.values[0].replace('nan', 'None')))
        response_data.setdefault(Keys.ATTRIBUTES, ast.literal_eval(data.player_attributes.values[0]))
        return {Keys.DATA_TYPE: Keys.OVERVIEW,
                Keys.BASE_DATA: [response_data],
                Keys.MARKET_VALUE: data.market_value.values[0],
                Keys.TEAM_ID: int(data.team_id.values[0]),
                Keys.NAME: data.player_name.values[0],
                Keys.POSITION: utils.get_position(PlayersModel.Meta.database,
                                                  query.Players.position(player_id=player_id)),
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
            Keys.COUNT_OF_GAMES:
                PlayersModel.Meta.database.get_data(query=query.Players.count_of_games(player_id=player_id))[0],
            Keys.STATUS_CODE: 200}


@router_players.get(path="/filter/{data_type}/{object_id}", summary="Returns all players by team or country id")
async def get_players_by_id(object_id: int, data_type: int = 1):
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


@router_players.get(path="/filter/{data_type}/{object_id}/{key}", summary="Returns all players by data type and key argument")
async def get_players_by_argument_type(object_id: int, key: str, data_type: int = 1):
    """
        data_type:
        - current player team id: 1
        - country id: 2
        - position and team id: 3
        - position and country id: 4
        - age and team id: 5
        - age and country id: 6
        - market_value and team id: 7
        - market_value and country id: 8
        - combination: 6 [List]
        object_id:
        - the main id, need to be unique.
    """
    keys = key.split(', ')
    return {Keys.DATA_TYPE: Keys.PLAYERS,
            Keys.DATA:
                PlayersModel.Meta.database.get_data(
                    query=query.Players.players_filter(object_id=object_id, data_type=data_type, argument=keys))[0],
            Keys.STATUS_CODE: 200}
