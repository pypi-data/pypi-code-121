import api_utils as au
from peewee import CharField
from fastapi import APIRouter


class OverviewModel(base_model.BaseModel):
    id = CharField(max_length=30)
    name = CharField(max_length=30)
    overview_object = CharField(max_length=1000)


router_data = APIRouter(
    prefix=f"/{constants.Routs.DATA}",
    tags=[constants.Routs.DATA]
)


@router_data.get(path="/overview/{player_id}", summary="Returns player overview")
async def overview(player_id: int):
    """
    Returns player overview by player_id
    """
    return {constants.Keys.DATA_TYPE: constants.Keys.OVERVIEW,
            constants.Keys.DATA:
                OverviewModel.Meta.database.get_data(query=query.Players.players_overview(player_id=player_id))[0],
            constants.Keys.STATUS_CODE: 200}
