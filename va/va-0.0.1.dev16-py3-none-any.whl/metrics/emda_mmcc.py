from emda.ext.cc import cc_overall_realsp
from emda.ext.cc import cc_overall_fouriersp


def run_realmmcc(mapa, mapb, mask=None):
    """
        Calculate the real space map-modelmap correlation

    :param mapa: primary map
    :param mapb: map from the model
    :param mask: mask map if availabel
    :return: cross-correlation value
    """

    realcc = cc_overall_realsp(mapa, mapb, mask)

    return realcc


