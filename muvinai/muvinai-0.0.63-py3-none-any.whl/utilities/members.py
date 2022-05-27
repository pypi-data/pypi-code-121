from datetime import datetime
from .dates import localize
from .init_creds import init_mongo
from .dates import today_argentina

db = init_mongo()


def member_unsubscribe(member, reason, unsubscribe_request=False):
    """ Da de baja un socio modificando los parámetros necesarios

       :param member: objeto de cliente a dar de baja
       :type receiver: dict
       :param reason: motivo de la baja
       :type template: str
       :param unsubscribe_request: es True si el cliente es 'baja' y puede seguir ingresando
       :type unsubscribe_request: bool, optional
       :return: None
       :rtype: None
       """

    history = {
        "subscription_date": member["last_subscription_date"],
        "unsubscribe_date": today_argentina(),
        "unsubscribe_reason": reason,
        "plan": member["active_plan_id"],
        "discounts": member["discounts"]
    }

    status = "inactivo" if not unsubscribe_request else "baja"

    db.clientes.update_one({"_id": member["_id"]},
                           {"$push": {"history": history}, "$set": {"next_payment_date": None, "status": status}})

    db.boletas.update_many({"member_id": member["_id"],
                                        "status": {"$in": ["error", "rejected"]}},
                                        {"$set": {"status": "expired"}})

'''def create_member_from_prospect(prospect):
    if "corporativo" in prospect.keys():
        corpo_id = prospect["corporativo"]
    else:
        corpo_id = None

    new_customer_data = {"domicilio": {"calle": prospect["domicilio"],
                                       "altura": prospect["address2"],
                                       "apto_lote": prospect["aptolote"],
                                       "localidad": prospect["locality"],
                                       "provincia": prospect["state"],
                                       "código postal": prospect["postcode"]},
                         "last_subscription_date": prospect["date_created"],
                         "active_plan_id": prospect["plan_id"],
                         "plan_corporativo": corpo_id,
                         "fecha_vigencia": None if status_cliente == 'pago en proceso' else set_next_vigency(
                             next_payment_date),
                         "cobros_recurrentes": 0,
                         "status": "activo",
                         "payer_id": None,
                         "sportaccess_id": sportaccess_prefix + "-" + customer_data["documento"],
                         "last_payment_id": payment["id"],
                         "discounts": discounts,
                         "period_init_day": today.day,
                         "next_payment_date": next_payment_date
                         }
'''