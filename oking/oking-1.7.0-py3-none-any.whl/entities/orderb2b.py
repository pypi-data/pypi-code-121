from typing import List, Dict


class FormaEnvioParceiro:
    tracking_code: str
    tracking_type: str
    shipping_type: str
    shipping_status: str
    post_forecast: str
    shipping_mode: str
    plp: str
    route: str
    mega_route: str

    def __init__(self, codigo_rastreio: str, forma_envio: str, tipo_envio: str, status_envio: str, data_previsao_postagem: str, modo_envio: str, plp: str, rota: str, mega_rota: str) -> None:
        self.tracking_code = codigo_rastreio
        self.tracking_type = forma_envio
        self.shipping_type = tipo_envio
        self.shipping_status = status_envio
        self.post_forecast = data_previsao_postagem
        self.shipping_mode = modo_envio
        self.plp = plp
        self.route = rota
        self.mega_route = mega_rota


class FormaPagamentoParceiro:
    payment_type: str
    flag: str
    authorization_code: str
    status_code: str
    transaction_code: str
    created_date: str
    approved_date: str
    status_detail: str
    status: str
    freight_value: int
    installment_value: int
    order_amount: int
    total_paid_amount: int
    installments: int

    def __init__(self, tipo_pagamento: str, bandeira: str, codigo_autorizacao: str, codigo_status: str, codigo_transacao: str, data_criacao: str, data_aprovacao: str, detalhe_status: str,
                 status: str, valor_frete: int, valor_parcela: int, valor_pedido: int, valor_total_pago: int, parcelas: int) -> None:
        self.payment_type = tipo_pagamento
        self.flag = bandeira
        self.authorization_code = codigo_autorizacao
        self.status_code = codigo_status
        self.transaction_code = codigo_transacao
        self.created_date = data_criacao
        self.approved_date = data_aprovacao
        self.status_detail = detalhe_status
        self.status = status
        self.freight_value = valor_frete
        self.installment_value = valor_parcela
        self.order_amount = valor_pedido
        self.total_paid_amount = valor_total_pago
        self.installments = parcelas


class Item:
    main_sku: str
    variation_sku: str
    reference_sku: str
    variation_hierarchy: str
    is_restock: bool
    restock_erp_code: str
    ean: str
    quantity: int
    amount: int
    discount_amount: int
    height: int
    length: int
    width: int
    weight: int
    volume: int
    expedition_branch: str
    invoice_branch: str
    selling_branch_cnpj: str
    branch_erp_code: str
    branch: str

    def __init__(self, sku_principal: str, sku_variacao: str, sku_reference: str, hierarquia_variacao: str, is_restock: bool, codigo_externo_restock: str, ean: str, quantidade: int, value: int,
                 valor_desconto: int, altura: int, comprimento: int, largura: int, peso: int, volume: int, filial_expedicao: str, filial_faturamento: str, cnpj_filial_venda: str,
                 codigo_externo_filial: str, filial: str) -> None:
        self.main_sku = sku_principal
        self.erp_code = sku_variacao
        self.sku = sku_reference
        self.variation_hierarchy = hierarquia_variacao
        self.is_restock = is_restock
        self.restock_erp_code = codigo_externo_restock
        self.ean = ean
        self.quantity = quantidade
        self.value = value
        self.discount = valor_desconto
        self.height = altura
        self.length = comprimento
        self.width = largura
        self.weight = peso
        self.volume = volume
        self.expedition_branch = filial_expedicao
        self.invoice_branch = filial_faturamento
        self.selling_branch_cnpj = cnpj_filial_venda
        self.branch_erp_code = codigo_externo_filial
        self.branch = filial


class ItensBrinde:
    price: int
    quantity: int
    discount: int
    product_id: str
    erp_code: str
    product_identifier: str
    reference_code: str
    name: str
    unity: str
    attribute_identifier: str
    attribute_option_identifier: str
    expedition_branch: str
    invoice_branch: str

    def __init__(self, preco_atual: int, quantidade: int, desconto: int, produto_id: str, codigo_externo: str, identificador_produto: str, codigo_referencia: str, nome_produto: str,
                 unidade_produto: str, identificador_atributo: str, identificador_opcao_atributo: str, filial_expedicao: str, filial_faturamento: str) -> None:
        self.price = preco_atual
        self.quantity = quantidade
        self.discount = desconto
        self.product_id = produto_id
        self.erp_code = codigo_externo
        self.product_identifier = identificador_produto
        self.reference_code = codigo_referencia
        self.name = nome_produto
        self.unity = unidade_produto
        self.attribute_identifier = identificador_atributo
        self.attribute_option_identifier = identificador_opcao_atributo
        self.expedition_branch = filial_expedicao
        self.invoice_branch = filial_faturamento


class ItensPersonalizado:
    id: str
    net_price: int
    gross_price: int
    text: str

    def __init__(self, id: str, preco_liquido: int, preco_bruto: int, texto: str) -> None:
        self.id = id
        self.net_price = preco_liquido
        self.gross_price = preco_bruto
        self.text = texto


class Titulo:
    installment: int
    amount: int
    expiration_date: str
    discharge_date: str
    paid_date: str
    return_code: str
    return_description: str
    designed_rebate_amount: int
    designed_discount: int
    iof_collected_amount: int
    credited_amount: int
    withdrawn_amount: int
    other_amount: int
    other_credits: int

    def __init__(self, parcela: int, valor: int, data_vencimento: str, data_baixa: str, data_pago: str, codigo_retorno: str, descricao_retorno: str, valor_abatimento_concebido: int,
                 desconto_concebido: int, valor_iof_recolhido: int, valor_creditado: int, valor_sacado: int, outros_valores: int, outros_creditos: int) -> None:
        self.installment = parcela
        self.amount = valor
        self.expiration_date = data_vencimento
        self.discharge_date = data_baixa
        self.paid_date = data_pago
        self.return_code = codigo_retorno
        self.return_description = descricao_retorno
        self.designed_rebate_amount = valor_abatimento_concebido
        self.designed_discount = desconto_concebido
        self.iof_collected_amount = valor_iof_recolhido
        self.credited_amount = valor_creditado
        self.withdrawn_amount = valor_sacado
        self.other_amount = outros_valores
        self.other_credits = outros_creditos


class Pagamento:
    payment_option: str
    installments: int
    flag: str
    rsvarejo_finance_table: str
    rsvarejo_sale_type: str
    channel_id: str
    channel: str
    coupom_number: str
    coupom_amount: int
    purchase_code: str
    channel_order_code: str
    movement_date: str
    market_code: str
    bonds: List[Titulo]
    erp_payment_condition: str

    def __init__(self, opcao_pagamento: str, parcelas: int, bandeira: str, tabela_financiamento_rsvarejo: str, tipo_venda_rsvarejo: str, canal_venda_id: str, canal_venda: str, numero_cupom: str,
                 valor_cupom: int, codigo_compra: str, codigo_pedido_canal: str, data_movimento: str, codigo_mercado: str, titulos: List[Dict], condicao_pagamento_erp: str) -> None:
        self.payment_option = opcao_pagamento
        self.installments = parcelas
        self.flag = bandeira
        self.rsvarejo_finance_table = tabela_financiamento_rsvarejo
        self.rsvarejo_sale_type = tipo_venda_rsvarejo
        self.channel_id = canal_venda_id
        self.channel = canal_venda
        self.coupom_number = numero_cupom
        self.coupom_amount = valor_cupom
        self.purchase_code = codigo_compra
        self.channel_order_code = codigo_pedido_canal
        self.movement_date = data_movimento
        self.market_code = codigo_mercado
        self.bonds = [Titulo(**t) for t in titulos]
        self.erp_payment_condition = condicao_pagamento_erp


class PedidoNotaFiscal:
    invoice_id: int
    oder_id: int
    tax_number: str
    series_number: str
    access_key: str
    total_amount: int
    emission_date: str
    register_date: str
    xml: str
    link_danfe: str
    link_xml: str
    volume_quantity: str

    def __init__(self, nota_fiscal_id: int, pedido_id: int, num_fiscal: str, num_serie: str, access_key: str, valor_total_nota: int, data_emissao: str, dt_cadastro: str, xml: str,
                 link_danfe: str, link_xml: str, quantidade_volume: str) -> None:
        self.invoice_id = nota_fiscal_id
        self.oder_id = pedido_id
        self.tax_number = num_fiscal
        self.series_number = num_serie
        self.access_key = access_key
        self.total_amount = valor_total_nota
        self.emission_date = data_emissao
        self.register_date = dt_cadastro
        self.xml = xml
        self.link_danfe = link_danfe
        self.link_xml = link_xml
        self.volume_quantity = quantidade_volume


class Transacao:
    transaction_id: str
    authorization_number: str
    nsu: str
    return_message: str
    additional_3: str
    additional_4: str

    def __init__(self, transacao_id: str, numero_autorizacao: str, nsu: str, mensagem_retorno: str, adicional_3: str, adicional_4: str) -> None:
        self.transaction_id = transacao_id
        self.authorization_number = numero_autorizacao
        self.nsu = nsu
        self.return_message = mensagem_retorno
        self.additional_3 = adicional_3
        self.additional_4 = adicional_4


class TransportadoraFob:
    name: str
    company_name: str
    cnpj: str

    def __init__(self, nome: str, razao_social: str, cnpj: str) -> None:
        self.name = nome
        self.company_name = razao_social
        self.cnpj = cnpj


class Address:
    zipcode: str
    address_line: str
    number: str
    complement: str
    neighbourhood: str
    city: str
    ibge_code: str
    state: str
    country: str
    reference: str
    description: str
    address_type: str

    def __init__(self, cep: str, logradouro: str, numero: str, complemento: str, bairro: str, cidade: str, codigo_ibge: str, estado: str, pais: str, referencia: str, descricao: str,
                 tipo_logradouro: str) -> None:
        self.zipcode = cep
        self.address_line = logradouro
        self.number = numero
        self.complement = complemento
        self.neighbourhood = bairro or ''
        self.city = cidade
        self.ibge_code = codigo_ibge
        self.state = estado
        self.country = pais
        self.reference = referencia
        self.description = descricao
        self.address_type = tipo_logradouro or 'Rua'


class Usuario:
    erp_code: str
    id: int
    name: str
    company_name: str
    cpf: str
    rg: str
    birth_date: str
    cnpj: str
    sex: str
    email: str
    organ: str
    state_registry: str
    residential_phone: str
    mobile_phone: str
    address: Address
    delivery_address: Address

    def __init__(self, codigo_referencia: str, id: int, nome: str, razao_social: str, cpf: str, rg: str, data_nascimento: str, cnpj: str, sexo: str, email: str, orgao: str,
                 RegistroEstadual: str, TelefoneResidencial: str, TelefoneCelular: str, Endereco: Dict, EnderecoEntrega: Dict) -> None:
        self.erp_code = codigo_referencia
        self.id = id
        self.name = nome
        self.company_name = razao_social
        self.cpf = cpf
        self.rg = rg
        self.birth_date = data_nascimento
        self.cnpj = cnpj
        self.sex = sexo
        self.email = email
        self.organ = orgao
        self.state_registry = RegistroEstadual
        self.residential_phone = TelefoneResidencial
        self.mobile_phone = TelefoneCelular
        self.address = Address(**Endereco)
        self.delivery_address = Address(**EnderecoEntrega)


class OrderB2B:
    order_id: int
    sale_order_id: int
    order_date: str
    generated_date: str
    erp_code: str
    total_amount: int
    payment_method_amount: int
    discount_amount: int
    freight_amount: int
    status: str
    bonds_quantity: int
    delivery_forecast: str
    tracking_code: str
    channel_id: int
    carrier_id: str
    carrier: str
    service_id: int
    service: str
    freight_type: str
    fob_carrier: TransportadoraFob
    transaction: Transacao
    user: Usuario
    payments: List[Pagamento]
    items: List[Item]
    gift_items: List[ItensBrinde]
    custom_items: List[ItensPersonalizado]
    partner_payment_type: FormaPagamentoParceiro
    partner_shipping_method: FormaEnvioParceiro
    invoices: List[PedidoNotaFiscal]
    protocol: str
    erp_representative: str

    def __init__(self, id: int, pedido_venda_id: int, data_pedido: str, data_geracao: str, codigo_referencia: str, valor_total: int, valor_forma_pagamento: int, valor_desconto: int,
                 valor_frete: int, status: str, quantidade_titulos: int, previsao_entrega: str, codigo_rastreio: str, canal_id: int, transportadora_id: str, transportadora: str, servico_id: int,
                 servico: str, tipo_frete: str, transportadora_fob: Dict, transacao: Dict, usuario: Dict, pagamento: List[Dict], itens: List[Dict], itens_brinde: List[Dict],
                 itens_personalizados: List[Dict], forma_pagamento_parceiro: Dict, forma_envio_parceiro: Dict, pedido_nota_fiscal: List[Dict], protocolo: str, representante: str) -> None:
        self.order_id = id
        self.sale_order_id = pedido_venda_id
        self.order_date = data_pedido
        self.generated_date = data_geracao
        self.erp_code = codigo_referencia
        self.total_amount = valor_total
        self.payment_method_amount = valor_forma_pagamento
        self.discount_amount = valor_desconto
        self.freight_amount = valor_frete
        self.status = status
        self.bonds_quantity = quantidade_titulos
        self.delivery_forecast = previsao_entrega
        self.tracking_code = codigo_rastreio
        self.channel_id = canal_id
        self.carrier_id = transportadora_id
        self.carrier = transportadora
        self.service_id = servico_id
        self.service = servico
        self.freight_type = tipo_frete
        self.fob_carrier = TransportadoraFob(**transportadora_fob) if transportadora_fob is not None else None
        self.transaction = Transacao(**transacao) if transacao is not None else None
        self.user = Usuario(**usuario) if usuario is not None else None
        self.payments = [Pagamento(**p) for p in pagamento] if pagamento is not None else list()
        self.items = [Item(**i) for i in itens] if itens is not None else list()
        self.gift_items = [ItensBrinde(**ib) for ib in itens_brinde] if itens_brinde is not None else list()
        self.custom_items = [ItensPersonalizado(**ip) for ip in itens_personalizados] if itens_personalizados is not None else list()
        self.partner_payment_type = FormaPagamentoParceiro(**forma_pagamento_parceiro) if forma_pagamento_parceiro is not None else None
        self.partner_shipping_method = FormaEnvioParceiro(**forma_envio_parceiro) if forma_envio_parceiro is not None else None
        self.invoices = [PedidoNotaFiscal(**pnf) for pnf in pedido_nota_fiscal] if pedido_nota_fiscal is not None else list()
        self.protocol = protocolo
        self.erp_representative = representante

        if len(self.payments) > 0 and len(self.payments[0].bonds) > 0:
            self.paid_date = self.payments[0].bonds[0].paid_date
            self.payment_type = self.payments[0].payment_option
            self.flag = self.payments[0].flag
            self.installments = self.payments[0].installments
            self.erp_payment_condition = self.payments[0].erp_payment_condition
