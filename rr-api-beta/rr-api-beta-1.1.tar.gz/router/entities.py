from fastapi import APIRouter
from api_utils import Routs, Keys, query, base_model


class EntitiesModel(base_model.BaseModel):
    """
    Initiate entities model
    """
    pass


router_entities = APIRouter(
    prefix=f"/{Routs.ENTITIES}",
    tags=[Routs.ENTITIES])


@router_entities.get(path=f"/countries", summary="Returns all countries")
async def countries():
    """
    Returns all competitions by country id
    """
    return {Keys.DATA_TYPE: Keys.COUNTRIES,
            Keys.DATA:
                EntitiesModel.Meta.database.get_data(query=query.BaseEntities.countries())[0],
            Keys.STATUS_CODE: 200}


@router_entities.get(path="/competitions/{country_id}", summary="Returns all competitions by country id")
async def competitions(country_id: int):
    """
        Returns all competitions by country id
        - **country**: The country unique id.
    """
    return {Keys.DATA_TYPE: Keys.COMPETITIONS,
            Keys.DATA:
                EntitiesModel.Meta.database.get_data(
                    query=query.BaseEntities.competitions(country_id=country_id))[0],
            Keys.STATUS_CODE: 200}


@router_entities.get(path="/teams/{competition_id}", summary="Returns all teams by competition id")
async def teams(competition_id: int):
    """
        Returns all teams by country and competition id"
        - **competition**: The competition unique id.
    """
    return {Keys.DATA_TYPE: Keys.TEAMS,
            Keys.DATA:
                EntitiesModel.Meta.database.get_data(
                    query=query.BaseEntities.teams(competition_id=competition_id))[
                    0],
            Keys.STATUS_CODE: 200}


@router_entities.get(path="/players/{team_id}",
                     summary="Returns all players by team id")
async def players(team_id: int):
    """
        Returns all players by country, competition and team id
        - **team**: The team unique id.
    """
    return {Keys.DATA_TYPE: Keys.PLAYERS,
            Keys.DATA:
                EntitiesModel.Meta.database.get_data(query=query.BaseEntities.players(team_id=team_id))[
                    0], Keys.STATUS_CODE: 200}
