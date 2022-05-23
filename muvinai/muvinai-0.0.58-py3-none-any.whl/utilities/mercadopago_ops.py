import bson

from .init_creds import init_mongo

import mercadopago

db = init_mongo()


def get_payment(payment_id, sdk: mercadopago.sdk):
    response = sdk.payment().search(filters={"id": payment_id})
    return response["response"]


def get_merchant_from_payment(payment_id: str):
    """ Obtener el merchant a partir de un pago de mercadopago

          :param payment_id: id del pago
          :type payment_id: str
          :return: el merchant del pago
          :rtype: ObjectId
          """
    for merchant in db.merchants.find({"keys.access_token": {"$exists": True}}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return merchant["_id"]


def get_sdk_from_payment(payment_id: str):
    """ Obtener el sdk a partir de un pago de mercadopago

      :param payment_id: id del pago
      :type payment_id: str
      :return: el sdk ya instanciado de mercadopago
      :rtype: mercadopago.SDK
      """
    for merchant in db.merchants.find({"keys.access_token": {"$exists": True}}):
        try:
            sdk = mercadopago.SDK(merchant["keys"]["access_token"])
        except KeyError:
            continue
        payment = get_payment(payment_id, sdk)
        if "results" in payment.keys():
            if payment["results"]:
                return sdk


def get_payments_from_user_id(mp_id: str, sdk: mercadopago.sdk, days=30, limit=10):
    """ Obtener todos los pagos en los últimos <days> días para un usuario dado un mercadopago_id

          :param mp_id: id del usuario en mercadopago. Sólo los números antes de guión
          :type payment_id: str
          :param sdk: El SDK de mercadopago correspondiente al plan del usuario
          :type sdk: SDK.mercadopago
          :param mp_id: id del usuario en mercadopago. Sólo los números antes de guión
          :type days: int
          :param limit: límite de resultados a obtener
          :type limit: int
          :return: lista de pagos que satisfacen query
          :rtype: list
          """

    if "-" in mp_id:
        mp_id, x = mp_id.split("-")

    payment_info = {"begin_date": f"NOW-{days}DAYS",
                 "end_date": "NOW",
                 "range": "date_created",
                 "sort": "date_created",
                 "limit": limit,
                 "offset": 0,
                 "payer.id": mp_id
                 }

    payments = sdk.payment().search(filters=payment_info)

    return payments["response"]["results"]


def get_sdk_from_user(user_id: bson.ObjectId):
    """ Obtener el SDK de mercadopago a partir de un id de usuario

           :param user_id: id del usuario en mongoDB.
           :type payment_id: bson.ObjectId
           :return: sdk de mercadopago
           :rtype: mercadopago.SDK
           """
    client = db.clientes.find_one({"_id": user_id})
    plan = db.planes.find_one({"_id": client["active_plan_id"]})
    merchant = db.merchants.find_one({"_id": plan["merchant_id"]})
    sdk = mercadopago.SDK(merchant["keys"]["access_token"])
    return sdk


def get_sdk_from_merchant(merchant_id):
    merchant = db.merchants.find_one(bson.ObjectId(merchant_id))
    return mercadopago.SDK(merchant["keys"]["access_token"])
