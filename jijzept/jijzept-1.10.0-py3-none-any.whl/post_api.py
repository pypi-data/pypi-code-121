import logging, sys, time

from logging import getLogger
from typing import Any, Dict, Optional, Type, TypeVar

from jijzept.client import JijZeptClient
from jijzept.response import APIStatus, BaseResponse

ResponseType = TypeVar("ResponseType", bound=BaseResponse)

logger = getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# set the default timeout to 60 min if not specified.
DEFAULT_TIMEOUT_SEC = 3600


def post_instance_and_query(
    ResponseType: Type[TypeVar("ResponseType", bound="BaseResponse")],
    client: JijZeptClient,
    instance_type: str,
    instance: Dict[str, Any],
    queue_name: str,
    solver: str,
    parameters: dict,
    timeout: Optional[float],
    sync: bool = True,
):

    # Instance を投げる
    logger.info("uploading instance ...")
    instance_id = client.post_instance(instance_type, instance)

    # Solverにqueryをなげる
    logger.info("submitting query ...")
    actual_timeout = DEFAULT_TIMEOUT_SEC if timeout is None else timeout
    solver_res = client.submit_solve_query(
        queue_name, solver, parameters, instance_id, actual_timeout
    )
    logger.info(f"submitted to the queue.")
    logger.info(f'Your solution_id is {solver_res["solution_id"]}.')

    # 同期モードで解を取得
    status = "PENDING"
    show_running_flag = False
    if sync:
        polling_count = 0
        while (status == APIStatus.PENDING.value) or (
            status == APIStatus.RUNNING.value
        ):
            response = client.fetch_result(solver_res["solution_id"])
            status = response["status"]
            if (
                response["status"] == APIStatus.RUNNING.value
                and show_running_flag == False
            ):
                logger.info("running...")
                show_running_flag = True
            elif response["status"] == APIStatus.SUCCESS.value:
                break
            elif response["status"] == APIStatus.FAILED.value:
                return ResponseType.empty_response(
                    APIStatus.FAILED,
                    client,
                    solver_res["solution_id"],
                    err_dict=response["solution"],
                )

            elif response["status"] == APIStatus.UNKNOWNERROR.value:
                return ResponseType.empty_response(
                    APIStatus.UNKNOWNERROR, client, solver_res["solution_id"]
                )

            time.sleep(2)
            polling_count = polling_count + 1

            if polling_count == 10:
                # show hints if polling is repeated certain times
                logger.info(f"It takes a lot of time to get the solution...")
                logger.info(f"You can also access the solution by")
                logger.info(f">>> a = XXXSampler(config=...)")
                logger.info(f'>>> a.get_result("{solver_res["solution_id"]}")')

    else:
        logger.info(f"You can access the solution by")
        logger.info(f">>> a = XXXSampler(config=...)")
        logger.info(f'>>> a.get_result("{solver_res["solution_id"]}")')
        return ResponseType.empty_response(
            APIStatus.PENDING, client, solver_res["solution_id"]
        )

    res_obj = ResponseType.from_json_obj(response["solution"])
    res_obj.set_status(APIStatus.SUCCESS)
    return res_obj
