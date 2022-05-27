from javaman.connexio import JManCon


class Tercers:
    __slots__ = '_con'

    _url_get_tercers = '/tercer'
    _url_get_tercers_parametres = '/tercer/{id_tercer}/parametres'

    def __init__(self, con: JManCon):
        self._con = con

    def get_tercer(self, p_tercer: int):
        req = self._con.get(url=self._url_get_tercers+'/'+str(p_tercer))
        return req.json()

    def get_tercer_parametres(self, p_tercer: int):
        req = self._con.get(url=Tercers._url_get_tercers_parametres.format(id_tercer=p_tercer))
        return req.json()
