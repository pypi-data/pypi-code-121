from javaman.connexio import JManCon


class Albarans:
    __slots__ = '_con'

    _url_get_albara_imprimir = '/albarans/{albara_id}/imprimir'

    def __init__(self, con: JManCon):
        self._con = con

    def get_albara_imprimir(self, p_albara_id: int):
        req = self._con.get(url=self._url_get_albara_imprimir.format(albara_id=p_albara_id))
        return req.json()
