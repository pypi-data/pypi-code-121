""" This file contains a look up table for receiver calibration dates and directory names. """

from datetime import date

cal_lut = {
    """ Look up table for which calibration files correspond with which dates """
    "AA": {date(2018, 5, 25): "BriarwoodDiffTest_2018_05"},
    "AO": {date(2017, 7, 19): "Arecibo_2017_07"},
    "BX": {
        date(2016, 1, 6): "Baxley_2016_01",
        date(2016, 7, 22): "Baxley_2016_07",
        date(2016, 11, 4): "Baxley_2016_11",
        date(2017, 1, 26): "Baxley_2017_01",
        date(2017, 5, 2): "Baxley_2017_05",
        date(2019, 6, 13): "Baxley_2019_06",
    },
    "BW": {
        date(2015, 6, 10): "Briarwood_2015_06",
        date(2016, 5, 25): "Briarwood_2016_05",
        date(2017, 3, 10): "Briarwood_2017_03",
        date(2017, 8, 8): "Briarwood_2017_08",
        date(2017, 8, 18): "Briarwood_2017_09",
        date(2018, 5, 25): "Briarwood_2018_05",
        date(2018, 10, 29): "Briarwood_2018_10",
        date(2019, 8, 21): "Briarwood_2019_08",
    },
    "BD": {
        date(2016, 3, 25): "Burden_2016_03",
        date(2016, 7, 27): "Burden_2016_07",
        date(2017, 6, 29): "Burden_2017_06",
    },
    "DA": {
        date(2016, 3, 24): "Delaware_2016_03",
        date(2017, 3, 23): "Delaware_2017_03",
        date(2017, 5, 9): "Delaware_2017_05",
    },
    "JU": {
        date(2015, 7, 30): "Juneau_2015_07",
        date(2017, 4, 26): "Juneau_2017_04",
    },
    "LP": {
        date(2017, 6, 15): "LostPines_2017_06",
        date(2018, 6, 29): "LostPines_2018_06",
    },
    "OX": {date(2017, 8, 1): "Oxford_2017_07"},
    "PA": {
        date(2014, 9, 26): "PARI_2014_09",
        date(2015, 4, 23): "PARI_2015_04",
        date(2016, 4, 7): "PARI_2016_04",
        date(2016, 8, 13): "PARI_2016_08",
        date(2017, 4, 13): "PARI_2017_04",
        date(2017, 5, 31): "PARI_2017_05",
        date(2018, 11, 1): "PARI_2018_11",
    },
}
