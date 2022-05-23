from pyrda.dbms.rds import RdClient
from pyrdo.value import *
from pyrdo.list import *
from pyrdo.seq import seq_along
class BillModel():
    def __init__(self,token="AD64F20D-6063-4E87-81E8-A24C1751D758",FFormId='BD_MATERIAL',FActionName='Save'):
        '''
        initial setup for the BillModel class
        :param token: token for access the metadata database
        :param FFormId: id for bill
        :param FActionName: name for action.
        '''
        self.token = token
        self.FFormId = FFormId
        self.FActionName =FActionName
        # app for receice data from metadata
        self.app = RdClient(token=self.token)
        # ownerName get from token.
        self.FOwnerName = self.app.ownerName()
        # get the database info for businessinterface
        sql_head = "select FAccessToken,FTableKey, FViewName+'Stat' as FViewNameStat  from t_api_kdc_entity "
        sql_where1 = " where FOwnerName ='" + self.FOwnerName + "' and Ftype ='Head' "
        sql_where2 = " and FFormId='" + self.FFormId + "' and FActionName='" + self.FActionName + "'"
        sql_all = sql_head + sql_where1 + sql_where2
        data = self.app.select(sql_all)
        self.token2 = data[0]['FAccessToken']
        #get the viewName for statistics info.
        self.viewNameStat = data[0]['FViewNameStat']
        self.tableKey = data[0]['FTableKey']
        #client to access the data of business.
        self.dataClient = RdClient(token=self.token2)
    def getBillStat(self,FBillNo='so-api-002'):
        '''
        get the actual statistics info from business database.
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        sql_head ="select  FEntityName,FListCount   from  " + self.viewNameStat
        sql_where1 = " where  "+self.tableKey+" = '"+self.FBillNo+"' and FFormId ='"+self.FFormId+"' and FActionName ='"+self.FActionName+"'"
        sql_where2 = " and FOwnerName ='"+self.FOwnerName+"' and FType ='entryList'"
        sql_all = sql_head + sql_where1 +  sql_where2
        data = self.dataClient.select(sql_all)
        return(data)
    def getBillTable(self):
        sql_head = "select  distinct FTableName  from t_api_erp_kdc "
        sql_where = " where FOwnerName ='"+self.FOwnerName+"' and FFormId ='"+self.FFormId+"' and FActionName ='"+self.FActionName+"' and FIsShow =1 and Ftype <>'entry'"
        sql_all = sql_head + sql_where
        data = self.app.select(sql_all)
        return(data)
    def billGetActiveEntity(self,Ftype ='entry'):
        '''
        get the active entityname for data dealing
        :param Ftype:
        :return:
        '''
        self.Ftype = Ftype
        sql_head = " select  distinct FEntityName from t_api_erp_kdc "
        sql_where = " where FOwnerName ='"+self.FOwnerName+"' and FFormId ='"+self.FFormId+"' and FActionName ='"+self.FActionName+"' and FIsShow =1 and Ftype ='"+self.Ftype+"'"
        sql_all = sql_head + sql_where
        data = self.app.select(sql_all)
        ncount = len(data)
        if ncount >0:
            res = []
            for i in data:
                res.append(i['FEntityName'])
        else:
            res = ""
        return(res)

    def billTableSqlGenerator(self,FBillNo='so-api-002',Ftype ='head',FEntityName =''):
        '''
        generator the sql for each entry.
        :param FBillNo:
        :param Ftype:
        :param FEntityName:
        :return:
        '''
        self.FBillNo = FBillNo
        self.Ftype = Ftype
        self.FEntityName = FEntityName
        sql_head = "select  FTableName ,FTableFieldName,FAccessToken,FMainKey,FFormId,FEntityName,Ftype,FIsShow,FTableKey from t_api_erp_kdc "
        sql_where = " where FOwnerName ='" + self.FOwnerName + "' and FFormId ='" + self.FFormId + "' and FActionName ='" + self.FActionName + "' and FIsShow =1 and Ftype ='"+self.Ftype+"' and FEntityName ='"+self.FEntityName+"'"
        sql_all = sql_head + sql_where
        data_meta = self.app.select(sql_all)
        ncount_meta = len(data_meta)
        if ncount_meta > 0:
            FTableName = []
            FAccessToken = []
            FFieldList = []
            FTableKey = []
            for item in data_meta:
                FTableName.append(item['FTableName'])
                FTableKey.append(item['FTableKey'])
                FAccessToken.append(item['FAccessToken'])
                fieldCell = item['FTableFieldName'] + ' as ' + item['FMainKey']
                FFieldList.append(fieldCell)
            sql_field = ",".join(FFieldList)
            sql_head = "select "
            sql_from = " from " + FTableName[0]
            res = sql_head + sql_field + sql_from + " where  "+FTableKey[0]+" = '"+self.FBillNo+"' "

        else:
            res = ''
        return(res)
    def billHeadGetMeta(self,FBillNo='so-api-002'):
        '''
        get metainfo for head part.
        :param FBillNo:
        :return:
        '''
        self.FBillNo =FBillNo
        res = self.billTableSqlGenerator(FBillNo=self.FBillNo,Ftype='head',FEntityName='')
        return(res)

    def billHeadGetData(self,FBillNo='so-api-002'):
        '''
        get business data for head part
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        sql = self.billHeadGetMeta(FBillNo=self.FBillNo)
        if sql != '':
            data = self.dataClient.select(sql)
        else:
            data = ''
        return(data)

    def billHeadSetValue(self,option,FBillNo='so-api-002'):
        '''
        set option value for head part
        :param FBillNo:
        :return:
        '''
        self.option = option
        self.FBillNo = FBillNo
        data = self.billHeadGetData(FBillNo=self.FBillNo)
        ncount = len(data)
        if ncount == 1:
            cell = data[0]
            FMainKeys = dict_keys_list(cell)
            FValues = dict_values_list(cell)
            ncount_keys = len(FMainKeys)
            if ncount_keys > 0:
                for i in range(ncount_keys):
                    FMainKey = FMainKeys[i]
                    FValue = FValues[i]
                    self.option = self.setValue(option=self.option, FMainKey=FMainKey, FValue=FValue)
        return(self.option)
    def billEntryUnitGetMeta(self,FBillNo='so-api-002',FEntityName ='FSaleOrderFinance'):
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        res = self.billTableSqlGenerator(FBillNo=self.FBillNo,Ftype='entry',FEntityName=self.FEntityName)
        return(res)
    def billEntryUnitGetData(self,FBillNo='so-api-002',FEntityName ='FSaleOrderFinance'):
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        sql = self.billEntryUnitGetMeta(FBillNo=self.FBillNo,FEntityName=self.FEntityName)
        if sql != '':
            data = self.dataClient.select(sql)
        else:
            data = ''
        return(data)
    def billEntryUnitSetValue(self,option,FBillNo='so-api-002',FEntityName ='FSaleOrderFinance'):
        self.option = option
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        data = self.billEntryUnitGetData(FBillNo=self.FBillNo,FEntityName=self.FEntityName)
        ncount = len(data)
        if ncount == 1:
            cell = data[0]
            FMainKeys = dict_keys_list(cell)
            FValues = dict_values_list(cell)
            ncount_keys = len(FMainKeys)
            if ncount_keys > 0:
                for i in range(ncount_keys):
                    FMainKey = FMainKeys[i]
                    FValue = FValues[i]
                    self.option = self.setValue(option=self.option, FMainKey=FMainKey, FValue=FValue)
        return (self.option)


    def billEntryGetMeta(self,FBillNo='so-api-002'):
        '''
        not to be used.
        :param FBillNo: 
        :return: 
        '''
        pass
    def billEntryGetData(self,FBillNo='so-api-002'):
        '''
        get business data for entry part.
        not to be used
        :param FBillNo:
        :return:
        '''
        pass


    def billEntrySetValue(self,option,FBillNo='so-api-002'):
        '''
        set option value for entry part.
        :param FBillNo:
        :return:
        '''
        self.option = option
        FEntityNames = self.billGetActiveEntity(Ftype='entry')
        for FEntityName in FEntityNames:
            self.option = self.billEntryUnitSetValue(option=self.option,FBillNo=self.FBillNo,FEntityName=FEntityName)
        return(self.option)
    def billEntryListUnitGetMeta(self,FBillNo='so-api-002',FEntityName='FSaleOrderEntry'):
        '''
        get metadata for entrylist each table
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        res = self.billTableSqlGenerator(FBillNo=self.FBillNo,Ftype='entryList',FEntityName=self.FEntityName)
        return(res)
    def billEntryListUnitGetData(self,FBillNo='so-api-002',FEntityName='FSaleOrderEntry'):
        '''
        get busidata for entrylist each table.
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        sql = self.billEntryListUnitGetMeta(FBillNo=self.FBillNo,FEntityName=self.FEntityName)
        if sql != '':
            data = self.dataClient.select(sql)
        else:
            data = ''
        return(data)
    def billEntryListUnitSetValue(self,FBillNo='so-api-002',FEntityName='FSaleOrderEntry'):
        '''
        set option value for entrylist each table
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        self.FEntityName = FEntityName
        data =self.billEntryListUnitGetData(FBillNo=self.FBillNo,FEntityName=self.FEntityName)
        ncount = len(data)
        if ncount > 0 :
            for index in seq_along(ncount):
                cell = data[index-1]
                FMainKeys = dict_keys_list(cell)
                FValues = dict_values_list(cell)
                ncount_keys = len(FMainKeys)
                if ncount_keys > 0:
                    for i in range(ncount_keys):
                        FMainKey = FMainKeys[i]
                        FValue = FValues[i]
                        self.option = self.setValue(option=self.option, FMainKey=FMainKey, FValue=FValue,FListCount=index)

        return (self.option)

    def billEntryListGetMeta(self,FBillNo='so-api-002'):
        '''
        get metadata for entryList all
        not to use
        :param FBillNo:
        :return:
        '''
        pass
    def billEntryListGetData(self,FBillNo='so-api-002'):
        '''
        get busidata for entryList all
        not to use
        :param FBillNo:
        :return:
        '''
        pass
    def billEntryListSetValue(self,option,FBillNo='so-api-002'):
        '''
        set option value for entryList all
        :param FBillNo:
        :return:
        '''
        self.option =option
        self.FBillNo =FBillNo
        FEntityNames = self.billGetActiveEntity(Ftype='entryList')
        for FEntityName in FEntityNames:
            self.option = self.billEntryListUnitSetValue(FBillNo=self.FBillNo,FEntityName=FEntityName)
        return(self.option)




    def queryData(self, Ftype='head',FEntityName='', FListCount=0):
        '''
        query the metadata each by one entity name where FisHHOW is 1
        :param Ftype: type of the metadata
        :param FEntityName:  the entityname
        :param FListCount: the listconnt
        :return:
        '''
        self.Ftype = Ftype
        self.FEntityName = FEntityName
        self.FListCount = FListCount
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = "select FNodeName,FMainKey,FAuxKey,FDefaultValue,FDataType,FValueType  from t_api_erp_kdc"
        sql_where = "  where  Ftype ='" + self.Ftype + "'  and FEntityName ='" + self.FEntityName + "' and FIsShow =1  and FListCount = " + str(
            self.FListCount) + " and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)
    def queryMeta(self,FMainKey='FIssueType'):
        '''
        query meta info by Main key
        :param FMainKey: the main key
        :return:
        '''
        self.FMainKey = FMainKey
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = " select  FNodeName,FEntityName,FListCount,FMainKey,FAuxKey,Ftype,FDataType,FValueType from  t_api_erp_kdc  "
        sql_where = "  where   FIsShow =1  and FMainKey ='" + self.FMainKey + "' and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)
    def setValue(self,option,FMainKey='FIssueType',FListCount=0, FValue=""):
        '''
        set the value for each key
        which has a bug for the key has more than one row.
        to do list: add the parameter FListCount
        :param option:
        :param FMainKey:
        :param FListCount:
        :param FValue:
        :return:
        '''
        self.option = option
        self.FMainKey =FMainKey
        # print('bug for mainKey:')
        # print(FMainKey)
        self.FValue = FValue
        data = self.queryMeta(FMainKey=self.FMainKey)
        ncount = len(data)
        if ncount > 0:
            for i in data:
                node_model = i['FNodeName']
                node_entity = i['FEntityName']
                #fix the bug
                #node_count = i['FListCount'] - 1
                node_count = FListCount - 1
                node_main = i['FMainKey']
                node_aux = i['FAuxKey']
                node_type = i['Ftype']
                node_datatype = i['FDataType']
                node_valueType = i['FValueType']
                if node_type == 'head':
                    if node_valueType == 'simple':
                        self.option[node_model][node_main] = valueConverter(FValue, node_datatype)
                    else:
                        # complex one
                        self.option[node_model][node_main][node_aux] = valueConverter(FValue, node_datatype)
                if node_type == 'entry':
                    if node_valueType == 'simple':
                        self.option[node_model][node_entity][node_main] = valueConverter(FValue, node_datatype)
                    else:
                        # complex one
                        self.option[node_model][node_entity][node_main][node_aux] = valueConverter(FValue, node_datatype)
                if node_type == 'entryList':
                    if node_valueType == 'simple':
                        self.option[node_model][node_entity][node_count][node_main] = valueConverter(FValue, node_datatype)
                    else:
                        # complex one
                        self.option[node_model][node_entity][node_count][node_main][node_aux] = valueConverter(FValue,
                                                                                                          node_datatype)
        return (self.option)

    def bodySheet(self,Ftype='entry'):
        '''
        get the entityNames by type
        :param Ftype: type for head,entry and entryList
        :return:
        '''
        self.Ftype = Ftype
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = "select  distinct FEntityName  from  t_api_erp_kdc"
        sql_where = "  where  Ftype ='" + self.Ftype + "'   and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)
    def queryEntity(self, Ftype='entry'):
        '''
        queryEntity is the alias name of bodySheet
        :param Ftype:
        :param FActionName:
        :return:
        '''
        self.Ftype = Ftype
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = "select  distinct FEntityName  from  t_api_erp_kdc"
        sql_where = "  where  Ftype ='" + self.Ftype + "'   and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)

    def tailCount(self, Ftype='entryList',FEntityName='FEntityAuxPty'):
        '''
        there is a bug in this function which query the metadata.
        not for usage.
        :param Ftype:
        :param FEntityName:
        :return:
        '''
        self.Ftype = Ftype
        self.FEntityName =FEntityName
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = "  select distinct FListCount  from t_api_erp_kdc"
        sql_where = "  where  Ftype ='" + self.Ftype + "'  and FEntityName ='" + self.FEntityName + "'  and FIsShow =1  and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)

    def tailCountEx(self, Ftype='entryList', FEntityName='FEntityAuxPty'):
        '''
        to do list:
        :param Ftype:
        :param FEntityName:
        :return:
        '''
        self.Ftype = Ftype
        self.FEntityName = FEntityName
        # app = RdClient(token=self.token)
        # FOwnerName = app.ownerName()
        sql_head = "  select distinct FListCount  from t_api_erp_kdc"
        sql_where = "  where  Ftype ='" + self.Ftype + "'  and FEntityName ='" + self.FEntityName + "'  and FIsShow =1  and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='" + self.FOwnerName + "'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)
    def item(self,node, i):
        '''
        transform the data into a node.
        :param node: a node in an option tree
        :param i:  one data row
        :return:  return value.
        '''
        self.node =node
        self.i = i
        valueType = self.i['FValueType']
        dataType = self.i['FDataType']
        value = self.i['FDefaultValue']
        key = self.i['FMainKey']
        key2 = self.i['FAuxKey']
        value = valueConverter(value, dataType)
        self.node[key] = valueWrapper(value, valueType, key2)
        return (self.node)

    def unity(self,data, option, FEntityName='', Ftype='entryList'):
        '''
        unity used for head or entry body with option as input.
        if used for entryList,please refer unitNode function.
        :param data:
        :param option:
        :param FEntityName:
        :param Ftype:
        :return:
        '''
        ncount = len(data)
        node = {}
        if ncount > 0:
            for i in data:
                node = self.item(node, i)
            # 是否为表头
            if Ftype == 'head':
                option["Model"] = node
            else:
                option["Model"][FEntityName] = node
        return (option)
    def unityNode(self,data, FEntityName='', Ftype='entryList'):
        '''
        this the the key to solve the question for billEntry.
        unitNode used for entryList without option as input parameters.
        eachNode means one row in entryList
        if we have two or more row for billEntry,then we should call this function multiplly.
        :param data:
        :param FEntityName:
        :param Ftype:
        :return:
        '''
        ncount = len(data)
        node = {}
        if ncount > 0:
            for i in data:
                node = self.item(node, i)
        return (node)

    def tailUnity(self,Ftype='entryList', FEntityName='FEntityAuxPty', FListCount=1):
        '''
        tail Unity means one row the property setting without option
        :param Ftype:
        :param FEntityName:
        :param FListCount:
        :return:
        '''
        self.Ftype =Ftype
        self.FEntityName =FEntityName
        self.FListCount =FListCount
        data = self.queryData(Ftype=self.Ftype,FEntityName=self.FEntityName, FListCount=self.FListCount)
        res = self.unityNode(data=data, FEntityName=self.FEntityName, Ftype=self.Ftype)
        return (res)

    def tail(self,option,  Ftype='entryList',FEntityName='FEntityAuxPty',FListCount=1):
        '''
        tail mean model tail part represent as a list object.
        :param option:
        :param Ftype:
        :param FEntityName:
        :return:
        '''
        self.option = option
        self.Ftype = Ftype
        self.FEntityName =FEntityName
        #not use  for metadata
        #data = self.tailCount(Ftype=self.Ftype, FEntityName=self.FEntityName)
        data = seq_along(FListCount)
        ncount = len(data)
        if ncount > 0:
            res = []
            for i in data:
                #generate multiple row with same data
                #we set i into 1 for param:FListCount
                item = self.tailUnity(Ftype=self.Ftype, FEntityName=self.FEntityName,
                                       FListCount=1)
                res.append(item)
            self.option['Model'][self.FEntityName] = res
        return (self.option)

    def head(self):
        data = self.queryData(Ftype='head', FEntityName='', FListCount=0)
        option = {}
        option = self.unity(data=data, option=option, FEntityName='', Ftype='head')
        return (option)

    def body(self,option,FEntityName='FSubHeadEntity'):
        self.option = option
        self.FEntityName =FEntityName
        data = self.queryData(Ftype='entry', FEntityName=self.FEntityName, FListCount=0)
        ncount = len(data)
        self.option = self.unity(data=data, option=self.option, FEntityName=self.FEntityName, Ftype='entry')
        return (self.option)

    def bodySet(self,option):
        self.option =option
        dataSheet = self.bodySheet(Ftype='entry')
        for sheet in dataSheet:
            self.option = self.body(option=self.option,FEntityName=sheet['FEntityName'])
        return (self.option)

    def tailSet(self,option,FBillNo='so-api-002'):
        self.option = option
        self.FBillNo = FBillNo
        #body sheet 也是一个问题，如何传入分页的数量
        # bug fixed
        #tailSheet = self.bodySheet(Ftype='entryList')
        tailSheet = self.getBillStat(FBillNo=self.FBillNo)
        for i in tailSheet:
            #there is bug to be fixed
            self.option = self.tail(option=self.option, Ftype='entryList',
                                FEntityName=i['FEntityName'],FListCount=i['FListCount'])
            #print('bug2')
            #print(i)
            #print(self.option)
        return (self.option)
    def dataGen(self,FBillNo='so-api-002'):
        '''
        gen the data from metadata.
        :param FBillNo:
        :return:
        '''
        self.FBillNo = FBillNo
        #initial option
        option = self.head()
        option = self.bodySet(option=option)
        option = self.tailSet(option=option,FBillNo=self.FBillNo)
        #get data
        option = self.billHeadSetValue(option=option,FBillNo=self.FBillNo)
        option = self.billEntrySetValue(option=option,FBillNo=self.FBillNo)
        option = self.billEntryListSetValue(option=option,FBillNo=self.FBillNo)
        #set value
        #note for key and value.
        return(option)
if __name__ =='__main__':
    pass