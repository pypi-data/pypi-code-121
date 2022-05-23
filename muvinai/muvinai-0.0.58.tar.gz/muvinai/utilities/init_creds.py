import os
import json
import pymongo
import gspread
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import mercadopago

load_dotenv()
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')
flask_secret = os.getenv('SECRET_KEY')
mailchimp_key = os.getenv('MAILCHIMP_CLIENT')
sportaccess_key = os.getenv('SPORTACCESS_PASSWORD')
api_key = os.getenv('API_KEY')
sportclub_id = os.getenv('SPORTCLUB_ID')

try:
    test = os.getenv('TEST').lower() == 'true'
except AttributeError:
    test = False

gc = None
db_prod = None
db_test = None
sdk_test = None
sdk_prod = None

test_str = "TEST" if test else "PRODUCCION"
print("Environment: " + test_str)


def init_gspread():
    """ Inicializar gspread (si no fue inicializado anteriormente)

    :return: gspread
    :rtype: Client
    """
    global gc
    if gc is not None:
        return gc   # gc ya esta instanciada

    encrypted = b'gAAAAABhwj0N7xSHt0HdNkQA2arqrs4pDHQMKI4u5CwPJsTT1QZvpAk1MV6eI8Kdyf66C4YJYoDWmtTEMYICbZT0C0kZ2qr6' \
                b'Zb2_1v3C1rByMrRDzfnEAcaqCfVyqQGcaMeIn7eCNiDtWA4NLGO0qH8cPAyEV6JTnJH3nljSlo6cYDKwvD0f6-zRrqOj5qdN4' \
                b'HESJuDGgR3ZDcjFEnPGO-N_wMewtm76gkeJlR-tITOcOQp12f0N6n4WcI4lznOIGMpFzbQ94TL1-NuMSzG_ujTCZEXpSc9UgvdP' \
                b'Lxx0eqM_rOm2zly2yX1oxLKSjISCjDviZ5f59AUuwXf90w_PFbSjaizNP5ZgTZ_DdxVAfiFQR1ZJryHcKz4_ISYHp1zp70kmpI' \
                b'O3QZFffnD6UsUh8jxqYhJoBfc9UnTeY2k7pDPJElfuU98QlftsFxawytLGEIgrm0YzPWUguskv397MlA1nhEtk3iGgkX21NPuH' \
                b'8NkdqXMfGmtV6Wz1Atwq4t-UtHZTKJ3XUEdbU-51C36BdfiGh-F9P7I3U0_NWx9ts0cvyenSSnxjfntH1qE7MOH0-J3Np9oPSHm' \
                b'UkFPzy0ZUTXdO76EKi0ZRK4b4l8s9KD8MjI5i37oP7U-fmQ0d_kudEkDlY1AZxJMO8-YhG7DPvblaP9TOx6lYbzxdG7yoeQseCO' \
                b'NKkgcZADAbliFgUGRmg2n692CkIF64zrP2IgQ_aqLznp4CxI1GOXXfsT8dzYsBzM9bdazYNZ-n7Hgmo_kinpU5N8iVqgZiGV34' \
                b'HEOcSsPbCPhS7dcNph448SRYiGhG2S2GhKXwLfWRKf3UWAHU7TIAJw-i3XiLGc_uZ7b2PglASn7iPJI-uJS1A0WPTfdssfvHl_i' \
                b'1Zd4k2cXNXlL1w_h_7RloyUEEMthnqBqIYT80suixg_krXScBOSZrvIVEP5mjdVgWenaPvIAPUlFbsYwo34448ff2vsh24D4JKH' \
                b'tJ-vZfE-2kyZUQecWT1BistV5ZiNw-kKO5FfRLuA3YyoiIrw0Wb6dwCv4sc9dq1B82vr-RYCoZsCyuJYLKS7HwdXpJWERFTPFf' \
                b'X_jWKwnRuQ9RWS4uG7r3o1iFWNfuwM05Hwo15O_391acG6P0YExH-0FNBVNHDj8DoyXOEJ_dALWxVukLIrK9wykefBPxKF4ej8' \
                b'3gEk52nriSkX33uLeeE2CcRGbsxbI8SSgaI1beT2Ivxdh0C1QJnZ5tXDIKzi3vtB0GnjGkuOZZ9vsMoG4aGUTlXxxPoOzsVre' \
                b'MdvyC6nOU3TgklNv-EXSav9lPUUgoFl2WOu7YSk64-4LHOSde22q9is0jQu5UakBpESmtRNmfMWxF5MqWjxNxJcqSfyv_DSDS' \
                b'Srf9l48Nsb6cIUt-LHdq7CIlrHbkNRlZ_X_p_iiaOL5Em8E979ldzpeByvAozFHKWRkWFbfeleS11gFgDMx8ItiiQizml_VyD' \
                b'kJi_zi7Mm7mUX7DO7x2vpdI_dxyG-yJMlFQLYJ3q4DrWOABbK1zBQJ-7ZIJDJo003gCohfuCWkyO_QGcUiiWFlJ-Cbe7gO3Bh' \
                b'2yztkP53vPt-af222imVtI_xgWT3_jjLY7m6-_870tWB4NEJ_c8UlKiAdV4Ri9vSmcBOiWMa77nCxjPDSQSe5B1fk22ztENBg' \
                b'LngdvmQAYvo-Ck8lOSkkuraD5_9IZpdOmfVB8klMFldctfNqdFSUYGlwRnm4lWLJobZGVWvQ-ozZfBb-x7rswII6EyjOdTKhe' \
                b'2ZmmWuzBLzBGRQt44hCbTSYHO9schkM8nA6FzoGT8Yx4m-H06F_q9fnIMewADoyLkPjhLkWx5pNJFKNgE3ee5NVmjdBps0_v5' \
                b'OkoxTEuj-NgNWfEwD720i9Im3nnRX0ltEMzk80m_JaUIi8-ltKDtgbuzTbpqkV4REP805cZHOupLwhuijmUQunCd6WlW_jT9UD' \
                b'l5_mw6M6B8rT3yoW5lmZnR1QqbgcCpGUZqul_6wptTDCaHBk4sDPMZBJ-Dl4NRxEh9vK2_uJS-En5c5-t1Zt5UwQ-jYIFRJ-lz' \
                b'717ZEm-w3g-_ab_1lpC8LPWVYbIXmqI2TYXjukjJbKhTWHul4wKbxp94SN0TCDhYvDZrWOjZxMF2HkRxBUOWT2sDADet0BNxFV' \
                b'v8CXZO7G1_3qiSZP-r2pCy19fZ9jtyP5bcFv7TqQatPSg1R2ayhMbFwZfvBlVznuVAvgK0gecJaNYAe5c-LQu2KmVuQiaH-Pl7' \
                b'd3YPv3ZvnmXqgmXIEyy2ZRLX7nmtleSMH0qYn41PolZO_q3uK9HplK4zlzoMTHIY2cTUEg-4Hs-B8s1w59W692GV16ii2NGA0k' \
                b'GF6RYuEZMMXg6N0SelSAQb6ZOWKIK1HAQ5aOsy1LrIB5xFkv4U54PrcMWsLa3NYwktM-_pRLbKPnQNvbjG62tGmV9tww0AzoEg' \
                b'usfK9D4mOZTEpE230Zqn2L2VrcHa9-vFJ21hpURkNlPs5ttMGN8TE44q9vMXIq6pJBl8w9_yXeipe0hzylJ1b81_8tFtRZXuzo' \
                b'IZ5HD-b4Rw-xvrxpMCmw0tnOo54pdcI7hKdzaNv2hyu0y41B1ektgCHh033az7zyJf72u_an_LoZlq0IINWBeUMeXI552ohIwl' \
                b'M4aDgei_LhPTluR9kDkxFeSkxhHEQA6K__MJAq8M8HBp3xIQF3QeA7tNDp9n5S1OBGBgHB8CFjc2BM81pEuOSNKUd55QPZcy-_' \
                b'SnKQ0Pu6s7CJBd-qVcLzNYMVaUvyg9-LzmozOpSOxZGwvlaUVtL3k1Ewdbdv6Izsagvf_YYJrOu4y1MRCZ1XhnUwIM0iwWcCcL' \
                b'N2aEwcM_a0mMAcMTylTyVeqmmjHFFK6pC3XsABOHxvhIaG4I3erhHXfoCT7x9Nn-wb9NtxCjb62-3ii6cKMklTIEIQ-C14dMwe' \
                b'te79kiKz75m_8c6WuOZH8yKWl4uzK3QQ0HW0HTVvMHU5gNzcs8HH4__fUjp4Uhir2blDbDwpWW3O2LCb3Gbk0cNcLDKlLwUijk' \
                b'BQPP8fJgN_z7AhoA2gZwapY8ugXLSPsOI3K08Ualk33YVwdbgE4FIjILndOp0sUY3IWd_TCV9BU7tE0ZdncfU3h2XyIOhM='

    key = os.getenv("CRYPTO").encode('utf-8')

    fernet = Fernet(key)
    gspread_credentials = fernet.decrypt(encrypted).decode()
    gc = gspread.service_account_from_dict(json.loads(gspread_credentials))
    return gc


def init_mongo(_test: bool = None):
    """ Inicializar la base de mongo. Si no recibe ningun parametro inicializa la\
        base de datos segun la variable de entorno test.

    Es posible inicializar las bases de produccion y de test al mismo tiempo de la siguiente manera:
        
        >>> db_prod = init_mongo(False)
        >>> db_test = init_mongo(True)

    :param _test: Indica la base a inicializar (True para test, False para produccion), defaults to None
    :type _test: bool, optional
    :return: base de mongo
    :rtype: Database
    """    
    global db_prod
    global db_test
    if _test is None:
        _test = test

    if _test:
        if db_test is not None: return db_test # db_test ya esta instanciada
        client = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_pass}@cluster0.sf15y.mongodb.net/checkout",
                                     tlsAllowInvalidCertificates=True,
                                     retryWrites=True,
                                     w="majority")
        db_test = client.checkout
        return db_test

    if db_prod is not None: return db_prod  # db_prod ya esta instanciada
    client = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_pass}@cluster0.sf15y.mongodb.net/sportclub_prod",
                                 tlsAllowInvalidCertificates=True,
                                 retryWrites=True,
                                 w="majority")
    db_prod = client.sportclub_prod
    return db_prod


def init_mercadopago(token: str = None) -> mercadopago.SDK:
    """ Inicializar la sdk de mercadopago. Si no recibe ningun parametro\
        inicializa la sdk segun la variable de entorno test. 
    
    Es posible inicializar una sdk de produccion y otra de test al mismo tiempo de la siguiente manera:
        
        >>> sdk_prod = init_mercadopago(False)
        >>> sdk_test = init_mercadopago(True)

    :param token: access token para acceder a la sdk de mercadopago, defaults to None
    :type _test: str, optional
    :return: sdk de mercadopago
    :rtype: mercadopago.SDK
    """
    global sdk_prod
    global sdk_test
    if token is None:
        if sdk_test is not None:
            return sdk_test # sdk_test ya esta instanciada
        access_token_test = os.getenv("MP_ACCESS_TOKEN_TEST")
        sdk_test = mercadopago.SDK(access_token_test)
        return sdk_test
    
    if sdk_prod is not None:
        return sdk_prod # sdk_prod ya esta instanciada
    sdk_prod = mercadopago.SDK(token)
    return sdk_prod


def init_mongo_CR20():
    """ Inicializar la base de mongo de test - CR20.

    :return: base de mongo
    :rtype: Database
    """
    client = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_pass}@cluster0.sf15y.mongodb.net/CR20_test",
                                 tlsAllowInvalidCertificates=True,
                                 retryWrites=True,
                                 w="majority")
    db_test = client.CR20_test
    return db_test

