""" This file contains a set of lookup dictionaries for the transmitters and
receivers
"""
site_mapping = {
    "AO": "Arecibo",
    "BX": "Baxley",
    "BW": "Briarwood",
    "BD": "Burden",
    "DA": "Delaware",
    "JU": "Juneau",
    "KG": "Kagoshima",
    "LP": "LostPines",
    "OX": "Oxford",
    "PA": "PARI",
    "SL": "Sligo",
    "TK": "Toolik",
}
site_mapping_inv = {
    "Arecibo": "AO",
    "Arecibo, Puerto Rico": "AO",
    "Baxley": "BX",
    "Briarwood": "BW",
    "Briarwood Academy": "BW",
    "Burden": "BD",
    "Delaware": "DA",
    "DASEF": "DA",
    "Juneau": "JU",
    "Kagoshima": "KG",
    "LostPines": "LP",
    "Lost Pines": "LP",
    "Oxford": "OX",
    "OXFORD Mississippi": "OX",
    "PARI": "PA",
    "Sligo": "SL",
    "Toolik": "TK",
}
tx_dict = {
    "NAA": [44.644982, -67.282803, 24e3],
    "NML": [46.366, -98.336, 25.2e3],
    "NLK": [48.203, -121.917, 24.8e3],
    "NAU": [18.399, -67.178, 40.75e3],
    "NPM": [21.420, -158.151, 21.4e3],
    "NRK": [63.850, -22.466, 37.5e3],
    "NWC": [-21.816, 114.165, 19.8e3],
    "HW3": [46.714, 1.244, 18.3e3],
    "GBZ": [52.9, -3.28, 19.6e3],
    "ICV": [40.92, 9.73, 20.27e3],
    "JJI": [32.04, 130.81, 22.2e3],
    "DHO": [53.08, 7.61, 23.4e3],
}
# 0s correspond to unknown day of week
# Mon=1, Tue=2, Wed=3, Thur=4, Fri=5, Sat=6, Sun=7
tx_off = {
    "NAA": 1,
    "NML": 2,
    "NLK": 4,
    "HW3": 0,
    "NAU": 0,
    "NPM": 0,
    "NRK": 0,
    "NWC": 0,
}
rx_dict = {
    "AO": [18.3485103, -66.7502039],
    "BX": [31.877906, -82.362481],
    "BW": [33.427531, -82.579384],
    "BD": [37.324386, -96.756617],
    "DA": [39.278852, -75.581115],
    "JU": [58.590243, -134.905163],
    "KG": [33.77617194, -84.39687833],
    "LP": [30.088556, -97.171495],
    "OX": [34.430183, -89.388017],
    "PA": [35.199273, -82.870521],
    "SL": [36.43634139, -76.09051639],
    "TK": [33.77616944, -84.39686972],
}
