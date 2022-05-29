from flask import Blueprint

blueprint = Blueprint("web_health_checker", __name__)


@blueprint.get("/is-healthy")
def health_check():
    return "🆗"
