from javaman.connexio import JManCon
import requests


class Magatzems:
    __slots__ = '_con'

    _url_magatzems = '/magatzems'
    _url_tip_magatzems = '/tip_magatzems'
    _url_moviment_magatzem_ex = '/moviments_magatzems/ex'

    def __init__(self, con: JManCon):
        self._con = con

    def list_magatzems(self):
        res = self._con.get(url=self._url_magatzems)
        return res.json()

    def get_magatzem(self, magatzem_id: int):
        res = self._con.get(url=self._url_magatzems + '/' + str(magatzem_id))
        return res.json()

    def list_tip_magatzems(self):
        res = self._con.get(url=self._url_tip_magatzems)
        return res.json()

    def get_moviment_magatzem_ex(self, moviment_magatzem_id: int):
        res = self._con.get(url=self._url_moviment_magatzem_ex + '/' + str(moviment_magatzem_id))
        return res.json()
