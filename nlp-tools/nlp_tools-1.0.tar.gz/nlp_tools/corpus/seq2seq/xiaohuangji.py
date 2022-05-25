import re
from nlp_tools import utils
from nlp_tools.utils.text_clean import _regular_
from typing import Tuple, List
import logging
def _good_line_(line):
    """
    判断一句话是否是好的语料,即判断
    :param line:
    :return:
    """
    if len(line) == 0:
        return False
    ch_count = 0
    for c in line:
        # 中文字符范围
        if '\u4e00' <= c <= '\u9fff':
            ch_count += 1
    if ch_count / float(len(line)) >= 0.8 and len(re.findall(r'[a-zA-Z0-9]', ''.join(line))) < 3 \
            and len(re.findall(r'[ˇˊˋˍεπのゞェーω]', ''.join(line))) < 3:
        return True
    return False


class XiaoHuangJi(object):
    __corpus_name__ = 'xiao_huang_ji'

    @classmethod
    def load_data(cls,
                  file_path: str ,
                  shuffle: bool = True) -> Tuple[List[List[str]], List[List[str]]]:
        """
                Load dataset as sequence labeling format, char level tokenized

                features: ``[['海', '钓', '比', '赛', '地', '点', '在', '厦', '门', ...], ...]``

                labels: ``[[海', '钓', '比', '赛', '地', '点', , ...], ...]``

                Args:
                    file_path: file ablsute path
                    shuffle: should shuffle or not, default True.

                Returns:
                    dataset_features and dataset labels
                """
        x_data = []
        y_data = []
        q = None
        with open(file_path, 'r', encoding='utf-8') as fr:
            for line in fr:
                if line.startswith('M '):
                    if q is None:
                        q = _regular_(line[2:-1])
                    else:
                        a = _regular_(line[2:-1])
                        if _good_line_(q) and _good_line_(a):
                            x_data.append(list(q))
                            y_data.append(list(a))
                        q = None

        if shuffle:
            x_data, y_data = utils.unison_shuffled_copies(x_data, y_data)
        logging.debug(f"loaded {len(x_data)} samples from {file_path}. Sample:\n"
                      f"x[0]: {x_data[0]}\n"
                      f"y[0]: {y_data[0]}")
        return x_data, y_data

if __name__ == '__main__':
    file_path = r'F:\nlp-data\chat\xiaohuangji50w_nofenci.conv'
    x,y = XiaoHuangJi.load_data(file_path)
    print(x[0])
    print(y[0])