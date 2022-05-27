import requests
import logging

logger = logging.getLogger()


def register_warn(message):
    logger.warning(message)
    post_message(message)


def register_error(erro):
    logger.error(erro)
    post_message(erro)


def post_message(message):
    dct_body = {
        'text': message,
        'channel': '#oking'
    }

    url = 'https://hooks.slack.com/services/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'

    try:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/html'
        }

        response = requests.post(url, json=dct_body, headers=headers)
        if not 200 <= response.status_code <= 299:
            msg = 'Erro ao enviar slack ' + str(response.status_code) + ' ' + str(dct_body)
            logger.error(msg)
    except Exception:
        logger.error('Erro ao enviar slack')
