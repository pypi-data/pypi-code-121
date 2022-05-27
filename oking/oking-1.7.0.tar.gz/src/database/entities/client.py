from datetime import datetime


class Client:
    def __init__(self, nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia,
                 cliente_erp, direcao, data_sincronizacao):
        self.name: str = nome
        self.company_name: str = razao_social
        self.cpf: str = cpf
        self.cnpj: str = cnpj
        self.email: str = email
        self.residential_phone: str = telefone_residencial
        self.mobile_phone: str = telefone_celular
        self.zipcode: str = cep
        self.address_type: str = tipo_logradouro
        self.address: str = logradouro
        self.number: str = numero
        self.complement: str = complemento
        self.neighbourhood: str = bairro
        self.city: str = cidade
        self.state: str = estado
        self.reference: str = referencia
        self.client_erp: str = cliente_erp
        self.direction: str = direcao
        self.sync_date: datetime = data_sincronizacao
