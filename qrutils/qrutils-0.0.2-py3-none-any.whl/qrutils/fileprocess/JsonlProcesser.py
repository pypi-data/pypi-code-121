import json
from tqdm import tqdm
from typing import List, Dict

def read_json(read_file: str) -> List[Dict]:
    with open(read_file, 'r', encoding='utf8') as f:
        tmp = json.load(f)
    return tmp


def read_datas(read_file):
    print("-----开始读取jsonl-----")
    return_list = []
    with open(read_file, "r", encoding="utf8") as f:
        for line in tqdm(f.readlines()):
            return_list.append(json.loads(line))
    return return_list


def read_datas_with_keys(read_file, spacial_keys):
    print("-----开始读取jsonl-----")
    return_list = []
    with open(read_file, "r", encoding="utf8") as f:
        for line in tqdm(f.readlines()):
            tmp = json.loads(line)
            dic = {}
            for k in spacial_keys:
                dic[k] = tmp[k]
            return_list.append(dic)
    return return_list


def write_jsonl(datas, save_file):
    tqdm.write("-----开始写入jsonl-----")
    with open(save_file, "w", encoding="utf8") as f:
        for data in tqdm(datas):
            f.write(json.dumps(data, ensure_ascii=False))
            f.write("\n")


def modify_keys(source_data: List[Dict], taget_keys: List) -> List[Dict]:
    tqdm.write("-----开始写入jsonl-----")
    return_list = []
    source_keys = list(source_data[0].keys())
    length = len(source_data[0])
    for data in tqdm(source_data):
        tmp_dic = {}
        for pos in range(length):
            tmp_dic[taget_keys[pos]] = data[source_keys[pos]]
        return_list.append(tmp_dic)
    return return_list
