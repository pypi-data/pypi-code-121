from datetime import datetime


class Endereco:
    ativo: bool
    tipo_logradouro: str
    endereco: str
    cep: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    estado: str
    telefone_contato: str
    descricao_endereco: str
    referencia_entrega: str
    pais: str
    codigo_ibge: str

    def __init__(self, ativo: bool, tipo_logradouro: str, endereco: str, cep: str, numero: str, complemento: str, bairro: str, cidade: str, estado: str, telefone_contato: str, descricao_endereco: str,
                 referencia_entrega: str, pais: str, codigo_ibge: str) -> None:
        self.ativo = ativo
        self.tipo_logradouro = tipo_logradouro
        self.endereco = endereco
        self.cep = cep
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.telefone_contato = telefone_contato
        self.descricao_endereco = descricao_endereco
        self.referencia_entrega = referencia_entrega
        self.pais = pais
        self.codigo_ibge = codigo_ibge


class Cliente:
    nome: str
    razao_social: str
    sexo: str
    data_nascimento: datetime
    data_constituicao: str
    cpf: str
    cnpj: str
    rg: str
    orgao: str
    email: str
    senha: str
    senha_expirada: bool
    telefone_residencial: str
    telefone_celular: str
    codigo_referencia: str
    inscricao_estadual: str
    inscricao_municipal: str
    limite_credito: int
    data_bloqueio: datetime
    parcelamento: bool
    tipo_pessoa: str
    tipo_usuario: int
    codigo_livro: str
    compra_liberada: bool
    contribuinte_icms: int
    optante_simples_nacional: bool
    fator_juros: int
    fator_frete: int
    fator_cliente: int
    solicitacao_limite_credito: int
    quantidade_lojas: int
    valida_pedido_minimo: bool
    codigo_suframa: str
    eh_cif: bool
    site_pertencente: str
    ramo_atividade: str
    segmento: str
    grupo_economico: str
    endereco: Endereco
    protocolado: bool

    def __init__(self, nome: str, razao_social: str, sexo: str, cpf: str, cnpj: str, email: str, endereco: Endereco, telefone_residencial: str, telefone_celular: str, codigo_referencia: str,
                 orgao: str = str(), senha: str = str(), rg: str = str(), senha_expirada: bool = False, inscricao_estadual: str = str(), inscricao_municipal: str = str(), limite_credito: int = 0,
                 data_bloqueio: datetime = None, parcelamento: bool = False, tipo_pessoa: str = str(), tipo_usuario: int = 0, codigo_livro: str = str(), compra_liberada: bool = False,
                 contribuinte_icms: int = 0, optante_simples_nacional: bool = False, fator_juros: int = 0, fator_frete: int = 0, fator_cliente: int = 0, solicitacao_limite_credito: int = 0,
                 quantidade_lojas: int = 0, valida_pedido_minimo: bool = False, codigo_suframa: str = str(), eh_cif: bool = False, site_pertencente: str = str(), ramo_atividade: str = str(),
                 segmento: str = str(), grupo_economico: str = str(), protocolado: bool = False, data_nascimento: datetime = None, data_constituicao: str = None) -> None:
        self.nome = nome
        self.razao_social = razao_social
        self.sexo = sexo
        self.data_nascimento = data_nascimento
        self.data_constituicao = data_constituicao
        self.cpf = cpf
        self.cnpj = cnpj
        self.rg = rg
        self.orgao = orgao
        self.email = email
        self.senha = senha
        self.senha_expirada = senha_expirada
        self.telefone_residencial = telefone_residencial
        self.telefone_celular = telefone_celular
        self.codigo_referencia = codigo_referencia
        self.inscricao_estadual = inscricao_estadual
        self.inscricao_municipal = inscricao_municipal
        self.limite_credito = limite_credito
        self.data_bloqueio = data_bloqueio
        self.parcelamento = parcelamento
        self.tipo_pessoa = tipo_pessoa
        self.tipo_usuario = tipo_usuario
        self.codigo_livro = codigo_livro
        self.compra_liberada = compra_liberada
        self.contribuinte_icms = contribuinte_icms
        self.optante_simples_nacional = optante_simples_nacional
        self.fator_juros = fator_juros
        self.fator_frete = fator_frete
        self.fator_cliente = fator_cliente
        self.solicitacao_limite_credito = solicitacao_limite_credito
        self.quantidade_lojas = quantidade_lojas
        self.valida_pedido_minimo = valida_pedido_minimo
        self.codigo_suframa = codigo_suframa
        self.eh_cif = eh_cif
        self.site_pertencente = site_pertencente
        self.ramo_atividade = ramo_atividade
        self.segmento = segmento
        self.grupo_economico = grupo_economico
        self.endereco = endereco
        self.protocolado = protocolado
