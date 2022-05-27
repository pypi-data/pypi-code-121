from javaman.connexio import JManCon


class Provincies:
    __slots__ = '_con'

    _url_provincies = '/provincies'
    _url_provincies_ex = '/provincies/ex'

    def __init__(self, con: JManCon):
        self._con = con

    def list(self):
        res = self._con.get(url=self._url_provincies)
        return res.json()

    def get(self, provincia_id: int):
        res = self._con.get(url=self._url_provincies_ex + '/' + str(provincia_id))
        return res.json()
