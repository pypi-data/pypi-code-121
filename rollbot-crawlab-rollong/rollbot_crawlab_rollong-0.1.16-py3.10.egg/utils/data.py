from rollbot_crawlab.constants import DedupMethod
from rollbot_crawlab.db.es import index_item
from rollbot_crawlab.db.kafka import send_msg
from rollbot_crawlab.db.mongo import get_col
from rollbot_crawlab.db.sql import get_item, update_item, insert_item
from rollbot_crawlab.utils.config import get_task_id, get_is_dedup, get_dedup_field, get_dedup_method
import datetime


def save_item_mongo(item):
    col = get_col()

    # 赋值task_id
    item['task_id'] = get_task_id()

    # 是否开启去重
    is_dedup = get_is_dedup()

    if is_dedup == '1':
        # 去重
        dedup_field = get_dedup_field()
        dedup_method = get_dedup_method()
        if dedup_method == DedupMethod.OVERWRITE:
            # 覆盖
            if col.find_one({dedup_field: item[dedup_field]}):
                col.replace_one({dedup_field: item[dedup_field]}, item)
            else:
                col.save(item)
        elif dedup_method == DedupMethod.IGNORE:
            # 忽略
            col.save(item)
        else:
            # 其他
            col.save(item)
    else:
        # 不去重
        col.save(item)


def save_item_sql(item):
    # 是否开启去重
    is_dedup = get_is_dedup()

    # 赋值task_id
    item['task_id'] = get_task_id()

    if is_dedup == '1':
        # 去重
        dedup_field = get_dedup_field()
        dedup_method = get_dedup_method()
        if dedup_method == DedupMethod.OVERWRITE:
            # 覆盖
            if get_item(item, dedup_field):
                update_item(item, dedup_field)
            else:
                insert_item(item)
        elif dedup_method == DedupMethod.IGNORE:
            # 忽略
            insert_item(item)
        else:
            # 其他
            insert_item(item)
    else:
        # 不去重
        insert_item(item)


def save_item_kafka(item):
    item['task_id'] = get_task_id()
    send_msg(item)


def save_item_es(item):
    item['task_id'] = get_task_id()
    index_item(item)


def get_post_item(url):
    col = get_col("results_rollbot")
    post_result = col.find_one({"url": url})
    return post_result


# 获取post的评论数量
def get_comment_total_by_post_item(post_item):
    col = get_col("results_comments")
    where = {"post_id": post_item["_id"]}
    return col.count(where)


def update_post_item_comment_latest_id(post_item, comment_latest_id):
    col = get_col("results_rollbot")
    comment_latest_count = post_item.get("comment_total_count", 0)
    comment_total_count = get_comment_total_by_post_item(post_item)
    where = {"_id": post_item["_id"]}

    json_obj = {
        "comment_latest_count": comment_total_count - comment_latest_count,
        "latest_end_at": datetime.datetime.now(),
        "comment_total_count": comment_total_count
    }

    if comment_latest_id:
        json_obj["comment_latest_id"] = comment_latest_id

    update = {
        "$set": json_obj
    }
    col.update_one(where, update)


def update_post_item_error(post, err_msg):
    if post:
        col = get_col("result_rollbot")
        col.update_one({"_id": post["_id"]}, {"$set": {"err_msg": err_msg}})
    raise Exception(err_msg)