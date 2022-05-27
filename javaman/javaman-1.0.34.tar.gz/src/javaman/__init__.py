__all__ = ['JMan', 'JManFb', 'JManError', 'JManErrorNoContent']

import fdb
from . import fb_consultes
from . import accions
from .errors import *
from .connexio import JManCon, ConfigJavaman


class JMan:

    __slots__ = '_con'

    def __init__(self, config_data: dict):
        self._con = JManCon(config_data=config_data)

    @property
    def config(self) -> ConfigJavaman:
        return self._con.config

    @property
    def clients(self):
        return accions.Clients(con=self._con)

    @property
    def tercers(self):
        return accions.Tercers(con=self._con)

    @property
    def repartidors(self):
        return accions.Repartidors(con=self._con)

    @property
    def articles(self):
        return accions.Articles(con=self._con)

    @property
    def usuaris(self):
        return accions.Usuaris(con=self._con)

    @property
    def pobles(self):
        return accions.Pobles(con=self._con)

    @property
    def provincies(self):
        return accions.Provincies(con=self._con)

    @property
    def comandes(self):
        return accions.Comandes(con=self._con)

    @property
    def regularitzacions(self):
        return accions.Regularitzacions(con=self._con)

    @property
    def portals_web(self):
        return accions.PortalsWeb(con=self._con)

    @property
    def wms(self):
        return accions.Wms(con=self._con)

    @property
    def magatzems(self):
        return accions.Magatzems(con=self._con)

    @property
    def albarans(self):
        return accions.Albarans(con=self._con)


class JManFb:
    __slots__ = '_con'

    def __init__(self, config_data: dict):
        self._con = fdb.connect(
            user=config_data["user"],
            password=config_data["password"],
            host=config_data["host"],
            port=config_data["port"],
            database=config_data["database"],
            charset=config_data["charset"],
        )

    def select(self, sql: str, args: tuple = None) -> list:
        cur = self._con.cursor()
        cur.execute(operation=sql, parameters=args)
        res = cur.fetchall()
        cur.close()
        return res

    def c_sync_clients(self):
        return self.select(sql=fb_consultes.sync_clients)

    def c_sync_clients_mrest(self):
        return self.select(sql=fb_consultes.sync_clients_mrest)

    def c_sync_productes(self):
        return self.select(sql=fb_consultes.sync_productes)

    def c_sync_transportistes(self):
        return self.select(sql=fb_consultes.sync_transportistes)

    def c_sync_comandes_pendents(self):
        return self.select(sql=fb_consultes.sync_comandes_pendents)

    def c_sync_magatzems_ordres_pendents(self, p_magatzem_entrada_id: int):
        return self.select(sql=fb_consultes.sync_magatzems_ordres_pendents, args=(p_magatzem_entrada_id,))

    def c_sync_moviments_magatzems_pendents(self, p_magatzem_sortida_id: int):
        return self.select(sql=fb_consultes.sync_moviments_magatzems_pendents, args=(p_magatzem_sortida_id,))

    def c_sync_comanda(self, comanda_id: int):
        return self.select(sql=fb_consultes.sync_comanda, args=(comanda_id,))[0]

    def c_sync_comanda_linies(self, comanda_id: int):
        return self.select(sql=fb_consultes.sync_comanda_linies, args=(comanda_id,))
