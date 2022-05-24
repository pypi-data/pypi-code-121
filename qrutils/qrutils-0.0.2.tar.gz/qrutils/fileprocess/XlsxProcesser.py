import pandas as pd
import xlsxwriter
from tqdm import tqdm
from typing import List, Dict



def read_xlsx_as_list(read_file: str, need_title=False) -> List[List]:
    print("-----开始读取xlsx-----")
    all_datas = []
    df = pd.read_excel(read_file)
    titles = df.columns.tolist()
    length = len(df)
    for row in tqdm(range(length)):
        all_datas.append(df.iloc[row].values.tolist())
    if need_title:
        return titles, all_datas
    else:
        return all_datas


def read_xlsx_as_dict(read_file: str) -> List[Dict]:
    print("-----开始读取xlsx-----")
    all_datas = []
    df = pd.read_excel(read_file)
    titles = df.columns.tolist()
    length = len(df)
    for row in tqdm(range(length)):
        tmp_dic = {}
        datas = df.iloc[row]
        for index, data in enumerate(datas):
            tmp_dic[titles[index]] = data
        all_datas.append(tmp_dic)
    return all_datas


def write_xlsx_from_list(titles: List[str], datas: List[List[str]], save_file: str) -> None:
    tqdm.write("-----开始写入xlsx-----")
    wb = xlsxwriter.Workbook(save_file)
    ws = wb.add_worksheet()
    for pos, title in enumerate(titles):
        ws.write(0, pos, title)
    for row, data in enumerate(datas):
        for col, dat in enumerate(data):
            ws.write(row+1, col, dat)
    wb.close()


def write_xlsx_from_dict(datas: List[Dict], save_file: str) -> None:
    tqdm.write("-----开始写入xlsx-----")
    wb = xlsxwriter.Workbook(save_file)
    ws = wb.add_worksheet()
    titles = datas[0].keys()
    for pos, title in enumerate(titles):
        ws.write(0, pos, title)
    for row, data in enumerate(datas):
        for col, item in enumerate(data.items()):
            ws.write(row+1, col, item[1])
    wb.close()
