
from boa.admin.urls import json_render
from app import api


@api.route("/main")
@json_render
def get_main_api():
    return {
        "success": True, 
        "message": "Metodo de api para api/main"
    }

