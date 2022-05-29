from quart import Blueprint

blueprint = Blueprint("web_health_checker", __name__)


@blueprint.get("/is-healthy")
async def health_check():
    return "🆗"
