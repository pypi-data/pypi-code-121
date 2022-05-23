"""The authentication package of JuMonC provides functionality to authenticate users using the REST-API."""


import logging


logger = logging.getLogger(__name__)

scope_name = {
    0: "see_links",
    5: "retrieve_data",
    10: "compute_data",
    15: "retrieve_simulation_data",
    20: "compute_simulation_data",
    100: "full"
}
    

scopes = {
    scope_name[0]: 0,
    scope_name[5]: 5,
    scope_name[10]: 10,
    scope_name[15]: 15,
    scope_name[20]: 20,
    scope_name[100]: 100
}