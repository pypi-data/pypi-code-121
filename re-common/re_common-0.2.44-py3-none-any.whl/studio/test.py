def test_sq():
    from re_common.baselibrary.utils.basepymongo import BasePyMongo
    # basemongo = BasePyMongo("mongodb://sdbadmin:sdbadmin@192.168.72.86:11817/test2?authMechanism=SCRAM-SHA-1")
    # basemongo = BasePyMongo(
    #     "mongodb://sdbadmin:sdbadmin@192.168.72.86:11817/dataware_house.base_obj_meta_a")
    basemongo = BasePyMongo(
        "mongodb://sdbadmin:sdbadmin@192.168.72.86:11817/test2.test?authMechanism=SCRAM-SHA-1")

    basemongo.use_db("test2")
    # basemongo.auth("sdbadmin", "sdbadmin", "SCRAM-SHA-1")
    basemongo.create_col("test")
    # for items in basemongo.find({}):
    #     print(items["user"])
    items = basemongo.find()
    for item in items:
        ids = item["id"]
        print(ids)

test_sq()