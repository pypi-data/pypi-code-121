import json

from typing import Any, Dict, Optional

import requests, ujson, zstandard

from requests.exceptions import HTTPError

from jijzept.config import Config


class JijZeptClient:
    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        proxy: Optional[str] = None,
        config: Optional[str] = None,
        config_env: str = "default",
    ):

        self.config = Config(url, token, proxy, config, config_env)
        # url = self.config.url
        # self.url = url if url[-1] != '/' else url[:-1]
        query_url = self.config.query_url
        self.query_url = query_url if query_url[-1] != "/" else query_url[:-1]

        post_url = self.config.post_url
        self.post_url = post_url if post_url[-1] != "/" else post_url[:-1]

        self.token = self.config.token

        self.proxy = self.config.proxy

        self.instance_id: Optional[str] = None
        self.req_solution_id: Optional[str] = None

    def post_instance(
        self, instance_type: str, instance: Dict[str, Any], endpoint: str = "/instance"
    ) -> Dict[str, str]:
        if not isinstance(instance_type, str):
            raise TypeError(
                "'instance_type' is `str`, not `{}`".format(type(instance_type))
            )
        if not isinstance(instance, dict):
            raise TypeError("instance is `dict`, not `{}`".format(type(instance)))

        endpoint = endpoint[:-1] if endpoint[-1] == "/" else endpoint

        # ------- Upload instance data to JijZept ---------
        upload_endpoint = self.post_url + endpoint + "/upload"
        headers = {
            "Content-Type": "application/zstd",
            "Ocp-Apim-Subscription-Key": self.token,
        }

        # encode instance
        json_data = ujson.dumps(instance)
        json_binary = json_data.encode("ascii")
        compressed_binary = zstandard.ZstdCompressor().compress(json_binary)
        res = requests.post(
            upload_endpoint,
            headers=headers,
            proxies=self.proxy,
            data=compressed_binary,
            stream=True,
        )

        status_check(res)

        # res_body => {
        #   "file_name": str
        # }
        res_body: dict = res.json()
        self.instance_data_id = res_body["instance_data_id"]
        # -----------------------------------------------

        # ---- `instance_type` registration to JijZept-API -----
        regist_endpoint = self.post_url + endpoint
        req_body = ujson.dumps(
            {"instance_type": instance_type, "instance_data_id": self.instance_data_id}
        )
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.token,
        }

        res = requests.post(
            regist_endpoint, headers=headers, proxies=self.proxy, data=req_body
        )
        status_check(res)

        self.instance_id = res.json()["instance_id"]
        # ------------------------------------------------------
        return self.instance_id

    def submit_solve_query(
        self,
        queue_name: str,
        solver_name: str,
        parameters: dict,
        instance_id: Optional[str] = None,
        timeout: Optional[float] = None,
        endpoint: str = "/query/solution",
    ):
        if self.instance_id is None and instance_id is None:
            message = "solve_request() missing 1 "
            message += "require positional argument: 'instance_id'"
            raise TypeError(message)

        if not isinstance(solver_name, str):
            raise TypeError("`solver_name` is str. not {}".format(type(solver_name)))

        if not isinstance(parameters, dict):
            raise TypeError("`parameters` is dict. not {}".format(type(parameters)))

        instance_id = self.instance_id if instance_id is None else instance_id

        query_endopoint = self.query_url + endpoint
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.token,
        }

        json_data = ujson.dumps(
            {
                "instance_id": instance_id,
                "solver_params": parameters,
                "queue_name": queue_name,
                "solver": solver_name,
                "timeout": timeout,
            }
        )
        res = requests.post(
            query_endopoint, headers=headers, proxies=self.proxy, data=json_data
        )
        status_check(res)

        # res_body => {
        #   "solution_id": str,
        # }
        res_body: dict = res.json()
        self.req_solution_id = res_body["solution_id"]

        return res_body

    def fetch_result(
        self, solution_id: Optional[str] = None, endpoint: str = "/query/solution"
    ) -> dict:
        if self.req_solution_id is None and solution_id is None:
            message = "fetch_result() missing 1 "
            message += "require positional argument: 'solution_id'"
            raise TypeError(message)

        solution_id = self.req_solution_id if solution_id is None else solution_id

        fetch_endpoint = self.query_url + endpoint

        headers = {"Ocp-Apim-Subscription-Key": self.token}

        params = {"solution_id": solution_id}

        res = requests.get(
            fetch_endpoint, headers=headers, proxies=self.proxy, params=params
        )

        status_check(res)

        res_body = res.json()
        if res_body is None:
            raise HTTPError("solution_id is not found")

        return res_body


def status_check(res) -> None:
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        res = e.response
        try:
            res_body = res.json()
        except json.decoder.JSONDecodeError:
            raise requests.exceptions.HTTPError(e)

        raise requests.exceptions.HTTPError(e, res_body)
