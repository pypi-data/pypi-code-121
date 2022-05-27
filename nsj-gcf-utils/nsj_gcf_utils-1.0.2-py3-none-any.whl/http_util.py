import json
import urllib

import requests
import time

from nsj_gcf_utils.app_logger import logger
from typing import Dict, Any


class HttpUtilGetException(Exception):
    pass


class HttpUtilPostException(Exception):
    pass

class HttpUtilPutException(Exception):
    pass

class HttpUtilDeleteException(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class HttpUtil:
    @staticmethod
    def post_retry(url: str, data: str, headers: Dict[str, str] = None, timeout: int = 20, tries: int = 3, interval: int = 3, format_data: bool = True, raise_for_status: bool = True, resouce_description: str = '', verify :bool = True, query_params: Dict[str, Any] = None):
        # Encoding query params
        if query_params is not None:
            q_params = urllib.parse.urlencode(query_params, doseq=True)

            if '?' in url:
                url += '&' + q_params
            else:
                url += '?' + q_params
                
        logger.info(f'Post URL: {url}')
        
        # Formatting data
        if format_data:
            if isinstance(data, dict) or isinstance(data, list):
                logger.info(
                    'Converting data from "dict" or "list" to json string')
                data = json.dumps(data)

                # adding content-type: application/json in headers
                if headers:
                    if not ('content-type' in [k.lower() for k in headers.keys()]):
                        headers['content-type'] = 'application/json'
                else:
                    headers = {'content-type': 'application/json'}
            elif not isinstance(data, str):
                logger.info('Converting data from non string to string')
                data = str(data)

        logger.info(f'Posting data (bellow) to URL: {url}')
        if not('password' in data) and not('client_secret' in data) and not('pass' in data):
            logger.info(f'Sending data: {data}')

        # Making tries
        exception_obj = None
        resp = None
        for i in range(tries):
            resp = None
            try:
                resp = requests.post(
                    url=url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    verify=verify
                )

                if resp.status_code >= 200 and resp.status_code < 400:
                    return resp
                else:
                    logger.warning(
                        f'HTTP POST FAIL - URL: {url} - STATUS CODE {resp.status_code} - CONTENT {resp.text}')
            except Exception as e:
                logger.warning(
                    f'HTTP POST FAIL - URL: {url} - EXCEPTION {e}')
                exception_obj = e

            time.sleep(interval)
            logger.warning('Retring HTTP POST')

        # If there was no success
        if resp:
            # Checking response status
            if raise_for_status:
                if resp.status_code == 404:
                    raise ResourceNotFound(
                        f'{resouce_description} - {resp.text}')
                resp.raise_for_status()

            return resp
            # raise Exception(
            #     f'Error posting data. Status code: {resp.status_code}. Content: {resp.text}')
        else:
            raise HttpUtilPostException(
                f'Error posting data.\nMessage {exception_obj}')

    @staticmethod
    def get_retry(url: str, headers: Dict[str, str] = None, timeout: int = 20, tries: int = 3, interval: int = 3, raise_for_status: bool = True, resouce_description: str = '', data: str = None, verify :bool = True, query_params: Dict[str, Any] = None):
        logger.info(f'Get URL: {url}')
        
        # Encoding query params
        if query_params is not None:
            q_params = urllib.parse.urlencode(query_params, doseq=True)

            if '?' in url:
                url += '&' + q_params
            else:
                url += '?' + q_params
                
        logger.info(f'Get URL: {url}')

        # Making tries
        exception_obj = None
        resp = None
        for i in range(tries):
            resp = None
            try:
                resp = requests.get(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    data=data,
                    verify=verify
                )

                if resp.status_code >= 200 and resp.status_code < 400:
                    return resp
                else:
                    logger.warning(
                        f'HTTP GET FAIL - URL: {url} - STATUS CODE {resp.status_code} - CONTENT {resp.text}')
            except Exception as e:
                logger.warning(
                    f'HTTP GET FAIL - URL: {url} - EXCEPTION {e}')
                exception_obj = e

            time.sleep(interval)
            logger.warning('Retring HTTP GET')

        # If there was no success
        if resp:
            # Checking response status
            if raise_for_status:
                if resp.status_code == 404:
                    raise ResourceNotFound(
                        f'{resouce_description} - {resp.text}')
                resp.raise_for_status()

            return resp
            # raise Exception(
            #     f'Error getting data. Status code: {resp.status_code}. Content: {resp.text}')
        else:
            raise HttpUtilGetException(
                f'Error getting data.\nMessage {exception_obj}')

    @staticmethod
    def put_retry(url: str, data: str, headers: Dict[str, str] = None, timeout: int = 20, tries: int = 3,
                   interval: int = 3, format_data: bool = True, raise_for_status: bool = True,
                   resouce_description: str = '', verify :bool = True):
        # Formatting data
        if format_data:
            if isinstance(data, dict) or isinstance(data, list):
                logger.info(
                    'Converting data from "dict" or "list" to json string')
                data = json.dumps(data)

                # adding content-type: application/json in headers
                if headers:
                    if not ('content-type' in [k.lower() for k in headers.keys()]):
                        headers['content-type'] = 'application/json'
                else:
                    headers = {'content-type': 'application/json'}
            elif not isinstance(data, str):
                logger.info('Converting data from non string to string')
                data = str(data)

        logger.info(f'Puting data (bellow) to URL: {url}')
        if not ('password' in data) and not ('client_secret' in data) and not ('pass' in data):
            logger.info(f'Sending data: {data}')

        # Making tries
        exception_obj = None
        resp = None
        for i in range(tries):
            resp = None
            try:
                resp = requests.put(
                    url=url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    verify=verify
                )

                if resp.status_code >= 200 and resp.status_code < 400:
                    return resp
                else:
                    logger.warning(
                        f'HTTP PUT FAIL - URL: {url} - STATUS CODE {resp.status_code} - CONTENT {resp.text}')
            except Exception as e:
                logger.warning(
                    f'HTTP PUT FAIL - URL: {url} - EXCEPTION {e}')
                exception_obj = e

            time.sleep(interval)
            logger.warning('Retring HTTP PUT')

        # If there was no success
        if resp:
            # Checking response status
            if raise_for_status:
                if resp.status_code == 404:
                    raise ResourceNotFound(
                        f'{resouce_description} - {resp.text}')
                resp.raise_for_status()

            return resp
        else:
            raise HttpUtilPutException(
                f'Error puting data.\nMessage {exception_obj}')

    @staticmethod
    def delete_retry(url: str, headers: Dict[str, str] = None, timeout: int = 20, tries: int = 3,
                   interval: int = 3, format_data: bool = True, raise_for_status: bool = True,
                   resouce_description: str = '', verify :bool = True):



        # Making tries
        exception_obj = None
        resp = None
        for i in range(tries):
            resp = None
            try:
                resp = requests.delete(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    verify=verify
                )

                if resp.status_code >= 200 and resp.status_code < 400:
                    return resp
                else:
                    logger.warning(
                        f'HTTP DELETE FAIL - URL: {url} - STATUS CODE {resp.status_code} - CONTENT {resp.text}')
            except Exception as e:
                logger.warning(
                    f'HTTP DELETE FAIL - URL: {url} - EXCEPTION {e}')
                exception_obj = e

            time.sleep(interval)
            logger.warning('Retring HTTP DELETE')

        # If there was no success
        if resp:
            # Checking response status
            if raise_for_status:
                if resp.status_code == 404:
                    raise ResourceNotFound(
                        f'{resouce_description} - {resp.text}')
                resp.raise_for_status()

            return resp
        else:
            raise HttpUtilDeleteException(
                f'Error deleting data.\nMessage {exception_obj}')