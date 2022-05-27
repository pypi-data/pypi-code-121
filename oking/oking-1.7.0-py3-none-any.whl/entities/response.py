from typing import List


class CatalogoResponse:
    def __init__(self, Message: str, Status: int = 3, codigo_erp: str = '', protocolo: str = '', loja: str = '') -> None:
        self.codigo_erp = codigo_erp
        self.status = Status
        self.message = Message
        self.protocolo = protocolo
        self.loja = loja


class PriceResponse:
    def __init__(self, codigo_erp, Status, Message, protocolo, loja='', codigo_externo_campanha=''):
        self.codigo_erp = codigo_erp
        self.status = Status
        self.message = Message
        self.protocolo = protocolo


class InvoiceResponse:
    def __init__(self, Status: int, Message: str):
        self.status = Status
        self.message = Message


class TrackingResponse:
    def __init__(self, Status: int, Message: str):
        self.status = Status
        self.message = Message


class StockResponse:
    def __init__(self, Identifiers, Status, Message, Protocolo):
        self.identifiers: List[str] = Identifiers
        self.status: int = Status
        self.message: str = Message
        self.protocol: str = Protocolo

class ClientResponse:
    def __init__(self, Identifiers: List[str], Status: int, Message: str, Protocolo):
        self.identifiers: List[str] = Identifiers
        self.status: int = Status
        self.message: str = Message

