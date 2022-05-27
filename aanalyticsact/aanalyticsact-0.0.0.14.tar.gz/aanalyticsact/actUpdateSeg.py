# Created by Sunkyeong Lee
# Inquiry : sunkyeong.lee@concentrix.com / sunkyong9768@gmail.com


from copy import deepcopy
import aanalytics2 as api2
import json
from itertools import *
from sqlalchemy import create_engine
import pandas as pd
from .actCreateSeg import *
import time
from ast import literal_eval


def dataInitiator():
    api2.configure()
    logger = api2.Login() 
    logger.connector.config


def updateSegment(segmentID, jsonFile):
    dataInitiator()
    cid = "samsun0"
    ags = api2.Analytics(cid)
    ags.header

    createSeg = ags.updateSegment(segmentID, jsonFile)
    
    return createSeg

def readJson(jsonFile):
    with open(jsonFile, 'r', encoding='UTF8') as bla:
        jsonFile = json.loads(bla.read())

    return jsonFile


def dumpJson(seg_location, seg_id, target):
    string = seg_location + '\\' + str(seg_id) + '-' + time.strftime('%Y%m%d-%H%M%S', time.localtime()) + '.json'
    with open(str(string), 'w', encoding='UTF8') as fileName:
        json.dump(target, fileName, indent="\t")


def idToList(segmentId):
    db_connection_str = 'mysql+pymysql://root:12345@127.0.0.1:3307/segment'
    db_connection = create_engine(db_connection_str, encoding='utf-8')
    conn = db_connection.connect()

    query = """
    SELECT id FROM segment.tb_segment_list as seg
    left join segment.tb_segment_contains as cont
    on seg.name = cont.segment_name
    where segment_contains like '%%{0}%%'
    """.format(segmentId)
    
    result = pd.read_sql_query(query, conn)
    result_to_list = result['id'].values.tolist()
    conn.close()

    return result_to_list

# return 변경한 세그먼트 id 리스트로 반환
def segmentUpdate(old_seg, new_seg, current_segment, segment_archive):
    # old segment의 id를 db의 seg_contains의 테이블에서 조회하여 해당 세그먼트가 포함된 세그 id 반환
    seg_contains = idToList(readJson(old_seg)['id'])

    for i in range(len(seg_contains)):
        # 변경할 세그먼트의 old 버전 archive에 현재 날짜 붙여서 저장
        
        # 1. 파일 읽기
        seg_loc = current_segment + "\\" + seg_contains[i] + '.json'
        segment = readJson(seg_loc)
        segment_copy = deepcopy(segment)
        # archive old seg
        dumpJson(segment_archive, seg_contains[i], readJson(seg_loc))
        
        # 세그먼트 긁어 모으기
        base_seg = str(segment['definition']['container']['pred']['stream'])
        old_seg_json = str(readJson(old_seg)['definition']['container'])
        new_seg_json = str(readJson(new_seg)['definition']['container'])

        # 저장된 세그먼트에 옛날 세그먼트를 새로운 세그먼트로 변경 후
        base_seg_replaced = base_seg.replace(old_seg_json, new_seg_json)
        # json 형식에 변경한 부분 엎어치기
        segment_copy['definition']['container']['pred']['stream'] = list(literal_eval(base_seg_replaced))

        # 원 파일에 저장
        with open(str(seg_loc), 'w', encoding='utf-8') as fileName:
            json.dump(segment_copy, fileName, indent="\t")

    return seg_contains

# Fianl Function
def updateSeg(old_seg, new_seg, current_segment, segment_archive):

    seg_list = segmentUpdate(old_seg, new_seg, current_segment, segment_archive)

    for i in range(len(seg_list)):
        seg_loc = current_segment + "\\" + seg_list[i] + '.json'

        print(updateSegment(seg_list[i], readJson(seg_loc)))
