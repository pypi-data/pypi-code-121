from javaman.connexio import JManCon


class Usuaris:
    __slots__ = '_con'

    _url_usuaris = '/usuaris'
    _url_login = '/login/usuari'

    def __init__(self, con: JManCon):
        self._con = con

    def list(self):
        res = self._con.get(url=self._url_usuaris)
        return res.json()

    def get(self, usr_guid: str):
        res = self._con.get(url=self._url_usuaris + '/' + usr_guid)
        return res.json()

    def delete_token(self, token: str):
        self._con.delete(url='/logout/' + token)
        return

    def get_current_user(self):
        res = self._con.get(url='/current_user')
        return res.json()
