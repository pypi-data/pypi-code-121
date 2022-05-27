from javaman.connexio import JManCon


class Articles:
    __slots__ = '_con'

    _url_get_articles = '/articles'
    _url_get_atributs = '/articles/{article_id}/articles_atributs'
    _url_get_articles_lots = '/articles_lots?article_atribut_id={article_atribut_id}'
    _url_get_article_lot = '/articles_lots?lot={lot}&article_atribut_id={article_atribut_id}'
    _url_get_article_lot_ex = '/articles_lots/ex?lot={lot}&article_atribut_id={article_atribut_id}'
    _url_get_article_lot_id = '/articles_lots/{id}'
    _url_get_article_estoc_magatzem = '/articles_estocs/{article_atribut_id}?magatzem_id={magatzem_id}'
    _url_post_article_lot = '/articles_lots'

    def __init__(self, con: JManCon):
        self._con = con

    def get_article(self, p_article: int):
        req = self._con.get(url=self._url_get_articles+'/'+str(p_article))
        return req.json()

    def get_article_by_ean(self, p_ean13_article: str):
        req = self._con.get(url=self._url_get_articles+'?ean13_article='+str(p_ean13_article))
        return req.json()

    def get_article_atribut(self, p_article_id: int):
        tmp_atributs = self.get_articles_atributs(p_article_id)
        res = None
        if len(tmp_atributs) > 0:
            res = tmp_atributs[0]
        return res

    def get_articles_atributs(self, p_article_id: int):
        tmp_url = Articles._url_get_atributs.format(article_id=p_article_id)
        req = self._con.get(url=tmp_url)
        return req.json()

    def get_article_lots(self, p_article_atribut_id: int, p_magatzem_id: int = None, p_palet_complert: bool = None):
        tmp_url = Articles._url_get_articles_lots.format(article_atribut_id=p_article_atribut_id)
        if p_palet_complert is not None:
            if p_palet_complert is True:
                tmp_url += "&palet_complert=S"
            else:
                tmp_url += "&palet_complert=N"
        if p_magatzem_id is not None:
            tmp_url += "&magatzem_id="+str(p_magatzem_id)

        req = self._con.get(url=tmp_url)
        return req.json()

    def get_article_lot_estoc(self, p_article_atribut_id: int, p_lot: str, p_magatzem_id: int = None, p_palet_complert: bool = None):
        tmp_url = Articles._url_get_article_lot_ex.format(article_atribut_id=p_article_atribut_id, lot=p_lot)
        if p_palet_complert is not None:
            if p_palet_complert is True:
                tmp_url += "&palet_complert=S"
            else:
                tmp_url += "&palet_complert=N"
        if p_magatzem_id is not None:
            tmp_url += "&magatzem_id="+str(p_magatzem_id)

        req = self._con.get(url=tmp_url)

        result = None
        if req is not None:
            llista = req.json()
            if len(llista) == 1:
                result = llista[0]
        return result

    def get_article_lot(self, p_article_atribut_id: int, p_lot: str):
        tmp_url = Articles._url_get_article_lot.format(article_atribut_id=p_article_atribut_id, lot=p_lot)
        req = self._con.get(url=tmp_url)
        result = None
        if req is not None:
            llista = req.json()
            if len(llista) == 1:
                result = llista[0]
        return result

    def get_article_lot_id(self, p_article_atribut_id: int, p_lot_id: int, p_magatzem_id: int = None, p_palet_complert: bool = None):
        tmp_url = Articles._url_get_article_lot_id.format(article_atribut_id=p_article_atribut_id, id=p_lot_id)
        if p_palet_complert is not None:
            if p_palet_complert is True:
                tmp_url += "&palet_complert=S"
            else:
                tmp_url += "&palet_complert=N"
        if p_magatzem_id is not None:
            tmp_url += "&magatzem_id="+str(p_magatzem_id)
        req = self._con.get(url=tmp_url)
        return req.json()

    def get_article_estoc_magatzem(self, p_article_atribut: int, p_magatzem: int):
        tmp_url = Articles._url_get_article_estoc_magatzem.format(
            article_atribut_id=p_article_atribut, magatzem_id=p_magatzem
        )
        req = self._con.get(url=tmp_url)
        llista = None
        if req is not None:
            llista = req.json()
        return llista

    def post_article_lot(self, p_data: dict):
        req = self._con.post(url=Articles._url_post_article_lot, data=p_data)
        return req.json()
