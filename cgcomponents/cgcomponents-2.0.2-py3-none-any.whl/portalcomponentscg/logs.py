import logging

import const
from requests_cg import post_cg

logging.basicConfig(filename='logsPortal.log', level=logging.INFO,
                    format='%(levelname)s - %(message)s')


def LogsMicroService(mc):
    json = {'microservice': mc}

    logging.info(mc)

    post_cg(const.URL_API_MICROSERVICE, json)


def LogsInfo(messages):

    json = {
        "info_message": [
            {
                "messages": messages
            }
        ]
    }
    post_cg(const.URL_API_INFOS, json)

    logging.info(messages)
    pass


def LogsErros(erros: []):

    logging.error(erros)


def LogsCriticalErros(critical: []):

    logging.warning(critical)

