
from sonofman import som_util


class SomCacheTab:
    def __init__(self, rq, tabid, tabtype, tabtitle, fullquery, scrollposy, bbname, isbook, ischapter, isverse, bnumber, cnumber, vnumber, trad, orderby, favfilter):
        self.tabid = tabid
        self.tabtype = tabtype
        self.tabtitle = som_util.SomUtil.rq(tabtitle) if rq else tabtitle
        self.fullquery = som_util.SomUtil.rq(fullquery) if rq else fullquery
        self.scrollposy = scrollposy
        self.bbname = bbname
        self.isbook = isbook
        self.ischapter = ischapter
        self.isverse = isverse
        self.bnumber = bnumber
        self.cnumber = cnumber
        self.vnumber = vnumber
        self.trad = som_util.SomUtil.rq(trad) if rq else trad
        self.orderby = orderby
        self.favfilter = favfilter
