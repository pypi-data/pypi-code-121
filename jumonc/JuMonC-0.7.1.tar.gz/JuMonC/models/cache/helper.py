import logging

from typing import Union, Optional

from JuMonC.models.cache.database import db_session
import JuMonC.models.cache.dbmodel as cache_model


logger = logging.getLogger(__name__)

def commit() -> None:
    db_session.commit()


def add_cache_entry(API_path:str) -> Optional[int]:
    entry = cache_model.CacheEntry(API_path)
    db_session.add(entry)
    commit()
    
    return entry.cache_id


def addParameter(cache_id:Optional[int], parameter_name:str, parameter_value:str) -> None:
    if not cache_id:
        logging.error("Missing cache_id")
        return
    
    parameter = cache_model.Parameter(cache_id, parameter_name, parameter_value)
    db_session.add(parameter)

    
def addResult(cache_id:Optional[int], result_name:str, result:Union[int,float,str]) -> None:
    if not cache_id:
        logging.error("Missing cache_id")
        return
    
    result_entry:Union[cache_model.ResultInt, cache_model.ResultFloat, cache_model.ResultStr]
    if isinstance(result, int):
        result_entry = cache_model.ResultInt(cache_id, result_name, result)
        logging.debug("Adding int result to cache database")
    elif isinstance(result, float):
        result_entry = cache_model.ResultFloat(cache_id, result_name, result)
        logging.debug("Adding float result to cache database")
    elif isinstance(result, str):
        result_entry = cache_model.ResultStr(cache_id, result_name, result)
        logging.debug("Adding str result to cache database")
    else:
        logging.warning("Non valid result is not added to cache database: %s", str(type(result)))
        return
    db_session.add(result_entry)