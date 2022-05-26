from datetime import datetime
from pprint import pprint

import bson

from .init_creds import init_mongo
from .dates import set_next_vigency, calculate_payment_date, get_periodo, localize, DIAS_ANTICIPO_DE_PAGO, today_argentina
from .format import datetime_parser
from .mercadopago_ops import get_payments_from_user_id
from dateutil.relativedelta import *
import mercadopago
from bson import ObjectId


def get_client_price(client: dict, plan_price: int, corpo_discount: float, sum_access=True) -> dict:
    """ Obtener el precio a pagar

    :param client: cliente con la estructura que se usa en mongodb
    :type client: dict
    :param plan: precio del plan nativo
    :type plan: int
    :param plan: porcentaje de descuento del plan corporativo
    :type plan: float
    :return: informacion del precio
    :rtype: dict
    """    

    prices = {"native_plan": plan_price}
    if corpo_discount:
        prices["corpo_discount"] = - plan_price * corpo_discount / 100

    if "discounts" in client.keys():
        if client["discounts"]:
            try:
                for discount in [i for i in client["discounts"] if i["aplicaciones_restantes"] > 0]:
                    if "concepto" in discount.keys():
                        concepto = discount["concepto"]
                    else:
                        concepto = "n/a"
                    prices["Descuento " + concepto] = - (plan_price * discount["porcentaje"]) /100 - discount["monto_absoluto"]
            except:
                print(f"    ERROR en el cálculo de descuentos - se retorna un diccionario de precios vacío.")
                return {}

    subtotal = max(0, sum(prices.values()))

    if sum_access:
        accesos = get_access_amount(client["_id"])
        prices["access"] = accesos
    else:
        accesos = 0

    prices["final_price"] = subtotal + accesos
    print(f"    El monto a cobrar es de ${prices['final_price']}")
    return prices


def get_access_amount(c_id: bson.ObjectId) -> int:
    """ Obtener monto de acceso

    :param c_id: id del socio
    :type c_id: bson.ObjectId
    :return: Monto de acceso
    :rtype: int
    """
    db = init_mongo()
    last_payment = [p["date_created"] for p in db.boletas.find({"member_id": c_id})]
    if last_payment:
        last_payment_date = max(last_payment)
    else:
        last_payment_date = datetime(year=2000, month=1, day=1)
    uses = db.accesos.find({"socio_id": c_id, "fecha": {"$gt": last_payment_date}, "costo": {"$gt": 0}})
    result = sum([a["costo"] for a in uses])
    print(f"    El monto de accesos a cobrar es de {result} acumulados desde {last_payment_date}.")
    return result


def substract_discounts(client: dict):
    """ Descontar aplicaciones de descuento

    :param client: cliente con la estructura que se usa en mongodb
    :type client: dict
    """        
    if client["discounts"]:
        for discount in client["discounts"]:
            if discount["aplicaciones_restantes"] > 0:
                discount["aplicaciones_restantes"] -= 1
                print("    se descuenta una aplicacion restante de descuento.")


############
# PAYMENTS #
############

def resolve_payment(payment_data: dict, card_data: dict, _client: dict, _plan: dict, sdk: mercadopago.SDK) -> dict:
    """ Resolver pago si es posible

    :param payment_data: informacion del pago
    :type payment_data: dict
    :param card_data: informacion de la tarjeta
    :type card_data: dict
    :param _client: informacion del cliente
    :type _client: dict
    :param _plan: informacion del plan
    :type _plan: dict
    :param sdk: sdk de mercadopago
    :type sdk: mercadopago.SDK
    :return: informacion con el resultado del proceso
    :rtype: dict
    """

    if _client["preferred_payment_method"] == "efectivo":
        payment_result = {
            "prev_status": "pending",
            "status": "pending_efectivo"
        }
        return payment_result

    if not payment_data["charges_detail"]:
        return {"status": "error",
                "status_detail": "Error al calcular el precio del cliente.",
                "prev_status": payment_data["status"],
                "date_created": today_argentina()}

    if payment_data["charges_detail"]["final_price"] > 0:
        if card_data["card_id"] is None:
            print("    Tarjeta no encontrada. No se puede procesar el pago.")
            payment_result = {"status": "error",
                              "status_detail": "No se puede obtener la tarjeta activa.",
                              "prev_status": payment_data["status"],
                              "date_created": today_argentina()}
        else:
            print("    Se procede a realizar un pago de $" + str(payment_data["charges_detail"]["final_price"]))

            payment_result = process_payment(payment_data, card_data, _client, _plan, sdk)

    else:
        print("    Pago no realizado por ser precio 0.")
        payment_result = {
            "status": "approved",
            "status_detail": "Pago no realizado por ser precio 0.",
            "id": 11,
            "prev_status": payment_data["status"],
            "date_created": today_argentina()
        }
    return payment_result


def process_payment(payment_data: dict, card_data: dict, _client: dict, _plan: dict, sdk: mercadopago.SDK) -> dict:
    """ Procesar pago

    :param payment_data: informacion del pago
    :type payment_data: dict
    :param card_data: informacion de la tarjeta
    :type card_data: dict
    :param _client: informacion del cliente
    :type _client: dict
    :param _plan: informacion
    :type _plan: dict
    :param sdk: sdk de mercadopago
    :type sdk: mercadopago.SDK
    :return: informacion con el resultado del proceso
    :rtype: dict
    """
        
    print("    Se procede a realizar el pago con MP")
    data = {"card_id": int(card_data["card_id"])}
    card_token_response = sdk.card_token().create(data)

    if card_token_response["status"] > 299:
        print("         Falló la creación de token de tarjeta.")
        print(card_token_response["response"])
        return {"status": "error",
                "status_detail": "Falló la creación de token de la tarjeta.",
                "response": card_token_response["response"]["message"],
                "prev_status": payment_data["status"],
                "date_created": today_argentina()
                }

    card_token = card_token_response["response"]["id"]
    print(f"        Token generado OK")
    
    if "tries" in payment_data.keys():
        n_try = len(payment_data["tries"]) + 1
        numero_intento = "Reintento " + str(n_try)
    else:
        numero_intento = "Primer intento"
    
    mp_payment_data = {
        "additional_info": {
            "items": [{
                "title": f'{_plan["name"]} - {_client["nombre"]} {_client["apellido"]} - {_client["email"]} -' 
                         f'{payment_data["period"]}',
                "category_id": _plan["nivel_de_acceso"],
                "description": numero_intento +"- id: " + f'{_client["_id"]}'
            }]
        },
        "notification_url": f"https://apisportclub.xyz/notificacion/mp"
                            f"?source_news=webhooks&merchant={str(_plan['merchant_id'])}",
        "transaction_amount": round(payment_data["charges_detail"]["final_price"], 2),
        "token": card_token,  # ??
        "description": _plan["name"],  # ir a base de datos de planes y traer el name
        "installments": 1,  # ??
        "payer": {
            "id": _client["mercadopago_id"]
        },
        "external_reference": str(payment_data["_id"])
    }
    payment_attempt = sdk.payment().create(mp_payment_data)
    payment_response = datetime_parser(payment_attempt["response"])

    print("         El estado del pago es :" + str(payment_response["status"]))

    # si hay algun error en el pago
    if payment_attempt["status"] >= 299:
        print(payment_response)
        try:
            detail = payment_response["message"]
        except KeyError:
            detail = "Falló el intento de pago."
        return {
            "status": "error",
            "status_detail": detail,
            "response": payment_attempt["response"],
            "prev_status": payment_data["status"],
            "date_created": today_argentina()
        }

    # si el pago es 200
    return {
        "status": payment_response["status"],
        "status_detail": payment_response["status_detail"],
        "id": payment_response["id"],
        "prev_status": payment_data["status"],
        "date_created": today_argentina()
    }


def create_payment_data(_client: dict, prices: dict, merchant_id: ObjectId, source: str) -> dict:
    """ Crear data del pago y guardalo en la coleccion de boletas de mongodb

    :param _client: cliente con la estructura que se usa en mongodb
    :type _client: dict
    :param prices: informacion de precios
    :type prices: dict
    :param merchant_id: id del merchant
    :type merchant_id: ObjectId
    :param source: de dónde proviene la boleta - checkout o recurring_charges
    :type source: str
    :return: data que se guardo en la coleccion de boletas
    :rtype: dict
    """
    db = init_mongo()

    if "checkout" in source:
        opd = today_argentina()
        period = get_periodo(opd)
    else:
        opd = _client["next_payment_date"]
        period = get_periodo(opd + relativedelta(days=DIAS_ANTICIPO_DE_PAGO))

    data = {"member_id": _client["_id"],
            "date_created": today_argentina(),
            "original_payment_date": opd,
            "source": source,
            "tries": [],
            "status": "error_not_processed",
            "merchant_id": merchant_id,
            "charges_detail": prices,
            "period": period,
            "plan_id": _client["active_plan_id"]}

    _id = db.boletas.insert_one(data)
    print(f"    Se inserta una nueva boleta de pago con _id: {_id.inserted_id}.")

    return data


def update_payment_data(payment_result: dict, payment_data: dict, card_data: dict):
    """ Actualizar pago. En payment_data se agrega un nuevo intento de pago

    :param payment_result: Resultado del pago
    :type payment_result: dict
    :param payment_data: data del pago que se quiere actualizar
    :type payment_data: dict
    :param card_data: informacion de la tarjeta
    :type card_data: dict
    """
    n_try = len(payment_data["tries"]) + 1

    if not "id" in payment_result.keys():
        payment_result["id"] = 400  # corresponde a un error 400

    intento = {
        "try_number": n_try,
        "payment_day": payment_result["date_created"],
        "payment_type": card_data["card_type"],
        "card_brand": card_data["card_brand"],
        "card_id": card_data["card_id"],
        "status": payment_result["status"],
        "status_detail": payment_result["status_detail"],
        "payment_id": payment_result["id"]
    }
    payment_data["tries"].append(intento)
    payment_data["status"] = payment_result["status"]
    return


def format_card(mp_card: dict) -> dict:
    if set(mp_card.keys()) == {"card_id", "payer_id", "card_type", "card_brand"}:
        return mp_card

    card = dict()
    card["card_id"] = mp_card["id"]
    card["payer_id"] = mp_card["user_id"]
    card["card_type"] = mp_card["payment_method"]["payment_type_id"]
    card["card_brand"] = mp_card["payment_method"]["name"]
    return card


def get_empty_card():
    return {
        "card_id": None,
        "payer_id": None,
        "card_type": None,
        "card_brand": None
    }


def get_cards(client: dict, price: dict):
    if not price:
        print("    No existe precio - se devuelve tarjeta vacía")
        return [get_empty_card()]

    if price["final_price"] == 0:
        print("         Por monto $0 no se busca tarjeta.")
        return [get_empty_card()]

    if "cards" not in client.keys() or not client["cards"]:
        print("         Cliente sin atributo 'cards'.")
        return [get_empty_card()]

    cards = []
    active_card = client['active_card'] if 'active_card' in client else None

    for card in client['cards']:
        formatted_card = format_card(card)
        if formatted_card['card_id'] == active_card:
            cards.insert(0, formatted_card)
        else:
            cards.append(formatted_card)

    return cards


def get_active_card(_client: dict, price: dict, sdk: mercadopago.SDK):
    """ Obtener la tarjeta activa (con la que se realizan los pagos)

    :param _client: Cliente con la estructura que se usa en mongodb
    :type _client: dict
    :param price: Precio que se quiere cobrar. Si es 0 no se busca la tarjeta
    :type price: dict
    :param sdk: sdk de mercado pago
    :type sdk: mercadopago.SDK
    :return: data de la tarjeta
    :rtype: dict
    """

    card = {"card_id": None,
            "payer_id": None,
            "card_type": None,
            "card_brand": None}
    if not price:
        print("    No existe precio - se devuelve tarjeta vacía")
        return card

    if price["final_price"] == 0:
        print("         Por monto $0 no se busca tarjeta.")
        return card

    if "cards" in _client.keys():
        if _client["cards"]:
            try:
                card_complete = next((item for item in _client["cards"] if item["id"] == _client["active_card"]), card)
                if card_complete["id"]:
                    card = card_complete
                else:
                    card = _client["cards"][0]
                print("    Se obtiene tarjeta correctamente.")
                return {"card_id": card["id"],
                        "payer_id": card["customer_id"],
                        "card_type": card["payment_method"]["payment_type_id"],
                        "card_brand": card["payment_method"]["name"]}
            except:
                print("         ERROR: No se puede obtener la tarjeta del cliente.")
                return card
        else:
            print("         Cliente sin atributo 'cards'.")

    if not card["card_id"] and "active_card" in _client.keys() and "mercadopago_id" in _client.keys():
        mp_card_data = sdk.card().get(_client["mercadopago_id"], _client["active_card"])
        if mp_card_data["status"] == 200:
            mp_card_data = mp_card_data["response"]
            card["card_id"] = mp_card_data["id"]
            card["payer_id"] = mp_card_data["user_id"]
            card["card_type"] = mp_card_data["payment_method"]["payment_type_id"]
            card["card_brand"] = mp_card_data["payment_method"]["name"]
            print("         Se reconstruyó tarjeta a partir de MP exitosamente.")
        elif "active_card" in _client.keys():
            card["card_id"] = _client["active_card"]

    return card


def update_client(_client: dict, _payment_result: dict, _plan: dict, period: str):
    """ Actualizar cliente

    :param _client: Cliente con la estructura que se usa en mongodb
    :type _client: dict
    :param _payment_result: Data del resultado del pago
    :type _payment_result: dict
    :param _plan: Plan con la estructura que se usa en mongodb
    :type _plan: dict
    :param period: periodo de la última boleta generada
    :type period: str
    """
    # si el pago tiene id_mp se los agrego al cliente
    if "id" in _payment_result.keys():
        print("         Se inserta payment id en el cliente.")
        _client["payment_ids"].insert(0, _payment_result["id"])
        _client["last_payment_id"] = _payment_result["id"]

    # actualizaciones de cliente
    _client["lastModified"] = today_argentina()

    if _payment_result["prev_status"] == "error_not_processed":
        _client["next_payment_date"] = calculate_payment_date(_client["period_init_day"], _plan["cobro"], period)
        print("         El próximo dia de cobro es el " + _client["next_payment_date"].strftime("%d/%m/%y"))
        # se resta una aplicacion de descuento
        if "discounts" in _client.keys():
            substract_discounts(_client)

    # updateo de la fecha de vigencia y los cobros recurrentes
    if _payment_result["status"] == "approved":
        _client["cobros_recurrentes"] += 1
        if _client["next_payment_date"]:
            _client["fecha_vigencia"] = set_next_vigency(_client["next_payment_date"])
    else:
        if localize(_client["fecha_vigencia"]) < today_argentina():
            _client["status"] = "inactivo"
            print("         El cliente pasa inactivo por vencer la vigencia")

    return


def restore_pending_payment(user_id, boleta_id):
    """ Actualiza una boleta que quedó en estado 'pending' a su estado real en función del último pago en mercadopago

    :param user_id: id de mongo del usuario
    :type user_id: str
    :param boleta_id: id de mongo de la boleta en estado pendiente
    :type amount: str
    """
    db = init_mongo()
    boleta = db.boletas.find_one({"_id": ObjectId(boleta_id)})
    if boleta["status"] != "error_not_processed":
        print("Boleta no estaba rota")
        return
    client = db.clientes.find_one({"_id": ObjectId(user_id)})
    plan = db.planes.find_one({"_id": client["active_plan_id"]})
    merchant = db.merchants.find_one({"_id": plan["merchant_id"]})
    print(merchant["keys"]["access_token"])
    sdk = mercadopago.SDK(merchant["keys"]["access_token"])
    user_id = client["mercadopago_id"].split('-')[0]
    payment_response = get_payments_from_user_id(user_id, sdk, days=6, limit=1)[-1]

    payment_result = {
        "status": payment_response["status"],
        "status_detail": payment_response["status_detail"],
        "id": payment_response["id"],
        "prev_status": boleta["status"],
        "date_created":  payment_response["date_created"]
    }
    card = {"card_id": payment_response["card"]["id"],
            "payer_id": payment_response["card"]["cardholder"]["identification"]["number"],
            "card_type": payment_response["payment_type_id"],
            "card_brand": payment_response["payment_method_id"]}

    update_payment_data(payment_result, boleta, card)
    db.boletas.update_one({"_id": boleta["_id"]}, {"$set": boleta})

    update_client(client, payment_result, plan, boleta["period"])
    db.clientes.update_one({"_id": client["_id"]}, {"$set": client})


def refund_process(payment_id: str, amount: int, sdk: mercadopago.SDK) -> dict:
    """ Hacer un reembolso

    :param payment_id: id del pago a reembolsar
    :type payment_id: str
    :param amount: monto a reembolsar
    :type amount: int
    :param sdk: sdk de mercadopago
    :type sdk: mercadopago.SDK
    :return: respuesta de mercadopago con informacion del reembolso
    :rtype: dict
    """
    refund_data = {
        "amount": amount
    }
    refund_response = sdk.refund().create(payment_id, refund_data)
    refund = refund_response["response"]
    pprint(refund)
    refund_data = datetime_parser(refund)
    return refund_data


def add_try_to_pending_boleta(boleta: dict, mp_payment: dict) -> None:
    db = init_mongo()
    payment_result = build_payment_result(mp_payment)
    card = get_card_data_from_payment(mp_payment)
    update_payment_data(payment_result, boleta, card)
    db.boletas.update_one({"_id": boleta["_id"]}, {"$set": boleta})


def build_payment_result(mp_payment: dict) -> dict:
    pr = {
        "status": mp_payment["status"],
        "status_detail": mp_payment["status_detail"],
        "prev_status": "error_not_processed",
        "id": mp_payment["id"],
        "date_created": mp_payment["date_created"]
    }
    return datetime_parser(pr)


def get_card_data_from_payment(mp_payment: dict) -> dict:
    return {
            "card_id": mp_payment["card"]["id"],
            "payer_id": mp_payment["payer"]["id"],
            "card_type": mp_payment["payment_type_id"],
            "card_brand": mp_payment["payment_method_id"]
            }


def get_other_cards(_client, card_data):

    active_card_id = card_data["card_id"]
    cards_list = []
    for card in _client["cards"]:
        if "id" in card.keys():
            if card["id"]:
                if active_card_id == card["id"]:
                    continue
                else:
                    card_data = {"card_id": card["id"],
                        "payer_id": card["customer_id"],
                        "card_type": card["payment_method"]["payment_type_id"],
                        "card_brand": card["payment_method"]["name"]
                    }
                    cards_list.append(card_data)
    return cards_list