from datetime import datetime
import logging
from src.entities.log import Log
import src.database.connection as database
from src.database import queries
from src.database.utils import DatabaseConfig
import src.database.utils as utils
from src.entities.product import Product
from src.entities.photos_sku import PhotosSku
import src.api.okvendas as api_okvendas
from src.jobs.system_jobs import OnlineLogger

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_update_products_semaphore(job_config_dict: dict):
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para criar produtos nao encontrado', 'warning', 'PRODUTO')
            return

        db = database.Connection(db_config)
        connection = db.get_conect()
        cursor = connection.cursor()

        cursor.execute(db_config.sql)
        cursor.close()

        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produtos marcados para atualizar no banco semaforo: {cursor.rowcount}', 'info', 'PRODUTO')
        connection.commit()
        connection.close()

    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao atualizar produtos no banco semaforo: {str(e)}', 'error', 'PRODUTO')


def job_insert_products_semaphore(job_config_dict: dict):
    """
    Job que realiza a insercao dos produtos no banco semaforo
    Args:
        job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para inserir produtos no semaforo nao encontrado', 'warning', 'PRODUTO')
            return

        # abre a connection com o banco
        db = database.Connection(db_config)
        connection = db.get_conect()
        cursor = connection.cursor()

        try:
            # sql: str = db_config.sql
            # if db_config.sql[len(db_config.sql) - 1] is ';':
            #     sql = db_config.sql[len(db_config.sql) - 1] = ' '

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Inserindo produtos no banco semáforo', 'info', 'PRODUTO')
            cursor.execute(db_config.sql)
            connection.commit()
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'{cursor.rowcount} produtos inseridos no banco semáforo', 'info', 'PRODUTO')
        except Exception as e:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao inserir produtos no banco semaforo: {str(e)}', 'error', 'PRODUTO')
            cursor.close()
            connection.close()

        cursor.close()
        connection.close()
    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True, f'Erro ao durante a execucao do job: {str(e)}', 'error', 'PRODUTO')


def job_send_products(job_config_dict: dict):
    """
    Job que realiza a leitura dos produtos contidos no banco semaforo e envia para a api okvendas
    Args:
        job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Comando sql para criar produtos nao encontrado', 'warning', 'PRODUTO')
            return

        produtos_repetidos = query_products(db_config)

        keys_photos_sent = {}
        photos_sku = mount_list_photos(produtos_repetidos)
        produtos = remove_repeat_products(produtos_repetidos)

        if len(produtos) <= 0:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Nao existem produtos para criar no momento', 'warning', 'PRODUTO')
            return

        for prod in produtos:
            try:
                response = api_okvendas.post_produtos([prod])

                for res in response:
                    if res.status > 1:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                      f'Erro ao gerar produto {res.codigo_erp} na api okvendas. Erro gerado na api: {res.message}', 'warning', 'PRODUTO')
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Produto {res.codigo_erp} criado com sucesso', 'info', 'PRODUTO')
                        protocol_products(job_config_dict, produtos, db_config)

                        keys_photos_sent[(prod.codigo_erp, prod.preco_estoque[0].codigo_erp_atributo)] = ""

            except Exception as e:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro durante o envio de produtos: {str(e)}', 'error', 'PRODUTO')

        if send_photos_products(photos_sku, keys_photos_sent, 50):
            logger.info(job_config_dict.get('job_name') + f' | Fotos dos produtos cadastradas com sucesso')
        else:
            print(" Erro ao cadastrar as fotos do produto")
            logger.error(job_config_dict.get('job_name') + f' | Erro durante o cadastro das fotos dos produtos')

    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro durante a execucao do job: {str(e)}', 'error', 'PRODUTO')


def query_products(db_config: DatabaseConfig):
    """
    Consulta os produtos contidos no banco semaforo juntamente com os dados do banco do ERP
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de produtos
    """
    # abre a connection com o banco
    db = database.Connection(db_config)
    connection = db.get_conect()
    # connection.start_transaction()
    cursor = connection.cursor()

    # obtem os dados do banco
    # logger.warning(query)
    cursor.execute(db_config.sql)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()

    produtos = []
    for result in results:
        produtos.append(Product(result))

    return produtos


def protocol_products(job_config_dict: dict, products: list, db_config: DatabaseConfig) -> None:
    """
    Protocola no banco semaforo os produtos que foram enviados para a api okvendas
    Args:
        job_config_dict: Configuração do job
        products: Lista de produtos enviados para a api okvendas
        db_config: Configuracao do banco de dados
    """
    try:
        if len(products) > 0:
            db = database.Connection(db_config)
            connection = db.get_conect()
            cursor = connection.cursor()
            for prod in products:
                try:
                    dados_produto = [prod.codigo_erp, prod.preco_estoque[0].codigo_erp_atributo]
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Protocolando codigo_erp {dados_produto[0]} sku {dados_produto[1]}', 'info', 'PRODUTO')
                    cursor.execute(queries.get_product_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, dados_produto))
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Linhas afetadas {cursor.rowcount}', 'info', 'PRODUTO')
                except Exception as e:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False, f'Erro ao protocolar sku {prod["codigo_erp_sku"]}: {str(e)}', 'error', 'PRODUTO')
            cursor.close()
            connection.commit()
            connection.close()
    except Exception as e:
        raise e


def mount_list_photos(products: list[Product]):
    photos = {}

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in photos:

            length_photos = len(photos[key])

            if contains_photo(photos[key], product.imagem_base64):
                continue
            else:
                order_photo = length_photos + 1
                photo_sku = PhotosSku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{order_photo}', order_photo,
                                      False)
                photos[key].append(photo_sku)

        else:
            # Mount photo
            photo_sku = PhotosSku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{1}', 1,
                                  True)

            photos[key] = [photo_sku]

    return photos


def remove_repeat_products(products: list[Product]):
    product_keys = {}
    result_products = []

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in product_keys:
            continue
        else:
            product_keys[key] = ""
            result_products.append(product)

    return result_products


def send_photos_products(photos_sku: dict, keys_photos_sent: dict, limit_photos_sent: int):
    count_success = 0
    list_photos = []
    for photo_key in photos_sku:

        if photo_key in keys_photos_sent:
            list_photo = photos_sku[photo_key]

            for photo in list_photo:
                if (len(list_photos) + 1) <= limit_photos_sent:
                    list_photos.append(photo)

                if len(list_photos) == limit_photos_sent:
                    success = api_okvendas.put_photos_sku(list_photos)
                    if not success:
                        return success
                    else:
                        count_success = count_success + 1
                        list_photos = []

    if 0 < len(list_photos) <= 50:
        return api_okvendas.put_photos_sku(list_photos)

    return count_success > 0 if True else False


def contains_photo(photos: list[PhotosSku], imagem_base64: str):
    for photo in photos:
        if photo.base64_foto == imagem_base64:
            return True
    return False
