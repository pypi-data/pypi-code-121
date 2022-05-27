import time
from datetime import datetime
from typing import List
from src.jobs.system_jobs import OnlineLogger
from src.api.entities.cliente import Cliente, Endereco
from src.database import utils, queries
import logging
import src.database.connection as database
from src.database.entities.client import Client
from src.entities.log import Log
import src.api.okvendas as api_okvendas
from src.database.utils import DatabaseConfig

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_send_clients(job_config: dict) -> None:
    """
    Job para enviar os clientes para api okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        db_config = utils.get_database_config(job_config)
        db_clients = get_clients(db_config, job_config.get('sql'))

        if len(db_clients) <= 0:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Nenhum cliente retornado para integracao no momento', 'warning', 'CLIENTE')
            return

        clients_inserted = insert_out_clients(db_config, db_clients)
        if not clients_inserted:
            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Nao foi possivel inserir os clientes no banco semaforo', 'error', 'CLIENTE')

        clients = [Cliente(
            nome=c.name,
            razao_social=c.company_name,
            sexo='M',
            data_nascimento=None,
            data_bloqueio=None,
            data_constituicao=None,
            cpf=c.cpf or "",
            cnpj=c.cnpj,
            endereco=Endereco(True, c.address_type, c.address, c.zipcode, c.number, c.complement, c.neighbourhood, c.city, c.state, c.residential_phone or c.mobile_phone, str(), c.reference, 'BR', str()),
            email=c.email,
            codigo_referencia=c.client_erp,
            telefone_residencial=c.residential_phone,
            telefone_celular=c.mobile_phone) for c in db_clients]

        total = len(clients)
        page = 10
        limit = 10 if total > 10 else total
        offset = 0

        partial_clients = clients[offset:limit]
        while limit <= total:
            results = api_okvendas.post_clients(partial_clients)
            if len(results) < 1:
                send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Falha ao integrar clientes: {results[0].message}', 'error', 'CLIENTE')

            sucessful_results = [result for result in results if result.status == 1]
            failed_results = [result for result in results if result.status > 1]

            if len(sucessful_results) > 0:
                protocol_clients(db_config, [c.codigo_referencia for sr in sucessful_results for c in clients if sr.identifiers[0].__contains__(c.cpf or c.cnpj)])

            if len(failed_results) > 0:
                for fr in failed_results:
                    for c in partial_clients:
                        if c.cpf or c.cnpj == fr.identifiers[0]:
                            time.sleep(0.3)
                            send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Falha ao integrar cliente cod.erp {c.codigo_referencia}: {fr.message}', 'error',
                                          'CLIENTE', c.codigo_referencia)

            limit = limit + page
            offset = offset + page
            partial_clients = clients[offset:limit]

    except Exception as e:
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'Erro nao esperado na integracao de clientes: {str(e)}', 'error', 'CLIENTE')


def get_clients(db_config: DatabaseConfig, sql: str) -> List[Client]:
    conn = database.Connection(db_config).get_conect()
    cursor = conn.cursor()

    cursor.execute(sql)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    conn.close()

    clients_list = []
    new: dict = {}
    for row in results:
        for i, c in enumerate(columns):
            new[c.lower()] = row[i]

        clients_list.append(new)

    clients = [Client(**c) for c in clients_list]
    return clients


def insert_out_clients(db_config: DatabaseConfig, clients: List[Client]) -> bool:
    conn = database.Connection(db_config).get_conect()
    cursor = conn.cursor()

    # cursor.executemany(queries.get_insert_out_clients(db_config.db_type), [queries.get_command_parameter(db_config.db_type, [c.client_erp, datetime.now(), datetime.now()]) for c in clients])
    for c in clients:
        cursor.execute(queries.get_insert_out_clients(db_config.db_type), queries.get_command_parameter(db_config.db_type, [c.client_erp, datetime.now(), datetime.now()]))

    result = cursor.rowcount

    cursor.close()
    conn.commit()
    conn.close()

    return result > 0


def protocol_clients(db_config: DatabaseConfig, client_erp_codes: List[str]) -> bool:
    conn = database.Connection(db_config).get_conect()
    cursor = conn.cursor()

    cursor.executemany(queries.get_out_client_protocol_command(db_config.db_type),
                       [queries.get_command_parameter(db_config.db_type, [c]) for c in client_erp_codes])
    result = cursor.rowcount

    cursor.close()
    conn.commit()
    conn.close()

    return result > 0
