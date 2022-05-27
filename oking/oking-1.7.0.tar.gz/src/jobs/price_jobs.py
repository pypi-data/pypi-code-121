from datetime import datetime
import logging
import src.database.connection as database
import src.database.utils as utils
from src.database.utils import DatabaseConfig
import src.api.okvendas as api_okvendas
from src.entities.price import Price
from src.entities.response import PriceResponse
from src.database import queries
import src
import time
from src.entities.log import Log
from typing import List
from src.jobs.system_jobs import OnlineLogger

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_insert_prices_semaphore(job_config_dict: dict):
    """
    Job para preços no banco semáforo
    Args:
        job_config_dict: Configuração do job
    """
    db_config = utils.get_database_config(job_config_dict)
    if db_config.sql is None:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir precos no semaforo nao encontrado', 'warning', 'PRECO')
    else:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()

        try:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo precos no banco semaforo', 'info', 'PRECO')
            logger.info(db_config.sql)
            cursor.execute(db_config.sql)
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{cursor.rowcount} precos inseridos no banco semaforo', 'info', 'PRECO')
        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro {str(ex)}', 'error', 'PRECO')

        cursor.close()
        conn.commit()
        conn.close()


def job_send_prices(job_config_dict: dict):
    """
    Job para realizar a atualização de preços
    Args:
        job_config_dict: Configuração do job
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir precos no semaforo nao encontrado', 'warning', 'PRECO')
        else:
            prices = query_prices(job_config_dict, db_config)
            if prices is not None and len(prices) > 0:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produtos para atualizar preco {len(prices)}', 'info', 'PRECO')

                for price in prices:
                    try:
                        time.sleep(1)
                        response = api_okvendas.post_prices(src.client_data.get('url_api') + '/catalogo/preco', price, src.client_data.get('token_api'))
                        if response.status == 1 or response.status == "Success":
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Protocolando preço do sku {price.codigo_erp}', 'info', 'PRECO')
                            protocol_price(db_config, price)
                        elif (response.status == 'Error' or response.status > 1) and response.message == "Erro ao atualizar o preço. Produto não existente":
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                          f'Nao foi possivel atualizar o preco do sku {price.codigo_erp}. Erro recebido da Api: {response.message}', 'warning', 'PRECO')
                            protocol_price(db_config, price)
                        else:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                          f'Nao foi possivel atualizar o preco do sku {price.codigo_erp}. Erro recebido da Api: {response.message}', 'warning', 'PRECO', price.codigo_erp)
                    except Exception as e:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Falha ao atualizar preco do sku {price.codigo_erp}: {str(e)}', 'warning', 'PRECO', price.codigo_erp)
            else:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao existem precos a serem enviados no momento', 'warning', 'PRECO')
    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro durante execucao do job: {str(e)}', 'error', 'PRECO')


def query_prices(job_config_dict: dict, db_config: DatabaseConfig) -> List[Price]:
    """
    Consulta os precos para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de preços para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            prices = [Price(**p) for p in results]
            return prices

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f' Erro ao consultar precos no banco semaforo: {str(ex)}', 'error', 'PRECO')

    return []


def protocol_price(db_config: DatabaseConfig, price: Price) -> None:
    """
    Protocola os preços no banco semáforo
    Args:
        db_config: Configuração do banco de dados
        price: Lista de skus para protocolar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    sql = queries.get_price_protocol_command(db_config.db_type)
    try:
        cursor.execute(sql, queries.get_command_parameter(db_config.db_type, [price.codigo_erp, price.preco_atual]))
    except Exception as e:
        raise Exception(f'Erro ao protocolar preco do sku no banco semaforo {price.codigo_erp}: {str(e)}')

    cursor.close()
    conn.commit()
    conn.close()
