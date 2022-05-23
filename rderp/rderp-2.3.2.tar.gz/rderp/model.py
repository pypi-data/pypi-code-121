from pyrda.dbms.rds import RdClient
from pyrdo.value import *
from pyrdo.list import *
from pyrdo.seq import seq_along
#object Style:
class Model():
    def __init__(self,token="AD64F20D-6063-4E87-81E8-A24C1751D758",FFormId='BD_MATERIAL',FActionName='Save'):
        self.token = token
        self.FFormId = FFormId
        self.FActionName =FActionName
        self.app = RdClient(token=self.token)
        self.FOwnerName = self.app.ownerName()

    def queryData(self, Ftype='head',FEntityName='', FListCount=0):
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
        self.FMainKey = FMainKey
        #app = RdClient(token=self.token)
        #FOwnerName = app.ownerName()
        sql_head = " select  FNodeName,FEntityName,FListCount,FMainKey,FAuxKey,Ftype,FDataType,FValueType from  t_api_erp_kdc  "
        sql_where = "  where   FIsShow =1  and FMainKey ='" + self.FMainKey + "' and FFormId = '"
        sql_all = sql_head + sql_where + self.FFormId + "'  and FActionName ='" + self.FActionName + "' and FOwnerName ='"+self.FOwnerName+"'"
        # print(sql_all)
        data = self.app.select(sql=sql_all)
        return (data)
    def setValue(self,option,FMainKey='FIssueType', FValue=""):
        self.option = option
        self.FMainKey =FMainKey
        self.FValue = FValue
        data = self.queryMeta(FMainKey=self.FMainKey)
        ncount = len(data)
        if ncount > 0:
            for i in data:
                node_model = i['FNodeName']
                node_entity = i['FEntityName']
                node_count = i['FListCount'] - 1
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
    def item(self,node, i):
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
        unitNode used for entryList without option as input parameters.s
        :param data:
        :param FEntityName:
        :param Ftype:
        :return:
        '''
        ncount = len(data)
        node = {}
        if ncount > 0:
            for i in data:
                node = model_Item(node, i)
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

    def tail(self,option,  Ftype='entryList',FEntityName='FEntityAuxPty'):
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
        data = self.tailCount(Ftype=self.Ftype, FEntityName=self.FEntityName)
        ncount = len(data)
        if ncount > 0:
            res = []
            for i in data:
                item = self.tailUnity(Ftype=self.Ftype, FEntityName=self.FEntityName,
                                       FListCount=i['FListCount'])
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

    def tailSet(self,option):
        self.option = option
        tailSheet = self.bodySheet(Ftype='entryList')
        for i in tailSheet:
            self.option = self.tail(option=self.option, Ftype='entryList',
                                FEntityName=i['FEntityName'])
            #print('bug2')
            #print(i)
            #print(self.option)
        return (self.option)


    def dataGen(self,sql_where = "FNumber = 'api-02'"):
        #prepare data
        sql_head_meta = "select FViewName,FViewFieldName,FAccessToken,FMainKey from t_api_erp_kdc "
        sql_where_meta = " where FOwnerName ='" + self.FOwnerName + "' and FFormId ='" + self.FFormId + "' and FActionName ='" + self.FActionName + "' and FIsShow =1"
        sql = sql_head_meta + sql_where_meta
        data_meta = self.app.select(sql)
        ncount_meta = len(data_meta)
        if ncount_meta > 0:
            FViewName = []
            FAccessToken = []
            FFieldList = []
            for item in data_meta:
                FViewName.append(item['FViewName'])
                FAccessToken.append(item['FAccessToken'])
                fieldCell = item['FViewFieldName'] + ' as ' + item['FMainKey']
                FFieldList.append(fieldCell)
            sql_field = ",".join(FFieldList)
            sql_head = "select "
            sql_from = " from " + FViewName[0]
            sql = sql_head + sql_field + sql_from + " where  " + sql_where
            app_data = RdClient(token=FAccessToken[0])
            res = app_data.select(sql)
            ncount_res = len(res)
            if ncount_res > 0:
                cell = res[0]
                FMainKeys = dict_keys_list(cell)
                FValues = dict_values_list(cell)
                # bill head
                option = self.head()
                # bill body
                option = self.bodySet(option=option)
                # tailList
                option = self.tailSet(option=option)
                #deal with data
                ncount_keys =len(FMainKeys)
                if ncount_keys >0:
                    for i in range(ncount_keys):
                        FMainKey = FMainKeys[i]
                        FValue = FValues[i]

                        option = self.setValue(option=option, FMainKey=FMainKey, FValue=FValue)
                    return (option)


if __name__ =='__main__':
    pass















