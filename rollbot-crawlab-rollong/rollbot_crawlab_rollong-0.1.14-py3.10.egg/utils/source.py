import datetime

from rollbot_crawlab.db.mongo import get_col


def get_block(identify):
    block_col = get_col("blocks")
    block = block_col.find_one({"identification": identify})
    if block is None:
        raise Exception("获取block信息失败：{}".format(identify))
    return block


def get_source_verify(url, block):
    col = get_col("sources")
    source = col.find_one({"url": url})
    if source is None \
            or 'enabled' not in source \
            or source['enabled'] is False \
            or 'block_id' not in source \
            or 'url' not in source \
            or 'identification' not in source:
        raise Exception("来源已不可用：{}".format(url))
    if source.get("block_id") != block.get("identification"):
        raise Exception("来源和对应block不匹配：{} - {}".format(url, block.get("identification")))
    source["total_count"] = get_source_total(source)
    return source


def get_source_item(url):
    col = get_col("sources")
    source = col.find_one({"url": url})
    return source


def get_source(url):
    block = None
    source = get_source_item(url)
    if source is None \
            or 'enabled' not in source \
            or source['enabled'] is False \
            or 'block_id' not in source \
            or 'url' not in source \
            or 'identification' not in source:
        raise Exception("来源已不可用：{}".format(url))
    block_id = source.get("block_id")
    if block_id:
        block_col = get_col("blocks")
        block = block_col.find_one({"identification": block_id})
    if block is None:
        raise Exception("来源相关block未找到：{} - {}".format(url, block_id))
    source["total_count"] = get_source_total(source)
    return source, block


def update_source_begin(source):
    col = get_col("sources")
    col.update_one({"_id": source["_id"]}, {"$set": {"latest_start_at": datetime.datetime.now()}})


def update_source_error(source, err_msg):
    if source:
        col = get_col("sources")
        col.update_one({"_id": source["_id"]}, {"$set": {"err_msg": err_msg}})
    raise Exception(err_msg)


def get_source_total(source):
    col = get_col()
    where = {"source_id": source["identification"]}
    return col.count(where)


def update_source_latest(source, latest_url):
    col = get_col("sources")
    latest_count = source.get("total_count", 0)
    total_count= get_source_total(source)
    where = {"_id": source["_id"]}

    json_obj = {
        "latest_count": total_count - latest_count,
        "latest_end_at": datetime.datetime.now(),
        "total_count": total_count
    }

    if latest_url:
        json_obj["latest_url"] = latest_url

    update = {
        "$set": json_obj
    }
    col.update_one(where, update)
