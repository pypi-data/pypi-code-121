from re_common.baselibrary.tools.move_mongo.mongo_table_to_file import Configs, MongoToFile

conf = Configs()


def hook_doc(doc):
    doc_info = doc["step_info"]
    id_ = doc_info["id"]
    url = f"https://wiki.mbalib.com/wiki/{id_}"
    doc_info["url"] = url
    return doc


mtf = MongoToFile(conf)
mtf.hook_doc = hook_doc
mtf.init_conn_mongodb()
mtf.open_file()
mtf.asyncio_run()
