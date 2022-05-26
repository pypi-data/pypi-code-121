from rollbot_crawlab.db.mongo import get_col


def get_comment_total(source):
    col = get_col("comments")
    where = {"source_id": source["source_id"]}
    return col.count(where)

