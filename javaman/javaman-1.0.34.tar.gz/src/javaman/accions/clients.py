from javaman.connexio import JManCon


class Clients:
    __slots__ = '_con'

    _url_crear_client = '/clients'
    _url_get_client = '/clients'
    _url_importar_tercers = '/importar_tercers'

    def __init__(self, con: JManCon):
        self._con = con

    def crear(self, p_client: dict):
        req = self._con.post(url=self._url_crear_client, data=p_client)
        return req.json()

    def get_client(self, p_client: int):
        req = self._con.get(url=self._url_crear_client+'/'+str(p_client))
        return req.json()

    def importar_tercers(self, p_dades: dict):
        req = self._con.post(url=self._url_importar_tercers, data=p_dades)
        return req.json()
