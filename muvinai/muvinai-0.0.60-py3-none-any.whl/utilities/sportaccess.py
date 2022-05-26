# Crea o modifica usuarios en sportaccess
import requests
import json
from .init_creds import init_mongo, test
from datetime import datetime
from .projections import proj_accesso_cliente
from pymongo import ReturnDocument

db = init_mongo()


zonas = {
    "Elite": "-1",
    "Total": "1",
    "Plus": "2",
    "Local": "7",
    "Flex": "7"
}

sedes = {
    "CORP": "1",
    "ECOM": "900",
    "ALIA": "901",
    "WORK": "1010",
    "MUVI": "900"
}

all_clubes = db.club.find({"sportaccess_id": {"$exists": True}})
sede_map = {c["sportaccess_id"]: c["name"] for c in all_clubes}
additional_map = {
    1: "Corporate",
    900: "e-Commerce",
    901: "Alianzas"
}
sede_map.update(additional_map)


def crear_usuario_sportclub(cliente: dict, payment_id: int, nivel_de_acceso: str) -> dict:
    """ Crear un usuario en la base de datos de Sportclub

    :param cliente: cliente de mongodb
    :type cliente: dict
    :param payment_id: id del pago de mercadopago
    :type payment_id: str
    :param nivel_de_acceso: [description]
    :type nivel_de_acceso: [type]
    :return: los valores posibles son: Elite, Total, Plus, Local, Flex
    :rtype: dict
    """
    db = init_mongo()
    url = "https://apisami.sportclubaccess.com/2.0/socio?"

    try:
        plan = db.planes.find_one({"_id": cliente["active_plan_id"]})
        if plan["sede_local"] is None:
            sede_value = sedes[cliente["sportaccess_id"][0:4]]
        else:
            club = db.club.find_one({"_id": plan["sede_local"]})
            sede_value = club["sportaccess_id"]
    except:
        sede_value = "1"

    for a in cliente["domicilio"]:
        if not a:
            cliente["domicilio"][a] = "n/a"

    if "nacimiento" not in cliente.keys():
        cliente["nacimiento"] = "22/02/2022"
    elif not cliente["nacimiento"] or cliente["nacimiento"] == "n/a":
        cliente["nacimiento"] = "22/02/2022"

    if "celular" not in cliente.keys():
        cliente["celular"] = "n/a"
    elif not cliente["celular"]:
        cliente["celular"] = "n/a"

    parameters = {
        "username": "3rdPty2902-8891-20",
        "password": "HWXSroa76FSI226JeEtOd9SqDoDXCkGtJyXTk2qEAN2HI34bOVe",
        "nro_socio": cliente["sportaccess_id"],
        "nombre": cliente["nombre"],
        "apellido": cliente["apellido"],
        "documento": cliente["documento"],
        "email": cliente["email"],
        "sexo": "X",
        "nacimiento": cliente["nacimiento"].replace("/", "-"),
        "celular": cliente["celular"],
        "calle": cliente["domicilio"]["calle"],
        "numero": cliente["domicilio"]["altura"],
        "localidad": cliente["domicilio"]["localidad"],
        "cp": cliente["domicilio"]["código postal"],
        "ciudad": cliente["domicilio"]["localidad"],
        "provincia": cliente["domicilio"]["provincia"],
        "nacionalidad": "Argentino",
        "sede": sede_value,
        "zona": zonas[nivel_de_acceso],
        "mp_payment_id": int(payment_id),
        "vigencia": cliente["fecha_vigencia"].strftime("%d-%m-%Y")
    }

    lista = [key + "=" + str(parameters[key]) for key in parameters.keys()]
    querystrings = "&".join(lista)
    if test:
        print("Se saltea el post a sportaccess por ser test.")
        return {"status": True, "message": "No se llamó al servicio por ser TEST."}
    r = requests.post(url + querystrings)
    response = r.json()
    if not response["status"]:
        print("Falló la creación de usuario en bd sporclub")
        print(response["message"])
    else:
        print("Usuario creado satisfactoriamente en bd sportclub")

    return response


def consulta_socio(documento: str) -> dict:
    """ Obtener un socio de la base de datos de sportclub
great
    :param documento: numero de documento del socio que buscado
    :type documento: str
    :return: respuesta de SpAccess (puede ser un socio o un mensaje de error)
    :rtype: dict
    """    
    url = "https://apisami.sportclubaccess.com/2.0/members?Documento="
    r = requests.get(url + documento)
    return r.json()
    

def consulta_socio_x_nro_socio(nro_socio: str) -> dict:
    """ Obtener un socio de la base de datos de sportclub

    :param documento: numero de documento del socio que buscado
    :type documento: str
    :return: respuesta de SpAccess (puede ser un socio o un mensaje de error)
    :rtype: dict
    """    
    url = "https://apisami.sportclubaccess.com/2.0/members?NroSocio="
    r = requests.get(url + nro_socio)
    return r.json()


def create_external_user(data: dict) -> dict:
    """ Crear un cliente externo en mongodb

    :param data: datos del socio (estos datos se obtienen de la base de sportclub)
    :type data: dict
    :return: datos del socio con los que se guardo en mongodb
    :rtype: dict
    """

    na = "Elite" if data["Documento"] in strelites else list(zonas.keys())[
        list(zonas.values()).index(str(data["Zona"]))]
    try:
        club_name = sede_map[int(data["Sede-SqlId"])]
    except:
        club_name = "n/a"

    nuevo_socio = {
        "sportaccess_id": data["NroSocio"],
        "nivel_de_acceso": na,
        "nombre": data["Nombre"],
        "apellido": data["Apellido"],
        "documento": data["Documento"],
        "email": data["Mail"],
        "domicilio": {
            "calle": data["Direccion"],
            "altura": data["Numero"],
            "apto_lote": data["Piso"],
            "localidad": data["Localidad"],
            "provincia": data["Provincia"],
            "código postal": data["CPostal"]
        },
        "celular": data["Movil"],
        "status": "externo",
        "fecha_vigencia": datetime.strptime(data["Vigencia"], '%d/%m/%Y'),
        "nacimiento": data["Nacimiento"],
        "last_subscription_date": datetime.strptime(data["FechaIngreso"], '%d/%m/%Y'),
        "sede": club_name
    }
    socio = db.clientes.insert_one(nuevo_socio)
    nuevo_socio["_id"] = socio.inserted_id
    return nuevo_socio


def cambio_de_plan(documento: str):
    """ Actualizar en mongodb y en SpAccess el plan del socio

    :param documento: numero de documento del socio al cual se le quiere cambiar el plan
    :type documento: str
    """    
    db = init_mongo()
    cliente = db.clientes.find_one({"documento": documento})
    cliente["active_plan"] = "total-mensual"
    cliente["nivel_de_acceso"] = "Total"
    crear_usuario_sportclub(cliente, cliente["last_payment_id"], cliente["nivel_de_acceso"])
    db.clientes.update_one({"documento": documento}, {"$set": cliente})


def update_external_user(data: dict):
    """ Actualizar cliente externo

    :param data: datos que se van a actualizar (tienen que estar las keys: Documento, \
                    Zona, NroSocio, Nombre, Apellido, Documento, Mail, Direccion, Numero, Piso, Localidad,\
                    Provincia, CPostal, Movil, Vigencia, Nacimiento, FechaIngreso)
    :type data: dict
    """    
    na = "Elite" if data["Documento"] in strelites else list(zonas.keys())[list(zonas.values()).index(str(data["Zona"]))]

    try:
        club_name = sede_map[int(data["Sede-SqlId"])]
    except:
        club_name = "n/a"

    socio = {
        "sportaccess_id": data["NroSocio"],
        "nivel_de_acceso": na,
        "nombre": data["Nombre"],
        "apellido": data["Apellido"],
        "documento": data["Documento"],
        "email": data["Mail"],
        "domicilio": {
            "calle": data["Direccion"],
            "altura": data["Numero"],
            "apto_lote": data["Piso"],
            "localidad": data["Localidad"],
            "provincia": data["Provincia"],
            "código postal": data["CPostal"]
        },
        "celular": data["Movil"],
        "status": "externo",
        "fecha_vigencia": datetime.strptime(data["Vigencia"], '%d/%m/%Y'),
        "nacimiento": data["Nacimiento"],
        "last_subscription_date": datetime.strptime(data["FechaIngreso"], '%d/%m/%Y'),
        "sede": club_name,
    }
    return db.clientes.find_one_and_update({"documento": data["Documento"]}, {"$set": socio},
                                           projection=proj_accesso_cliente,
                                           return_document=ReturnDocument.AFTER)


strelites = [
"17968603",
"25647644",
"18110621",
"44160654",
"28508245",
"20540023",
"29571882",
"17331567",
"24690984",
"29695864",
"32215977",
"16492982",
"17083952",
"37050158",
"94824571",
"14915216",
"14951519",
"39644268",
"27923183",
"42119189",
"20340280",
"11726199",
"28417781",
"26687480",
"24612588",
"25540482",
"28281063",
"12731772",
"16356582",
"22344506",
"17513343",
"28985800",
"22157614",
"17004744",
"30409905",
"17800734",
"16495297",
"30211271",
"32451066",
"22878693",
"21138738",
"20420715",
"20051366",
"21495716",
"12549464",
"21951202",
"44642281",
"37806138",
"28325919",
"21842834",
"10313318",
"94093103",
"42930040",
"43034077"]
