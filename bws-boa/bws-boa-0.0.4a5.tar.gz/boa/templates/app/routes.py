template="""
from boa.admin.urls import json_render
from app import api


@api.route("/%(app)s")
@json_render
def get_%(app)s_api():
    return {
        "success": True, 
        "message": "Metodo de api para api/%(app)s"
    }

"""