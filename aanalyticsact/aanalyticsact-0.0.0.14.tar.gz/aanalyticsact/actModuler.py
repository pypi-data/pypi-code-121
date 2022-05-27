# Created by Sunkyeong Lee
# Inquiry : sunkyeong.lee@concentrix.com / sunkyong9768@gmail.com

import aanalytics2 as api2
import json
from datetime import datetime, timedelta
from copy import deepcopy
from sqlalchemy import create_engine


# initator
def dataInitiator():
    api2.configure()
    logger = api2.Login()
    logger.connector.config

def dataReportSuites():
    cid = "samsun0"
    ags = api2.Analytics(cid)
    ags.header
    rsids = ags.getReportSuites()
    print(rsids)


# data retriving function
def dataRetriver_data(jsonFile):
    cid = "samsun0"
    ags = api2.Analytics(cid)
    ags.header
    myreport = ags.getReport(jsonFile)
    return myreport['data']


def dataRetriver_data_breakdown(jsonFile):
    cid = "samsun0"
    ags = api2.Analytics(cid)
    ags.header
    myreport1 = ags.getReport(jsonFile, item_id=True)
    data_report = myreport1['data']

    return data_report


def exportToCSV(dataSet, fileName):
    dataSet.to_csv(fileName, sep=',', index=False)


def returnRsID(jsonFile):
    with open(jsonFile, 'r') as bla:
        json_data = json.loads(bla.read())
    rsID = json_data['rsid']

    return rsID


def EndDateCalculation(startDate, endDate):
    startDate = str(startDate)
    endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
    endDate += timedelta(days=1)
    endDate = str(endDate)

    return startDate, endDate


def jsonDateChange(startDate, endDate, jsonFile):
    date = EndDateCalculation(startDate, endDate)
    startDate = date[0]
    endDate = date[1]

    with open(jsonFile, 'r') as bla:
        json_data = json.loads(bla.read())

    globalFilterElement = json_data['globalFilters']

    for i in range(len(globalFilterElement)):
        jsonDate = globalFilterElement[i]

    tobeDate = str(startDate + "T00:00:00.000/" + endDate + "T00:00:00.000")
    jsonDate['dateRange'] = tobeDate

    for i in range(len(globalFilterElement)):
        globalFilterElement[i] = jsonDate

    json_data['globalFilters'] = globalFilterElement
    
    return json_data

def convertToList(dataSet):
    place = []
    for i in range(len(dataSet)):
        place.append(dataSet[i])

    return place


def addStartEndDateColumn(startDate, endDate, rowNum):
    startDateList = []
    endDateList = []

    for i in range(rowNum):
        startDateList.append(startDate)
        endDateList.append(endDate)

    return startDateList, endDateList

def checkSiteCode(dimension):
    if (dimension == "variables/prop1" or dimension == "variables/evar1" or dimension == "variables/entryprop1"):
        return True

    else:
        return False

# 1st Level data Caller
def refinedFrame(startDate, endDate, period, jsonFile, epp, if_site_code, site_code_rs):
    dataInitiator()
    dateChange = jsonDateChange(startDate, endDate, jsonFile)
    dataFrame = dataRetriver_data(dateChange)

    if dateChange['rsid'] != "sssamsung4mstglobal":
        columnList = []
        for i in range(dataFrame.shape[1]):
            columnList.append(i)

        dataFrame.columns = columnList

        if site_code_rs == True:
            dataFrame = dataFrame.drop(0,axis =1)

        if dateChange['rsid'] == "sssamsungnewus":
            dataFrame.insert(0, "site_code", "us", True)

        else:
            rsName = dateChange['rsid'].split('4')
            if "epp" in rsName[-1]:
                dataFrame.insert(0, "site_code", rsName[-1].replace('epp', ''), True)
                epp = "Y"
            else:
                dataFrame.insert(0, "site_code", rsName[-1], True)

    if (if_site_code == True or site_code_rs == True):
        dataFrame.insert(1, "period", period, True)
        dataFrame.insert(2, "start_date", startDate, True)
        dataFrame.insert(3, "end_date", endDate, True)
        dataFrame.insert(4, "is_epp", epp, True)
    else:
        if dateChange['rsid'] == "sssamsung4mstglobal":
            dataFrame.insert(0, "site_code", "MST", True)
        dataFrame.insert(2, "period", period, True)
        dataFrame.insert(3, "start_date", startDate, True)
        dataFrame.insert(4, "end_date", endDate, True)
        dataFrame.insert(5, "is_epp", epp, True)

    return dataFrame  
# updated 220527. smb site code added
def filterSiteCode(dataframe):
    return dataframe.loc[dataframe['site_code'].isin(["kw", "kw_ar", "bh", "bh_ar", "om", "om_ar", "eg_en", "jo", "jo_ar", "ma", "africa_en", "africa_fr", "africa_pt", "al", "ar", "au", "at", "az", "be", "be_fr", "br", "ba", "bd", "bg", "ca", "ca_fr", "cl", "cn", "co", "hr", "cz", "dk", "eg", "ee", "fi", "fr", "de", "gr", "hk", "hk_en", "hu", "in", "id", "iran", "ie", "il", "it", "jp", "kz_ru", "kz_kz", "sec", "lv", "levant", "levant_ar", "lt", "mk", "my", "mx", "mm", "nl", "nz", "n_africa", "no", "pk", "latin", "latin_en", "py", "pe", "ph", "pl", "pt", "ro", "ps", "ru", "sa", "sa_en", "rs", "sg", "sk", "si", "za", "es", "se", "ch", "ch_fr", "tw", "th", "tr", "ae", "ae_ar", "uk", "ua", "uy", "uz_ru", "uz_uz", "vn", "au-smb", "uk-smb", "fr-smb", "at-smb", "it-smb", "es-smb", "th-smb", "id-smb", "vn-smb", "my-smb", "se-smb", "dk-smb", "fi-smb", "no-smb", "ca-smb", "ca_fr-smb", "de-smb", "nl-smb", "be-smb", "be_fr-smb", "levant-smb", "levant_ar-smb", "ae-smb", "ae_ar-smb", "nz-smb", "ph-smb", "ru-smb"])]


# updated 210907. added site_code_rs for us integration(due to the fact that us has no site code)
def jsonToDb(startDate, endDate, period, jsonLocation, tbColumn, dbTableName, epp, if_site_code, site_code_rs, limit):
    df = refinedFrame(startDate, endDate, period, jsonLocation, epp, if_site_code, site_code_rs)
    df.columns = tbColumn

    if limit == 0:
        df = df
    else:
        df = df.head(limit)

    if if_site_code == True:
        if returnRsID(jsonLocation) == "sssamsung4mstglobal":
            df = filterSiteCode(df)
 
    stackTodb(df, dbTableName)

def stackTodb(dataFrame, dbTableName):
    print(dataFrame)
    db_connection_str = 'mysql+pymysql://root:12345@127.0.0.1:3307/act'
    db_connection = create_engine(db_connection_str, encoding='utf-8')
    conn = db_connection.connect()

    dataFrame.to_sql(name=dbTableName, con=db_connection, if_exists='append', index=False)
    print("finished")


""" MST breakdown """

# breakdown itemID
def ChangeItemID(itemID, breakdownJson):
    temp_breakdownJson = deepcopy(breakdownJson)
    before_temp = temp_breakdownJson['metricContainer']['metricFilters']

    # change date > call using itemID iteration
    after_temp = deepcopy(before_temp)
    for i in range(len(after_temp)):
        if "itemId" in after_temp[i]:
            after_temp[i]["itemId"] = itemID
        else:
            continue

    temp_breakdownJson['metricContainer']['metricFilters'] = after_temp

    return temp_breakdownJson


def readJson(jsonFile):
    with open(jsonFile, 'r') as bla:
        json_data = json.loads(bla.read())

    return json_data
        

def returnItemID(startDate, endDate, jsonItemID):
    jsonFile = deepcopy(jsonItemID)
    itemIDjson = jsonDateChange(startDate, endDate, jsonFile)

    dataInitiator()

    itemIDdf = dataRetriver_data_breakdown(itemIDjson)

    columnList = list(map(str, range(itemIDdf.shape[1])))   

    columnList[0] = 'site_code'
    columnList[-1] = 'item_id'

    itemIDdf.columns = columnList

    if (itemIDjson["dimension"] == "variables/prop1" or itemIDjson["dimension"] == "variables/evar1" or itemIDjson["dimension"] == "variables/entryprop1"):
        itemIDdfFiltered = filterSiteCode(itemIDdf)
        itemIDlist = itemIDdfFiltered[['site_code', 'item_id']].values.tolist()        

    else:
        itemIDlist = itemIDdf[['site_code', 'item_id']].values.tolist()

    return itemIDlist


# Save as dictionary format return in tuple
def ReturnJsonchanged(startDate, endDate, jsonFile, jsonFilebreakdown):
    itemIDList = returnItemID(startDate, endDate, jsonFile)

    itemIDdict = {}
    for i in range(len(itemIDList)):
        jsonbreakdown = jsonDateChange(startDate, endDate, jsonFilebreakdown)
        itemIDdict[itemIDList[i][0]] = ChangeItemID(itemIDList[i][1], jsonbreakdown)
    
    itemIDdict = list(zip(itemIDdict.keys(), itemIDdict.values()))
    
    return itemIDdict

def StackbreakValue(startDate, endDate, period, jsonFile, jsonFilebreakdown, tbColumn, dbTableName, epp, limit):
    if returnRsID(jsonFile) == "sssamsung4mstglobal":
        itemIDdict = ReturnJsonchanged(startDate, endDate, jsonFile, jsonFilebreakdown)

        # iterable = list(map(int, range(len(itemIDdict))))

        # pool = multiprocessing.Pool(4)
        # func = partial(mstbreakDown, itemIDdict, startDate, endDate, period, tbColumn, dbTableName, epp, limit)
        # pool.map(func, iterable)
        # pool.close()
        # pool.join()

        for i in range(len(itemIDdict)):
            dataFrame = dataRetriver_data(itemIDdict[i][1])

            if limit == 0:
                dataFrame2 = dataFrame
            else:
                dataFrame2 = dataFrame.head(limit)

            dataFrame2.insert(0, "site_code", itemIDdict[i][0], True)
            dataFrame2.insert(2, "period", period, True)
            dataFrame2.insert(3, "start_date", startDate, True)
            dataFrame2.insert(4, "end_date", endDate, True)
            dataFrame2.insert(5, "is_us_epp", epp, True)

            dataFrame2.columns = tbColumn
            stackTodb(dataFrame2, dbTableName)

    else:
        dataInitiator()
        dateChange = jsonDateChange(startDate, endDate, jsonFile)
        dataFrame = dataRetriver_data(dateChange)

        dataFrame.columns = list(map(int, range(dataFrame.shape[1])))
        
        if limit == 0:
            dataFrame2 = dataFrame
        else:
            dataFrame2 = dataFrame.head(limit)

        if returnRsID(jsonFile) == "sssamsungnewus":
            dataFrame2.insert(0, "site_code", "us", True)
        else:
            rsName = dateChange['rsid'].split('4')
            dataFrame2.insert(0, "site_code", rsName[-1], True)   

        dataFrame2.insert(2, "period", period, True)
        dataFrame2.insert(3, "start_date", startDate, True)
        dataFrame2.insert(4, "end_date", endDate, True)
        dataFrame2.insert(5, "is_us_epp", epp, True)

        dataFrame2.columns = tbColumn
        stackTodb(dataFrame2, dbTableName)

"""Return after RS Name changed"""

def rsIDchange(jsonFile, rsID):
    temp_simple = deepcopy(jsonFile)
    temp_simple['rsid'] = rsID

    return temp_simple

def refineRsIDChange(startDate, endDate, jsonFile, rsList, period, tbColumn, epp):
    datechanged = jsonDateChange(startDate, endDate, jsonFile)
    rschanged = rsIDchange(datechanged, rsList[1])

    dataInitiator()
    dataFrame = dataRetriver_data(rschanged)


    columnList = []
    for i in range(dataFrame.shape[1]):
        columnList.append(i)

    dataFrame.columns = columnList

    dataFrame.insert(0, "site_code", rsList[0], True)
    dataFrame.insert(2, "period", period, True)
    dataFrame.insert(3, "start_date", startDate, True)
    dataFrame.insert(4, "end_date", endDate, True)

    if epp == True:
        dataFrame.insert(5, "is_epp", "Y", True)
    else:
        dataFrame.insert(5, "is_epp", "N", True)

    if (rsList[1] == "sssamsungnewus" or rsList[1] == "sssamsung4sec"):
        dataFrame.insert(6, "is_epp_integ", "Y", True)
    else:
        dataFrame.insert(6, "is_epp_integ", "N", True)
            
    dataFrame.columns = tbColumn
    
    return dataFrame

## 22.04.30 added
def refineRsIDChange_breakdown(startDate, endDate, jsonFile, jsonFile_breakdown, rsList, period, tbColumn, epp, limit):
    datechanged = jsonDateChange(startDate, endDate, jsonFile)
    datechanged_breakdown = jsonDateChange(startDate, endDate, jsonFile_breakdown)
    rschanged_jsonFile = rsIDchange(datechanged, rsList[1])
    rschanged_jsonFile_breakdown = rsIDchange(datechanged_breakdown, rsList[1])

    itemIDdict = ReturnJsonchanged(startDate, endDate, rschanged_jsonFile, rschanged_jsonFile_breakdown)
    for i in range(len(itemIDdict)):
        dataFrame = dataRetriver_data(itemIDdict[i][1])

        # limit 추가 시 넣기
        if limit == 0:
            dataFrame = dataFrame
        else:
            dataFrame = dataFrame.head(limit)

        # columnList = []
        # for i in range(dataFrame.shape[1]):
        #     columnList.append(i)

         # dataFrame.columns = columnList

        dataFrame.insert(0, "site_code", rsList[0], True)
        dataFrame.insert(2, "period", period, True)
        dataFrame.insert(3, "start_date", startDate, True)
        dataFrame.insert(4, "end_date", endDate, True)

        if epp == True:
            dataFrame.insert(5, "is_epp", "Y", True)
        else:
            dataFrame.insert(5, "is_epp", "N", True)

        if (rsList[1] == "sssamsungnewus" or rsList[1] == "sssamsung4sec"):
            dataFrame.insert(6, "is_epp_integ", "Y", True)
        else:
            dataFrame.insert(6, "is_epp_integ", "N", True)
                
        dataFrame.columns = tbColumn
        
        return dataFrame