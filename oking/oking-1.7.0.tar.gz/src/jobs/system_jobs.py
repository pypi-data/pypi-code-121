from datetime import datetime
import logging
import src.api.okvendas as api_okvendas
from src.entities.log import Log
import src.api.slack as slack

logger = logging.getLogger()


class OnlineLogger:

    @staticmethod
    def send_log(job_name: str, send_slack: bool, send_api: bool, message: str, log_type: str, job_method: str = 'LOG_ONLINE', api_log_identifier: str = ''):
        if send_slack or bool(send_api):
            slack.post_message(f'{job_name} | {message}')

        if send_api:
            api_okvendas.post_log(Log(f'{job_name} | {message}', datetime.now().isoformat(), api_log_identifier, job_method))

        if log_type == 'info':
            logger.info(f'{job_name} | {message}')
        elif log_type == 'warning':
            logger.warning(f'{job_name} | {message}')
        elif log_type == 'error':
            logger.error(f'{job_name} | {message}')


def send_execution_notification(job_config: dict) -> None:
    logger.info(job_config.get('job_name') + ' | Notificando execucao api okvendas')
    api_okvendas.post_log(Log(f'Oking em execucao desde {job_config.get("execution_start_time")} com {job_config.get("job_qty")} jobs para o cliente {job_config.get("integration_id")}', datetime.now().isoformat(), '', 'NOTIFICACAO'))

# online_logger = OnlineLogger.send_log
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'warning', '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'info', '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'error', '')
#
#
