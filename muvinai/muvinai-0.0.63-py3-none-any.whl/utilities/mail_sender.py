import mailchimp_transactional as MailchimpTransactional
from .init_creds import mailchimp_key, test
from mailchimp_transactional.api_client import ApiClientError
import iso8601
import typing
from .dates import today_argentina
from .init_creds import init_mongo

mailchimp = MailchimpTransactional.Client(mailchimp_key)


def send_mail_to_template(receiver: dict, template: str, owner, plan_name: str = "None") -> dict:
    """ Enviar mail con un template determinado

    :param receiver: objeto de cliente del destinatario
    :type receiver: dict
    :param template: nombre del template
    :type template: str
    :param plan: nombre del plan, defaults to "None"
    :type plan: str, optional
    :return: informacion del mail
    :rtype: dict
    """
    try:
        sdate = receiver["last_subscription_date"].strftime("%d/%m/%Y")

    except AttributeError:
        sdate = iso8601.parse_date(receiver["last_subscription_date"]).strftime("%d/%m/%Y")
    except:
        return {}

    global_vars = [{"name": "nombre", "content": receiver["nombre"]},
                   {"name": "apellido", "content": receiver["apellido"]},
                   {"name": "documento", "content": receiver["documento"]},
                   {"name": "plan", "content": plan_name},
                   {"name": "fecha_subscripcion", "content": sdate}
                   ]
    if owner["brand_name"] != "SportClub":
        global_vars.extend([
            {"name": "logo", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])
    send_mail(receiver["email"], global_vars, template, owner)


def send_alert(reciever_mail: str, proceso: str, mensaje: str, referencia: str, test_mail="matias@muvinai.com") -> typing.Union[dict, None]:
    """ Enviar mensaje de alerta a ignacio@muvinai.com
    :param reciever_mail: email de quien recibe la alerta
    :type reciever_mail: str
    :param proceso: nombre del proceso
    :type proceso: str
    :param mensaje: mensaje
    :type mensaje: str
    :param referencia: referencia
    :type referencia: str
    :return: Respuesta de mailchimp o None en caso de error
    :rtype: dict | None
    """

    global_vars = [{"name": "proceso", "content": proceso},
                   {"name": "mensaje", "content": mensaje},
                   {"name": "referencia", "content": referencia}
                   ]
    owner = {"mail_sender_address": "no-responder@sportclub.com.ar",
            "mail_sender_name": "SportClub"}
    return send_mail(reciever_mail, global_vars, "alertas", owner, test_mail)


def send_mail_inactivo(receiver, owner):
    """ Enviar mail indicando al cliente que está inactivo.

        :param receiver: documento de cliente del destinatario
        :type receiver: dict
        :return: informacion del mail
        :rtype: dict
        """

    global_vars = [{"name": "nombre", "content": receiver["nombre"]}]
    if owner["brand_name"] == "SportClub":
        template = "inactivo"
    elif owner["brand_name"] == "Aranceles":
        return
    else:
        template = "inactivo_nosc"
        global_vars.extend([
            {"name": "logo", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])
    return send_mail(receiver["email"], global_vars, template, owner)


def send_mail(receiver_mail, params, template, owner, test_mail="ignacio@muvinai.com"):
    """ Estructura y envía mail

    :param receiver_mail: mail del receptor
    :type receiver_mail: str
    :param params: lista de objetos que son parámetros a pasar al template
    :type params: list
    :param template: nombre del template
    :type template: str
    :param test_mail: mail del receptor en caso de test
    :type receiver_mail: str
    :return: informacion del mail
    :rtype: dict
    """
    print("Enviando mail" + template)

    msg = {
        "from_email": owner["mail_sender_address"],
        "from_name": owner["mail_sender_name"],
        "to": [{"email": test_mail}] if test else [{"email": receiver_mail}],
        "global_merge_vars": params}

    try:
        response = mailchimp.messages.send_template(
            {"template_name": template, "template_content": [], "message": msg})
        print(response)
        return response[0]
    except ApiClientError as error:
        print("An exception occurred: {}".format(error.text))
        return {}


def send_mail_cambio_tarjeta(receiver, owner):
    """ Enviar mail indicando al cliente que debe cambiar la tarjeta.

            :param receiver: documento de cliente del destinatario
            :type receiver: dict
            :return: informacion del mail
            :rtype: dict
            """
    fecha_vigencia = receiver["fecha_vigencia"].strftime("%d/%m/%Y")
    global_vars = [{"name": "nombre", "content": receiver["nombre"]},
                   {"name": "fecha_vigencia", "content": fecha_vigencia}]
    if owner["brand_name"] == "SportClub":
        template = "pago-rechazado"
    elif owner["brand_name"] == "Aranceles":
        return
    else:
        template = "pago-rechazado_nosc"
        global_vars.extend([
            {"name": "logo_mails", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])

    return send_mail(receiver["email"], global_vars, template, owner)


def send_mail_bienvenida(receiver, plan, owner, test_mail="ignacio@muvinai.com"):
    """ Enviar mail de bienvenida a la suscripción.

            :param receiver: documento de cliente del destinatario
            :type receiver: dict
            :return: informacion del mail
            :rtype: dict
            """

    global_vars = [{"name": "nombre", "content": receiver["nombre"]},
                   {"name": "apellido", "content": receiver["apellido"]},
                   {"name": "documento", "content": receiver["documento"]},
                   {"name": "plan", "content": plan["name"]},
                   {"name": "fecha_subscripcion", "content": today_argentina().strftime("%d/%m/%Y")},
                   ]

    if plan["sede_local"]:
        db = init_mongo()
        sede = db.club.find_one({"_id": plan["sede_local"]})
        global_vars.extend([
            {"name": "direccion", "content": sede["direccion"]},
            {"name": "telefono", "content": sede["telefono"]},
            {"name": "contact-mail", "content": sede["contact-email"]}
        ])
        if "instagram" in sede.keys():
            global_vars.append({"name": "instagram", "content": sede["instagram"]})

    if owner["brand_name"] == "SportClub":
        if plan["nivel_de_acceso"] == "Full" or plan["nivel_de_acceso"] == "Flex":
            template = "workclub-bienvenida"
        elif plan["nivel_de_acceso"] == "Local":
            template = "bienvenida-local"
        else:
            template = "bienvenida"
    else:
        template = "bienvenida_nosd"
        global_vars.extend([
            {"name": "logo_mails", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])

    return send_mail(receiver["email"], global_vars, template, owner, test_mail)


def send_mail_exitoso(receiver, plan, owner):
    global_vars = [{"name": "nombre", "content": receiver["nombre"]},
                   {"name": "apellido", "content": receiver["apellido"]},
                   {"name": "plan", "content": plan["name"]},
                   {"name": "fecha_subscripcion", "content": today_argentina().strftime("%d/%m/%Y")}
                   ]

    if owner["brand_name"] == "SportClub":
        template = "exitoso"
    else:
        template = "exitoso_nosc"
        global_vars.extend([
            {"name": "logo_mails", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])

    return send_mail(receiver["email"], global_vars, template, owner)


def send_mail_checkout_rechazado(receiver, owner):
    global_vars = [{"name": "nombre", "content": receiver["nombre"]}]

    if owner["brand_name"] == "SportClub":
        template = "checkout-rechazado"
    else:
        template = "checkout-rechazado_nosc"
        global_vars.extend([
            {"name": "logo_mails", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])

    return send_mail(receiver["email"], global_vars, template, owner)


def send_mail_pago_en_efectivo(receiver, owner):

    """ Estructura y envía mail
    :param receiver_mail: mail del receptor
    :type receiver_mail: str
    :param test_mail: mail del receptor en caso de test
    :type receiver_mail: str
    :return: informacion del mail
    :rtype: dict
    """

    global_vars = [{"name": "nombre", "content": receiver["nombre"]}]
    if owner["brand_name"] == "SportClub":
        template = "nueva_boleta_sc"
    else:
        template = "nueva_boleta_nosc"
        global_vars.extend([
            {"name": "logo", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])
    return send_mail(receiver["email"], global_vars, template, owner)


def send_mail_pago_pendiente(receiver, owner, test_mail="ignacio@muvinai.com"):
    """ Estructura y envía mail
        :param receiver_mail: mail del receptor
        :type receiver_mail: str
        :param test_mail: mail del receptor en caso de test
        :type receiver_mail: str
        :return: informacion del mail
        :rtype: dict
        """

    global_vars = [{"name": "nombre", "content": receiver["nombre"]}]
    if owner["brand_name"] == "SportClub":
        template = "pago-pendiente"
    else:
        template = "pago-pendiente_no_sc"
        global_vars.extend([
            {"name": "logo", "content": owner["mail_logo"]},
            {"name": "brand_name", "content": owner["brand_name"]}
        ])
    return send_mail(receiver["email"], global_vars, template, owner)