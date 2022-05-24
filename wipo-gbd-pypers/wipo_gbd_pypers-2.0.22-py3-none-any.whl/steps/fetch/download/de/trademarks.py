from .designs import Designs


class Trademarks(Designs):
    endpoints = {
        'getBibliografischeDaten_angemeldet_XML_JPG': 'mar_bib_ang_',
        'getBibliografischeDaten_eingetragen_XML_JPG_PDF': 'mar_bib_wvz_bil_eing_',
        'getBibliografischeDaten_zurueckgewiesen_zurueckgenommen_XML_PDF': 'mar_bib_zur_'}
