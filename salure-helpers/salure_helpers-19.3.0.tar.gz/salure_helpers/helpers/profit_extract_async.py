import json
import asyncio
import time
from typing import Union, List, Coroutine
import pandas as pd
import aiohttp


class ProfitExtractAsync:
    def __init__(self, environment: str, base64token: str, base_url: str = 'rest.afas.online', debug=False):
        self.environment = environment
        self.base_url = base_url
        self.base64token = base64token
        self.got_all_results = False
        self.debug = debug

    async def get_data(self, connectors: List = None, parameters: dict = {}, batch_size: int = 8, take: int = 40000) -> dict:
        """
        This (asynchronous) function functions as a wrapper that can carry out multiple single get requests to be able
        to get all data from profit in an asynchronous and efficient way. Note that this function cannot be called in itself,
        but has to be called via a synchronous function.

        :param connectors: Names of the connectors to be extracted. If not provided, keys of parameters dict will be used
        :param parameters: multilevel dict of filters per connector. Key must always be the connector, then dict like {connector: {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        :return: data in json format
        """
        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/'
        authorization_header = {'Authorization': 'AfasToken {}'.format(self.base64token)}
        batch_number = 0

        total_response = {}
        self.got_all_results = False
        while not self.got_all_results:
            async with aiohttp.ClientSession(headers=authorization_header, timeout=aiohttp.ClientTimeout()) as session:
                requests = [self.get_request(url=url,
                                             connector=connector,
                                             params={**(parameters[connector] if connector in parameters.keys() else {}), **{
                                                 "skip": take * (i + batch_number * batch_size),
                                                 "take": take}},
                                             session=session,
                                             take=take) for i in range(batch_size) for connector in connectors]
                response = await asyncio.gather(*requests)

                if len(response) > 0:
                    if any([isinstance(item, Coroutine) for item in response]):
                        return {"Message": "One or more requests have failed. Please try again"}
                    for item in response:
                        for key, value in item.items():
                            if key in total_response.keys():
                                total_response[key].extend(value)
                            else:
                                total_response[key] = value

                batch_number += 1

        return total_response

    async def get_request(self, url: str, connector: str, params: dict, session: aiohttp.ClientSession, take: int):
        """
        This function carries out a single get request given the inputs. It is used as input for the abovementioned wrapper,
        get_data_content. Note that this function cannot be called it itself, but has to be started via get_data_content.

        :param url: profit url to retrieve the data.
        :param params: body of the request.
        :param session: type of the request.
        :return: data in json format
        """
        if self.debug:
            print(f"started request for {connector} at: {time.time()}")
        async with session.get(url=f"{url}{connector}", params=params) as resp:
            if resp.status == 200:
                response = await resp.json()
                response = response['rows']
                if len(response) < take:
                    if self.debug:
                        print(f"request with params: {params} was the last request with {len(response)} rows")
                    self.got_all_results = True
                else:
                    if self.debug:
                        print(f"request with params: {params} has {len(response)} rows")
            else:
                print(f"request to AFAS failed with response: {resp.status, resp.text}")
                self.got_all_results = True
                response = resp.text

            return {connector: response}

    async def get_meta_data(self, connector: str = None):
        """
        This function makes sure that you can create a list of connector names without having to call another class.
        :return: returns a list of all connectors in the environment.
        """

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/metainfo{f'/get/{connector}' if connector is not None else ''}"
        authorization_header = {'Authorization': 'AfasToken ' + self.base64token}

        async with aiohttp.ClientSession(headers=authorization_header, timeout=aiohttp.ClientTimeout()) as session:
            async with session.get(url=f"{url}") as resp:
                if resp.status == 200:
                    response = await resp.json()
                    response = response[f"{'getConnectors' if connector is None else 'fields'}"]
                else:
                    print(f"request to AFAS failed with response: {resp.status}")
                    response = [resp.text]

                return response