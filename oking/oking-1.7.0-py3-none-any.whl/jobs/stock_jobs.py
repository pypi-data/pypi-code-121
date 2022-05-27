from datetime import datetime
import logging
import src.database.connection as database
import src.database.utils as utils
from src.jobs.system_jobs import OnlineLogger
from src.database.utils import DatabaseConfig
import src.api.okvendas as api_okvendas
from src.api import slack
from src.database import queries
import src
import time

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_insert_stock_semaphore(job_config_dict: dict):
    """
    Job para inserir estoques no banco semáforo
    Args:
        job_config_dict: Configuração do job
    """
    db_config = utils.get_database_config(job_config_dict)
    if db_config.sql is None:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, 'Comando sql para inserir estoques no semaforo nao encontrado', 'warning', 'ESTOQUE')
    else:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()

        try:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo estoques no banco semaforo \n {db_config.sql}', 'info', 'ESTOQUE')
            cursor.execute(db_config.sql)
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, '{cursor.rowcount} estoques inseridos no banco semaforo', 'info', 'ESTOQUE')
        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao inserir estoques no banco semaforo {str(ex)}', 'error', 'ESTOQUE')

        cursor.close()
        conn.commit()
        conn.close()


def job_send_stocks(job_config_dict: dict):
    """
    Job para realizar a atualização dos estoques padrão
    Args:
        job_config_dict: Configuração do job
    """
    db_config = utils.get_database_config(job_config_dict)
    stocks = query_stocks(job_config_dict, db_config)
    atualizados = []
    if len(stocks) or 0 > 0:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, 'Total de estoques a serem atualizados: {len(stocks)}', 'info', '')
        for stock in stocks:
            try:
                time.sleep(1)
                response, status_code = api_okvendas.send_stocks(src.client_data.get('url_api') + '/catalogo/estoque', stock, src.client_data.get('token_api'))

                if response is not None:
                    conexao = database.Connection(db_config)
                    conn = conexao.get_conect()
                    cursor = conn.cursor()

                    codigo_erp = response['codigo_erp']
                    if response['Status'] == 1 or response['Status'] == 'Success':
                        cursor.execute(queries.get_stock_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [codigo_erp]))
                        atualizados.append(response['codigo_erp'])
                    elif (response['Status'] == 'Error' or response['Status'] == 3) and response['Message'] == "Erro ao atualizar o estoque. Produto não existente":
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao atualizar estoque para o sku {codigo_erp}: {response["Message"]}', 'warning',
                                      'ESTOQUE', codigo_erp)
                        cursor.execute(queries.get_stock_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [codigo_erp]))
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao atualizar estoque para o sku {codigo_erp}: {response["Message"]}', 'warning',
                                      'ESTOQUE', codigo_erp)

                    cursor.close()
                    conn.commit()
                    conn.close()
            except Exception as e:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao atualizar estoque do sku {stock.get("codigo_erp")}: {str(e)}', 'error', 'ESTOQUE',
                              stock.get('codigo_erp'))

        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Atualizado estoques no semaforo: {len(atualizados) or 0}', 'info', 'ESTOQUE')
    else:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao ha produtos para atualizar estoque no momento', 'warning', 'ESTOQUE')


def job_send_stocks_ud(job_config_dict: dict):
    """
    Job para realizar a atualização dos estoques por unidade de distribuição
    Args:
        job_config_dict: Configuração do job
    """
    db_config = utils.get_database_config(job_config_dict)
    stocks = query_stocks_ud(job_config_dict, db_config)
    p_size = len(stocks) if stocks is not None else 0

    if p_size > 0:
        time.sleep(0.5)
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Total de produtos para atualizar estoque: {p_size}', 'info', 'ESTOQUE')
        count = 0
        for stock in stocks:
            codigo_erp = stock["codigo_erp"]
            try:
                response = api_okvendas.send_stocks_ud(src.client_data.get('url_api') + '/catalogo/estoqueUnidadeDistribuicao', [stock], src.client_data.get('token_api'))
                for res in response:
                    if res.status == 1:
                        protocol_stock(job_config_dict, db_config, codigo_erp)
                        count = count + 1
                    elif (res.status == 'Error' or res.status > 1) and res.message.__contains__("não encontrado"):
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao atualizar estoque {codigo_erp} erro da api: {res.message}', 'warning',
                                      'ESTOQUE')
                        protocol_stock(job_config_dict, db_config, codigo_erp)
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao atualizar estoque do sku {codigo_erp}: {res.message}', 'error', 'ESTOQUE',
                                      codigo_erp)
            except Exception as e:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao atualizar estoque para o sku {stock.get("codigo_erp")}: {str(e)}', 'error',
                              'ESTOQUE', stock.get('codigo_erp'))

        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produtos protocolados no semaforo: {count}', 'info', 'ESTOQUE')
    else:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao ha produtos para atualizar estoque', 'warning', 'ESTOQUE')


def query_stocks_ud(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta no banco de dados os estoques pendentes de atualização por unidade de distribuição
    Args:
        job_config_dict: Configuração do job
        db_config: Configuração do banco de dados

    Returns:
    Lista de estoques para realizar a atualização
    """
    stocks = None
    if db_config.sql is None:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Query estoque de produtos nao configurada', 'warning', 'ESTOQUE')
    else:
        try:
            conexao = database.Connection(db_config)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            # print(db_config.sql)
            cursor.execute(db_config.sql)
            rows = cursor.fetchall()
            # print(rows)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            if len(results) > 0:
                stocks = stock_ud_dict(results)

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{str(ex)}', 'error', 'ESTOQUE')

    return stocks


def query_stocks(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta no banco de dados os estoques pendentes de atualização padrão
    Args:
        job_config_dict: Configuração do job
        db_config: Configuração do banco de dados

    Returns:
    Lista de estoques para realizar a atualização
    """
    produtos = None
    if db_config.sql is None or db_config.sql == '':
        slack.register_warn("Query estoque de produtos nao configurada!")
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Query estoque de produtos nao configurada', 'warning', 'ESTOQUE')
    else:
        try:
            conexao = database.Connection(db_config)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            # print(db_config.sql)
            cursor.execute(db_config.sql)
            rows = cursor.fetchall()
            # print(rows)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            if len(results) > 0:
                produtos = stock_dict(results)

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{str(ex)}', 'error', 'ESTOQUE')

    return produtos


def stock_dict(produtos):
    lista = []
    for row in produtos:
        pdict = {
            'codigo_erp': str(row['CODIGO_ERP']),
            'quantidade': int(row['QUANTIDADE'])
        }
        lista.append(pdict)

    return lista


def stock_ud_dict(produtos):
    lista = []
    for row in produtos:
        pdict = {
            'unidade_distribuicao': row['CODIGO_UNIDADE_DISTRIBUICAO'],
            'codigo_erp': row['CODIGO_ERP'],
            'quantidade_total': int(row['QUANTIDADE']),
            'parceiro': 1
        }
        lista.append(pdict)

    return lista


def protocol_stock(job_config_dict, db_config: DatabaseConfig, codigo_erp):
    try:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Protocolando produto {codigo_erp} no semaforo', 'info', 'ESTOQUE')
        conn = database.Connection(db_config).get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.get_stock_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [codigo_erp]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao protocolar estoque do sku {codigo_erp}: {str(e)}', 'error', '')
