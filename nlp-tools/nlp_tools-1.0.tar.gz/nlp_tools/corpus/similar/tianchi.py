import random
import json
class TianCiAddress2021():
    ## ccks2021 NLP https://tianchi.aliyun.com/competition/entrance/531901
    __corpus_name__ = 'ccks2021_address'

    @classmethod
    def load_data(cls,
                  file_path: str,
                  shuffle: bool = True,
                  data_agument=False):
        """
                {"text_id": "e225b9fd36b8914f42c188fc92e8918f", "query": "河南省巩义市新华路街道办事处桐和街6号钢苑新区3号楼一单元", "candidate": [{"text": "巩义市桐和街", "label": "不匹配"}, {"text": "桐和街依家小店", "label": "不匹配"}, {"text": "桐和街CHANG六LIULIU", "label": "不匹配"}
                """
        data = []
        with open(file_path, 'r', encoding='utf-8') as fread:
            for index, line in enumerate(fread):
                item_json = json.loads(line.strip())

                x1, x2, label = line.strip().split("\t")
                data.append(([x1, x2], str(label)))

        if shuffle:
            random.shuffle(data)
        return data


    def data_agument(self,json):
        pass
