from .init_creds import init_mongo
from bson import ObjectId

db_test = init_mongo(True)
db = init_mongo(False)


def update_socios():
    for socio in db_test.clientes.find():
        active_plan = db_test.planes.find_one({"slug": socio["active_plan"]})
        corporativo = db_test.corporativo.find_one({"slug": socio["plan_corporativo"]})
        settings = {"active_plan": ObjectId(active_plan["_id"] if active_plan else None),
                    "plan_corporativo": ObjectId(corporativo["_id"]) if corporativo else None}
        db_test.clientes.update_one({"_id": socio["_id"]}, {"$set": settings})
        print(socio["cod_client"])


def replicate_db(collection):
    '''
    Replica la base de datos de producción en la base de TEST
       :param str: collection a replicar
       :return: None
       :rtype: None
       '''
    db_test[collection].drop()
    print(collection, "was dropped form dbt")

    print("updating", collection)
    full = db[collection].find({})
    db_test[collection].insert_many(full)


def add_planid():
    for s in db.clientes.find({}):
        plan = db.planes.find_one({"slug": s["active_plan"]})
        db.clientes.update_one({"documento": s["documento"]}, {"$set": {"active_plan_id": plan["_id"]}})


def add_merchants():
    #for c in db.club.find({"asociacion": "SportClub"}):
    db.planes.update_many({"nivel_de_acceso": "Full"}, {"$set": {"merchant_id": ObjectId("617aafd1153d78a8f368dcd5")}})


def move_collection(collection):
    full = db_test[collection].find({})
    db[collection].insert_many(full)

