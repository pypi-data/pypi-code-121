import os,json

class CLUENERGlobalPointerLoader(object):
    @classmethod
    def load_data(cls,
                  subset_name: str = 'train',
                  corpus_path=None):
        '''
        传入格式：
                {"text": "吴三桂演义》小说的想像，说是为牛金星所毒杀。……在小说中加插一些历史背景，", "label": {"book": {"吴三桂演义》": [[0, 5]]}, "name": {"牛金星": [[15, 17]]}}}
                {"text": "看来各支一二流的国家队也开始走出欧洲杯后低迷，从本期对阵情况看，似乎冷门度也不太高，你认为呢？", "label": {"organization": {"欧洲杯": [[16, 18]]}}}
        输入格式：
        data [
           ('吴三桂演义》小说的想像，说是为牛金星所毒杀。……在小说中加插一些历史背景', [   [0, 5,'book'],  [15, 17,'name'] ]),
            ('看来各支一二流的国家队也开始走出欧洲杯后低迷，从本期对阵情况看，似乎冷门度也不太高，你认为呢？',[   [16, 18,'organization']]),
        ]
        '''
        assert subset_name in ['train','test','dev']
        file_path = os.path.join(corpus_path,subset_name+".json")
        result = []
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                item = []
                item_json = json.loads(line.strip())
                item.append(item_json['text'])
                sub_label = []
                for k, v in item_json['label'].items():
                    for spans in v.values():
                        for start, end in spans:
                            sub_label.append((start, end, k))
                item.append(sub_label)
                result.append(item)

        return result

if __name__ == '__main__':
    cluenew_data_path = '/home/qiufengfeng/nlp/nlp_data/ner/cluener'
    print(CLUENERGlobalPointerLoader.load_data(corpus_path=cluenew_data_path))
