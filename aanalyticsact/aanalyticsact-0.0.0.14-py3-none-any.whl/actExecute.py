# Created by Sunkyeong Lee
# Inquiry : sunkyeong.lee@concentrix.com / sunkyong9768@gmail.com

from copy import Error
# from actModuler import *
# from actRunner import *
from .actModuler import *
from .actRunner import *
import time


def Retrive_FirstLevel(start_date, end_date, period, jsonLocation, tbColumn, dbTableName, epp, site_code_rs, limit):
    if limit > 1000:
        raise Error("limit은 0 ~ 1000 사이 값으로 넣어주세요")

    dateCaller = dateGenerator(start_date, end_date, period)
    if_site_code = checkSiteCode(readJson(jsonLocation)["dimension"])
    
    tbColumn = tbColumnGenerator(tbColumn, if_site_code, False, False, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    for i in range(len(startDate)):
        while True:
            try:
                start = time.time()
                jsonToDb(startDate[i], endDate[i], period, jsonLocation, tbColumn, dbTableName, epp, if_site_code, site_code_rs, limit)
                timeSec = round(time.time() - start, 2)
                print("Time took: ", timeSec, "sec")
  
            except KeyError:
                print("Server Error Occurred")
                continue

            except IndexError:
                print("Index Error")
                continue
            
            break

def Retrive_SecondLevel(start_date, end_date, period, jsonLocation, jsonLocation_breakdown,tbColumn, dbTableName, epp, limit):
    dateCaller = dateGenerator(start_date, end_date, period)
    if_site_code = checkSiteCode(readJson(jsonLocation)["dimension"])

    if returnRsID(jsonLocation) == "sssamsungnewus":
        if_site_code = True

    site_code_rs = False
    tbColumn = tbColumnGenerator(tbColumn, if_site_code, True, False, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    for i in range(len(startDate)):
        while True:
            try:
                start = time.time()
                StackbreakValue(startDate[i], endDate[i], period, jsonLocation, jsonLocation_breakdown, tbColumn, dbTableName, epp, limit)
                timeSec = round(time.time() - start, 2)
                print("Time took: ", timeSec, "sec")

            except KeyError:
                print("Server Error Occurred")
                continue

            except IndexError:
                print("Index Error")
                continue
            
            break

def Retrive_by_RS(start_date, end_date, period, jsonLocation, rsInput, tbColumn, dbTableName, epp):
    dateCaller = dateGenerator(start_date, end_date, period)
    site_code_rs = False
    tbColumn = tbColumnGenerator(tbColumn, False, False, True, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for i in range(len(startDate)):
        for j in range(len(rsList)):
            try:
                sample = refineRsIDChange(startDate[i], endDate[i], jsonLocation, rsList[j], period, tbColumn, epp)

            except KeyError:
                print("Server Error Occurred")
                continue

            except IndexError:
                print("Index Error")
                continue

            stackTodb(sample, dbTableName)

## 22.04.30 added
def Retrive_by_RS_breakdown(start_date, end_date, period, jsonLocation, jsonLocation_breakdown, rsInput, tbColumn, dbTableName, epp, limit):
    dateCaller = dateGenerator(start_date, end_date, period)
    # site_code_rs = False
    # tbColumn = tbColumnGenerator(tbColumn, False, True, True, site_code_rs)
    tbColumn = ["rs_name", "dimension", "breakdown", "period", "start_date", "end_date", "is_epp", "is_epp_integ"]
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for i in range(len(startDate)):
        for j in range(len(rsList)):
            try:
                sample = refineRsIDChange_breakdown(startDate[i], endDate[i], jsonLocation, jsonLocation_breakdown, rsList[j], period, tbColumn, epp, limit)

            except KeyError:
                print("Server Error Occurred")
                continue

            except IndexError:
                print("Index Error")
                continue

            stackTodb(sample, dbTableName)


