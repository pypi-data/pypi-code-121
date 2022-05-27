
# Queries nao podem terminar com ponto e virgula

def get_product_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.produto set data_sincronizacao = now() where codigo_erp = %s and codigo_erp_sku = %s'
	elif connection_type.lower() == 'oracle':
		return 'update openk_semaforo.produto set data_sincronizacao = SYSDATE where codigo_erp = :codigo_erp and codigo_erp_sku = :codigo_erp_sku'
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.produto set data_sincronizacao = getdate() where codigo_erp = ? and codigo_erp_sku = ?'


def get_stock_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.estoque_produto set data_sincronizacao = now() where codigo_erp = %s'
	elif connection_type.lower() == 'oracle':
		return 'update openk_semaforo.estoque_produto set data_sincronizacao = SYSDATE where codigo_erp = :codigo_erp'
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.estoque_produto set data_sincronizacao = getdate() where codigo_erp = ?'


def get_price_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.preco_produto set data_sincronizacao = now() where codigo_erp = %s and preco_atual = %s'
	elif connection_type.lower() == 'oracle':
		return 'update openk_semaforo.preco_produto set data_sincronizacao = SYSDATE where codigo_erp = :1 and preco_atual = :2'
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.preco_produto set data_sincronizacao = getdate() where codigo_erp = ? and preco_atual = ?'


def get_insert_client_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, 
														TIPO_LOGRADOURO, LOGRADOURO,NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, REFERENCIA, DIRECAO) 
				VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17) '''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, 
														tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia, direcao)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_order_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.PEDIDO (PEDIDO_ID, PEDIDO_VENDA_ID, DATA_PEDIDO, STATUS, CLIENTE_ID, VALOR, VALOR_DESCONTO, VALOR_FRETE, 
					VALOR_ADICIONAL, DATA_PAGAMENTO, TIPO_PAGAMENTO, BANDEIRA, PARCELAS, CONDICAO_PAGAMENTO_ERP, CODIGO_RASTREIO, DATA_PREVISAO_ENTREGA, 
					TRANSPORTADORA, MODO_ENVIO, CANAL_ID)
					VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, TO_DATE(:10, 'YYYY-MM-DD HH24:MI:SS'), :11, :12, :13, :14, :15, TO_DATE(:16, 'YYYY-MM-DD HH24:MI:SS'), :17, :18, :19) '''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_order_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, representante_erp)
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.PEDIDO (PEDIDO_ID, PEDIDO_VENDA_ID, DATA_PEDIDO, STATUS, CLIENTE_ID, VALOR, VALOR_DESCONTO, VALOR_FRETE, 
					VALOR_ADICIONAL, DATA_PAGAMENTO, TIPO_PAGAMENTO, BANDEIRA, PARCELAS, CONDICAO_PAGAMENTO_ERP, CODIGO_RASTREIO, DATA_PREVISAO_ENTREGA, 
					TRANSPORTADORA, MODO_ENVIO, CANAL_ID, REPRESENTANTE_ERP)
					VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, TO_DATE(:10, 'YYYY-MM-DD HH24:MI:SS'), :11, :12, :13, :14, :15, TO_DATE(:16, 'YYYY-MM-DD HH24:MI:SS'), :17, :18, :19, :20) '''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.pedido (pedido_id, pedido_venda_id, data_pedido, status, cliente_id, valor, valor_desconto, valor_frete, 
					valor_adicional, data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, codigo_rastreio, data_previsao_entrega, 
					transportadora, modo_envio, canal_id, representante_erp)
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_order_items_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (%s, %s, %s, %s, %s, %s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE)
					VALUES (:1, :2, :3, :4, :5, :6, :7, :8)'''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete) 
					values (?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_order_items_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, cnpj_filial_venda, codigo_filial_erp, codigo_filial_expedicao_erp, codigo_filial_faturamento_erp) 
					values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE, CNPJ_FILIAL_VENDA, CODIGO_FILIAL_ERP, CODIGO_FILIAL_EXPEDICAO_ERP, CODIGO_FILIAL_FATURAMENTO_ERP)
					VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)'''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.itens_pedido (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, cnpj_filial_venda, codigo_filial_erp, codigo_filial_expedicao_erp, codigo_filial_faturamento_erp) 
					values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_query_client_id(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'select id from openk_semaforo.cliente where email = %s'
	elif connection_type.lower() == 'oracle':
		return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE EMAIL = :email'
	elif connection_type.lower() == 'sql':
		return 'select id from openk_semaforo.cliente where email = ?'


def get_query_client_erp(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'select id from openk_semaforo.cliente where cliente_erp = %s'
	elif connection_type.lower() == 'oracle':
		return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CLIENTE_ERP = :cliente_erp '
	elif connection_type.lower() == 'sql':
		return 'select id from openk_semaforo.cliente where client_erp = ?'


def get_insert_out_clients(connection_type: str) -> str:
	if connection_type.lower() == 'mysql':
		return '''insert into openk_semaforo.cliente (cliente_erp, data_alteracao, data_sincronizacao)
					values (%s, %s, %s) '''
	elif connection_type.lower() == 'oracle':
		return '''INSERT INTO OPENK_SEMAFORO.CLIENTE (CLIENTE_ERP, DATA_ALTERACAO, DATA_SINCRONIZACAO)
					VALUES (:1, :2, :3)'''
	elif connection_type.lower() == 'sql':
		return '''insert into openk_semaforo.cliente (cliente_erp, data_alteracao, data_sincronizacao)
					values (?, ?, ?) '''

def get_update_client_sql(connection_type: str):
	if connection_type.lower() == 'mysql':
		return '''update openk_semaforo.cliente
					SET nome = %s
					  , razao_social = %s
					  , cpf = %s
					  , cnpj = %s
					  , email = %s
					  , telefone_residencial = %s
					  , telefone_celular = %s
					  , cep = %s
					  , tipo_logradouro = %s
					  , logradouro = %s
					  , numero = %s
					  , complemento = %s
					  , bairro = %s
					  , cidade = %s
					  , estado = %s
					  , referencia = %s
					WHERE cliente_erp = %s '''
	elif connection_type.lower() == 'oracle':
		return '''UPDATE OPENK_SEMAFORO.CLIENTE
					SET NOME = :1
					  , RAZAO_SOCIAL = :2
					  , CPF = :3
					  , CNPJ = :4
					  , EMAIL = :5
					  , TELEFONE_RESIDENCIAL = :6
					  , TELEFONE_CELULAR = :7
					  , CEP = :8
					  , TIPO_LOGRADOURO = :9
					  , LOGRADOURO = :10
					  , NUMERO = :11
					  , COMPLEMENTO = :12
					  , BAIRRO = :13
					  , CIDADE = :14
					  , ESTADO = :15
					  , REFERENCIA = :16
					WHERE CLIENTE_ERP = :17 '''
	elif connection_type.lower() == 'sql':
		return '''update openk_semaforo.cliente
							SET nome = ?
							  , razao_social = ?
							  , cpf = ?
							  , cnpj = ?
							  , email = ?
							  , telefone_residencial = ?
							  , telefone_celular = ?
							  , cep = ?
							  , tipo_logradouro = ?
							  , logradouro = ?
							  , numero = ?
							  , complemento = ?
							  , bairro = ?
							  , cidade = ?
							  , estado = ?
							  , referencia = ?
							WHERE cliente_erp = ? '''


def get_query_non_integrated_order(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'select id from openk_semaforo.pedido where pedido_id = %s and data_sincronizacao is null'
	elif connection_type.lower() == 'oracle':
		return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id AND DATA_SINCRONIZACAO IS NULL'
	elif connection_type.lower() == 'sql':
		return 'select id from openk_semaforo.pedido where pedido_id = ? and data_sincronizacao is null'


def get_query_order(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'select id from openk_semaforo.pedido where pedido_id = %s'
	elif connection_type.lower() == 'oracle':
		return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :order_id'
	elif connection_type.lower() == 'sql':
		return 'select id from openk_semaforo.pedido where pedido_id = ?'


def get_command_parameter(connection_type: str, parameters: list):
	if connection_type.lower() == 'mysql':
		return tuple(parameters)
	elif connection_type.lower() == 'oracle':
		return parameters
	elif connection_type.lower() == 'sql':
		return parameters


def get_order_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.pedido set data_sincronizacao = now(), codigo_referencia = %s where pedido_id = %s'
	elif connection_type.lower() == 'oracle':
		return 'UPDATE OPENK_SEMAFORO.PEDIDO SET DATA_SINCRONIZACAO = SYSDATE, CODIGO_REFERENCIA = :order_erp_id WHERE PEDIDO_ID = :order_id'
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.pedido set data_sincronizacao = getdate(), codigo_referencia = ? where pedido_id = ?'


def get_client_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.cliente set cliente_erp = %s where id = (select cliente_id from openk_semaforo.pedido where pedido_id = %s)'
	elif connection_type.lower() == 'oracle':
		return '''UPDATE OPENK_SEMAFORO.CLIENTE C
				SET CLIENTE_ERP = :1 
				WHERE ID = (SELECT CLIENTE_ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_ID = :2)'''
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.cliente set cliente_erp = ? where id = (select cliente_id from openk_semaforo.pedido where pedido_id = ?)'


def get_out_client_protocol_command(connection_type: str):
	if connection_type.lower() == 'mysql':
		return 'update openk_semaforo.cliente set data_sincronizacao = now() where client_erp = %s'
	elif connection_type.lower() == 'oracle':
		return 'UPDATE OPENK_SEMAFORO.CLIENTE C SET DATA_SINCRONIZACAO = SYSDATE WHERE CLIENTE_ERP = :1 '
	elif connection_type.lower() == 'sql':
		return 'update openk_semaforo.cliente set data_sincronizacao = now() where client_erp = ? '
