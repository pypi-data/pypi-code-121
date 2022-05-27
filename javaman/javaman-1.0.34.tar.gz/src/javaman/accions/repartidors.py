from javaman.connexio import JManCon


class Repartidors:
    __slots__ = '_con'

    _url_get_repartior = '/repartidors/{id_rep}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_repartidor(self, p_repartidor: int):
        req = self._con.get(url=Repartidors._url_get_repartior.format(id_rep=p_repartidor))
        return req.json()

