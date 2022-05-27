from javaman.connexio import JManCon
from javaman.errors import JManErrorNoContent


class Wms:
    __slots__ = '_con'

    _url_estoc = '/wms/estoc?en_transicio=false&article_atribut_id={art_atrib_id}'  # &article_lot_id={art_lot_id}
    _url_get_palet_by_numero = "/unitats_logistiques/?numero_unitat={numero_unitat}"
    _url_get_palet_by_id = "/unitats_logistiques/ex/{unitat_logistica_id}"
    _url_post_palet = "/unitats_logistiques/ex"
    _url_put_palet = "/unitats_logistiques/ex/{unitat_logistica_id}"
    _url_delete_magatzem_ordre = '/wms/cancela_ordre/{magatzem_ordre_id}'
    _url_porta_palet = '/wms/palet_fora'
    _url_envia_palet = '/wms/palet_dins'
    _url_get_magatzem_ordre = '/magatzems_ordres/ex/{magatzem_ordre_id}'
    _url_get_magatzems_ordres = '/magatzems_ordres'
    _url_magatzem_ordre_finalitza = '/magatzems_ordres/{magatzem_ordre_id}/finalitza'
    _url_numero_unitat_logistica = '/comptadors/numero_unitat_logistica'
    _url_troba_magatzem_ordre = '/magatzems_ordres?numero_unitat_logistica={sscc}&' \
                                'magatzem_entrada_id={magatzem_entrada_id}&finalitzades=false'
    _url_afegir_unitat_logistica_albara = '/wms/albarans/{albara_id}/expedicions'
    _url_borrar_unitat_logistica_albara = '/wms/albarans/{albara_id}/expedicions/{unitat_logistica_id}'
    _url_tip_estats_unitats_logistiques = '/tip_estats_unitats_logistiques'
    _url_tip_unitats_logistiques = '/tip_unitats_logistiques'
    _url_tip_unitat_logistica_palet = '/tip_unitats_logistiques?palet=S'
    _url_unitat_logistica_format = '/unitats_logistiques_formats?tip_unitat_logistica_id={tip_unitat_logistica_id}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_tip_estats_unitats_logistiques(self):
        tmp_url = Wms._url_tip_estats_unitats_logistiques
        res = self._con.get(url=tmp_url)
        return res.json()

    def get_tip_unitats_logistiques(self):
        tmp_url = Wms._url_tip_unitats_logistiques
        res = self._con.get(url=tmp_url)
        return res.json()

    def get_tip_unitat_logistica_palet(self):
        tmp_url = Wms._url_tip_unitat_logistica_palet
        result = self._con.get(url=tmp_url)
        res = None
        llista = {}
        if result is not None:
            llista = result.json()
        if (llista is not None) and (len(llista) > 0):
            res = llista[0]
        return res

    def get_unitats_logistiques_formats(self, p_tip_unitat_logistica_id: int):
        tmp_url = Wms._url_unitat_logistica_format.format(tip_unitat_logistica_id=p_tip_unitat_logistica_id)
        res = self._con.get(url=tmp_url)
        return res.json()

    def get_estoc(self, p_article_atribut_id: int, p_article_lot_id: int = None):
        tmp_url = Wms._url_estoc.format(art_atrib_id=p_article_atribut_id)
        if p_article_lot_id is not None:
            tmp_url = tmp_url.format(art_lot_id=p_article_lot_id)
        res = self._con.get(url=tmp_url)
        return res.json()

    def get_palet_by_numero(self, p_numero_palet: str):
        tmp_url = Wms._url_get_palet_by_numero.format(numero_unitat=p_numero_palet)
        res = self._con.get(url=tmp_url).json()
        if len(res) == 0:
            raise JManErrorNoContent()
        return res[0]

    def get_palet_by_id(self, p_unitat_logistica_id: int):
        tmp_url = Wms._url_get_palet_by_id.format(unitat_logistica_id=p_unitat_logistica_id)
        res = self._con.get(url=tmp_url)
        return res.json()

    def delete_magatzem_ordre(self, p_magatzem_ordre_id: int):
        tmp_url = Wms._url_delete_magatzem_ordre.format(magatzem_ordre_id=p_magatzem_ordre_id)
        self._con.delete(url=tmp_url)
        return

    def porta_palet(self, p_magatzem_origen_id: int ,p_magatzem_desti_id: int,
                    p_unitat_logistica_id: int = None,
                    p_numero_unitat: str = None,
                    p_article_atribut_id: int = None,
                    p_article_lot_id: int = None):
        parametres = {"unitat_logistica_id": p_unitat_logistica_id,
                      "numero_unitat_logistica": p_numero_unitat,
                      "article_atribut_id": p_article_atribut_id,
                      "article_lot_id": p_article_lot_id,
                      "magatzem_origen_id": p_magatzem_origen_id,
                      "magatzem_desti_id": p_magatzem_desti_id,
                      "iniciar_ordre_auto": True
                      }
        res = self._con.post(url=Wms._url_porta_palet, data=parametres)
        return res.json()

    def crea_palet(self, p_data: dict):
        req = self._con.post(url=self._url_post_palet, data=p_data)
        return req.json()

    def vincula_unitat_logistica_albara(self, p_albara_id: int, p_unitat_logistica: dict):
        req = self._con.post(
            url=self._url_afegir_unitat_logistica_albara.format(albara_id=p_albara_id), data=p_unitat_logistica)
        return req.json()

    def desvincula_unitat_logistica_albara(self, p_albara_id: int, p_unitat_logistica_id: dict):
        req = self._con.delete(
            url=self._url_borrar_unitat_logistica_albara.format(
                albara_id=p_albara_id, unitat_logistica_id=p_unitat_logistica_id)
        )
        return req.json()

    def modifica_palet(self, p_palet_id: int, p_data: dict):
        req = self._con.put(url=self._url_put_palet.format(unitat_logistica_id=p_palet_id), data=p_data)
        return req.json()

    def troba_magatzem_ordre(self, p_sscc: str):
        req = self._con.get(url=self._url_troba_magatzem_ordre.format(
            sscc=p_sscc, magatzem_entrada_id=self._con.config.magatzem_gdis_id())
        )
        return req.json()

    def envia_palet(self, p_magatzem_origen_id: int,
                    p_magatzem_desti_id: int,
                    p_unitat_logistica_id: int):

        parametres = {"unitat_logistica_id": p_unitat_logistica_id,
                      "article_atribut_id": None,
                      "article_lot_id": None,
                      "magatzem_origen_id": p_magatzem_origen_id,
                      "magatzem_desti_id": p_magatzem_desti_id,
                      "iniciar_ordre_auto": True
                      }
        res = self._con.post(url=Wms._url_envia_palet, data=parametres)
        return res.json()

    def get_magatzem_ordre(self, p_magatzem_ordre_id: int):
        res = self._con.get(url=Wms._url_get_magatzem_ordre.format(magatzem_ordre_id=p_magatzem_ordre_id))
        return res.json()

    def get_magatzem_ordre_by_sscc(self, p_sscc: str):
        res = self._con.get(url=Wms._url_get_magatzems_ordres + "?numero_unitat_logistica="+p_sscc+"&finalitzades=False")
        return res.json()

    def nou_numero_unitat_logistica(self) -> str:
        res = self._con.post(url=Wms._url_numero_unitat_logistica, data=None)
        return res.text

    def finalitza_magatzem_ortdre(self, p_magatzem_ordre_id: int):
        res = self._con.put(url=Wms._url_magatzem_ordre_finalitza.format(magatzem_ordre_id=p_magatzem_ordre_id), data=None)
        return res.text
