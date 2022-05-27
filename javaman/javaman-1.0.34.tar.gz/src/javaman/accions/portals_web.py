from javaman.connexio import JManCon


class PortalsWeb:
    __slots__ = '_con'

    _url_portal = '/portals_web/{num_portal}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_portal_web(self, portal_web_id: int):
        tmp_url = PortalsWeb._url_portal.format(num_portal=portal_web_id)
        req = self._con.get(url=tmp_url)
        return req.json()
