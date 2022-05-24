class BaseEsDSL(object):
    """
    将条件转换成dsl语句
    """

    def __init__(self):
        self.size = 10000
        self.dsl = {}
        # 字段列表
        self.source = []

    def set_size(self, size):
        """
        设置返回大小一般为10000
        :param size:
        :return:
        """
        self.size = size
        return self

    def set_source(self, source):
        """
        字段列表
        例如 ["keyid", "lngid", "title", "author", "pub_year", "source_type"]
        :param source:
        :return:
        """
        self.source = source

    def term(self, key, values, is_keyword=True):
        if is_keyword:
            key = key + ".keyword"
        return {"term": {key, values}}

    def terms(self, key, lists: list):
        """
        terms：查询某个字段里含有多个关键词的文档
        :param key:
        :param lists:
        :return:
        """
        return {"terms": {key: lists}}

    def match(self, key, values, is_fuzziness=True):
        """
        注意 match 和 match_phrase 之间的关系是should
        :param key:
        :param values:
        :param is_fuzziness:
        :return:
        """
        if is_fuzziness:
            values = {"query": values, "fuzziness": "1"}
        return {"match": {key, values}}

    def match_phrase(self, key, values):
        """
         注意 match 和 match_phrase 之间的关系是should
        :return:
        """
        return {"match_phrase": {key, values}}

    def range(self, key, dicts):
        """
        key 比如 pub_year
        传入一个字典 {"gte": "2011", "lte": "2021"}
        :param key:
        :param dicts:
        :return:
        """
        return {"range": {key: dicts}}

    def get_must(self):
        """
        获取一个must的结构
        :return:
        """
        return {"bool": {"must": []}}

    def set_query(self, dicts):
        self.dsl["query"] = dicts

    def build(self):
        self.dsl["size"] = self.size
        self.dsl["_source"] = self.source
        self.set_query(self.get_must())
