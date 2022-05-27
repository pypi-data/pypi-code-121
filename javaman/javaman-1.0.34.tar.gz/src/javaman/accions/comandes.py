from javaman.connexio import JManCon


class Comandes:
    __slots__ = '_con'

    _url_portal_web_comanda = '/portals_web/{numcom}/comanda'
    _url_pendent_servir = '/comandes/{id_com}/pendent_servir'
    _url_bloqueig = '/comandes/{id_com}/magatzem_retingut'
    _url_comencar = '/comandes/{id_com}/iniciar'
    _url_cancelar = '/comandes/{id_com}/cancelar'
    _url_tancar = '/comandes/{id_com}/tancar'
    _url_albarans = '/comandes/{id_com}/albarans/iniciats'
    _url_comanda_distribucio = '/comandes/{id_com}/distribucio'

    def __init__(self, con: JManCon):
        self._con = con

    def crear(self, portal_web_token: str, comanda: dict):
        tmp_url = Comandes._url_portal_web_comanda.format(numcom=portal_web_token)
        req = self._con.post(url=tmp_url, data=comanda)
        return req.json()

    def bloquejar(self, comanda_id: int):
        req = self._con.post(url=Comandes._url_bloqueig.format(id_com=comanda_id), data=None)
        return req.json()

    def pendent_servir(self, comanda_id: int):
        req = self._con.post(url=Comandes._url_pendent_servir.format(id_com=comanda_id), data=None)
        return req.json()

    def comencar(self, comanda_id: int):
        req = self._con.post(url=Comandes._url_comencar.format(id_com=comanda_id), data=None)
        return req.json()

    def llistar_albarans(self, comanda_id: int):
        req = self._con.get(url=Comandes._url_albarans.format(id_com=comanda_id))
        return req.json()

    def assignar_usuari(self, comanda_id: int, emplat_id: int):
        req = self._con.post(url='/comandes/' + str(comanda_id) + '/assignar', data={'id': emplat_id})
        return req.json()

    def pausar(self, comanda_id: int):
        req = self._con.post(url='/comandes/' + str(comanda_id) + '/pausar', data=None)
        return req.json()

    def cancelar(self, comanda_id: int):
        req = self._con.post(url=Comandes._url_cancelar.format(id_com=comanda_id))
        return req.json()

    def tancar(self, comanda_id: int):
        req = self._con.post(url=Comandes._url_tancar.format(id_com=comanda_id))
        return req.json()

    def put_comanda_distribucio(self, comanda_distribucio: dict):
        tmp_url = Comandes._url_comanda_distribucio.format(id_com=comanda_distribucio["comanda_id"])
        req = self._con.put(url=tmp_url, data=comanda_distribucio)
        return req.json()
