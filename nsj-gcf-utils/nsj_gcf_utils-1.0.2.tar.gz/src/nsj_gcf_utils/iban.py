class IBAN:
    def __init__(self):
        pass

    def setPais(self, pais:str):
        if pais != "BR":
            raise Exception("Pais não suportado")
        self.pais = pais
        return self

    def getPais(self)->str:
        return self.pais

    def setBanco(self, ispb:str):
        self.banco = ispb.zfill(8)
        return self

    def getBanco(self)->str:
        return self.banco

    def setAgencia(self, agencia:str):
        self.agencia = agencia.zfill(5)
        return self

    def getAgencia(self)->str:
        return self.agencia

    def setConta(self, conta:str):
        self.conta = conta.zfill(10)
        return self

    def getConta(self)->str:
        return self.conta

    def setTipo(self, tipo:str):
        if not tipo in ['C', 'c', 'P', 'p']:
            raise Exception("O tipo da conta deve ser C para Conta Corrente ou P para Conta Poupança")
        self.tipo = tipo
        return self

    def getTipo(self)->str:
        return self.tipo

    def setTitular(self, titular:int):
        if titular > 0 and titular < 10:
            self.titular = chr(titular + ord('0'))
        elif titular >= 10 and titular <= 35:
            self.titular = chr(titular - 9 + ord('A'))
        else:
            raise Exception("O número do titular deve ser um inteiro entre 1 e 35")
        return self

    def getTitular(self)->int:
        if self.titular >= '1' and self.titular <= '9':
            return ord(self.titular) - ord('0')
        return ord(self.titular) - ord('A')

    def getIban(self):
        return IBAN.preencherDv(self.pais + '00' + self.banco + self.agencia + self.conta + self.tipo + self.titular)

    def parseIban(self, iban:str, check:bool = False):
        if check and not IBAN.validarDv(iban):
            raise Exception("O IBAN inserido não é válido")
        self.pais = iban[:2]
        self.banco = iban[4:12]
        self.agencia = iban[12:17]
        self.conta = iban[17:27]
        self.tipo = iban[27]
        self.titular = iban[28]

    def preencherDv(iban:str):
        soma = 0;
        for c in iban[4:] + iban[:2]:
            if c >= '0' and c <= '9':
                soma = soma * 10 + ord(c) - ord('0')
            elif c >= 'A' and c <= 'Z':
                soma = soma * 100 + ord(c) - ord('A') + 10
            elif c >= 'a' and c <= 'z':
                soma = soma * 100 + ord(c) - ord('a') + 10
            else:
                raise Exception()
        return iban[:2] + str(98 - soma * 100 % 97) + iban[4:]

    def validarDv(iban:str):
        soma = 0;
        for c in iban[4:] + iban[:4]:
            if c >= '0' and c <= '9':
                soma = soma * 10 + ord(c) - ord('0')
            elif c >= 'A' and c <= 'Z':
                soma = soma * 100 + ord(c) - ord('A') + 10
            elif c >= 'a' and c <= 'z':
                soma = soma * 100 + ord(c) - ord('a') + 10
            else:
                raise
        return soma % 97 == 1
