'''
 * this file is wrapper for K3CloudApiSdk
 * version is 3.0
'''
from k3cloud_webapi_sdk.main import K3CloudApiSdk

'''
 * the follow code show the way to test in local mode
'''
# from rderp.main import ErpClient
# from rderp.model import Model

'''
* the follow code show the way to refer inner the package.
* check this setting before publish the code into new package.

'''
from ..main import ErpClient
from ..apiAuth import api_getInfo
from ..billLinkModel import BillLinkModel
import json
'''
* class definition for material object in ERP system
'''


class SaleDeliveryNotice(ErpClient):
    def __init__(self, api_token='BEC6002E-C3AE-4947-AD70-212CF2B4218B',
                 meta_token="AD64F20D-6063-4E87-81E8-A24C1751D758",
                 timeout=120):
        '''

        :param api_token:  api token to connect erp system.
        :param meta_token:  token to connect metadata
        :param timeout:
        '''

        self.api_token = api_token
        data_info = api_getInfo(api_token=self.api_token)
        #print(data_info)
        self.acct_id = data_info['Facct_id']
        self.user_name = data_info['Fuser_name']
        #print(self.user_name)
        self.app_id = data_info['Fapp_id']
        self.app_secret = data_info['Fapp_secret']
        self.server_url = data_info['Fserver_url']
        self.timeout = timeout
        self.token = meta_token
        ErpClient.__init__(self, acct_id=self.acct_id, user_name=self.user_name, app_id=self.app_id,
                           app_secret=self.app_secret, server_url=self.server_url, timeout=self.timeout)

    def Meta(self):
        '''
        query the business info or metadata info for material.
        :return:
        '''
        data = {"FormId": "SAL_DELIVERYNOTICE"}
        res = ErpClient.QueryBusinessInfo(self, data=data)
        return (res)


    def View(self, Number, CreateOrgId=0, Id=""):
        '''
        * material view / query opration,see the detail infomation each in one material
        :param Number: the number of material
        :param CreateOrgId: the Create orginazation of the material,default is 0
        :param Id: the inner code for material
        :return: the return value is a json formmated data
        '''
        '''
        * to do list:
        * 1. add the function to deal the return value.
        '''
        self.Number = Number
        self.CreateOrgId = CreateOrgId
        self.Id = Id
        '''
        * create the data for material.View opration
        '''
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Number": self.Number,
            "Id": self.Id}
        res = ErpClient.View(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def Save_demo(self, FNumber='API-01', FName='demo-02'):
        self.FNumber = FNumber
        self.FName = FName
        data = {
            "Model": {
                "FID": 0,
                "FBillTypeID": {"FNUMBER": "FHTZD01_SYS"},
                "FBillNo":'FHTZD22050032',
                "FDate": "2022-05-16 00:00:00",
                "FSaleOrgId": {"FNumber": "100"},
                "FCustomerID": {"FNumber": "CUST22033165"},
                "FSaleDeptID": {"FNumber": "BM000053"},
                "FDeliveryOrgID": {"FNumber": "100"},
                "FSaleGroupID": {"FNumber": "XS011"},
                "FSalesManID": {"FNumber": "HR028_GW000052_1"},
                "FReceiverID": {"FNumber": "CUST22033165"},
                "FSettleID": {"FNumber": "CUST22033165"},
                "FPayerID": {"FNumber": "CUST22033165"},
                "FOwnerTypeIdHead": "BD_OwnerOrg",
                "SubHeadEntity": {
                    "FSettleOrgID": {"FNumber": "100"},
                    "FSettleCurrID": {"FNumber": "PRE001"},
                    "FLocalCurrID": {"FNumber": "PRE001"},
                    "FExchangeTypeID": {"FNumber": "HLTX01_SYS"},
                    "FExchangeRate": 1.0,
                    "FOverOrgTransDirect": 'false'},
                "FEntity": [
                    {
                        "FRowType": "Standard",
                        "FMaterialID": {"FNumber": "800101-122"},
                        "FUnitID": {"FNumber": "carton"},
                        "FQty": 10.0,
                        "FDeliveryDate": "2022-05-16 00:00:00",
                        "FStockStatusId": {"FNumber": "KCZT01_SYS"},
                        "FOutContROL": 'true',
                        "FOutMaxQty": 10.0,
                        "FOutMinQty": 10.0,
                        "FBaseUnitID": {"FNumber": "carton"},
                        "FPriceBaseQty": 10.0,
                        "FPlanDeliveryDate": "2022-05-16 00:00:00",
                        "FStockUnitID": {"FNumber": "carton"},
                        "FSrctype":'SAL_SaleOrder',
                        "FStockQty": 10.0,
                        "FStockBaseQty": 10.0,
                        "FOwnerTypeID": "BD_OwnerOrg",
                        "FOwnerID": {"FNumber": "100"},
                        "FOutLmtUnit": "SAL",
                        "FOutLmtUnitID": {"FNumber": "carton"},
                        "FCheckDelivery": 'false',
                        "FEntity_Link":[{
                            "FEntity_Link_FRuleId":'SaleOrder-DeliveryNotice',
                            "FEntity_Link_FSTableName":'T_SAL_ORDERENTRY',
                            "FEntity_Link_FSBillId":'199556',
                            "FEntity_Link_FSId":"246023",
                            "FEntity_Link_FBaseUnitQtyOld":10,
                            "FEntity_Link_FBaseUnitQty":10,
                            "FEntity_Link_FStockBaseQtyOld":10,
                            "FEntity_Link_FstockBaseQty":10}]

                    },
                    {
                        "FRowType": "Standard",
                        "FMaterialID": {"FNumber": "YRT300C08-1"},
                        "FUnitID": {"FNumber": "box"},
                        "FQty": 1.0,
                        "FDeliveryDate": "2022-05-16 00:00:00",
                        "FStockStatusId": {"FNumber": "KCZT01_SYS"},
                        "FOutContROL": 'true',
                        "FOutMaxQty": 1.0,
                        "FOutMinQty": 1.0,
                        "FBaseUnitID": {"FNumber": "box"},
                        "FPriceBaseQty": 1.0,
                        "FPlanDeliveryDate": "2022-05-16 00:00:00",
                        "FStockUnitID": {"FNumber": "box"},
                        "FSrctype": 'SAL_SaleOrder',
                        "FStockQty": 1.0,
                        "FStockBaseQty": 1.0,
                        "FOwnerTypeID": "BD_OwnerOrg",
                        "FOwnerID": {"FNumber": "100"},
                        "FOutLmtUnit": "SAL",
                        "FOutLmtUnitID": {"FNumber": "box"},
                        "FCheckDelivery": 'false',
                        "FEntity_Link": [{
                            "FEntity_Link_FRuleId": 'SaleOrder-DeliveryNotice',
                            "FEntity_Link_FSTableName": 'T_SAL_ORDERENTRY',
                            "FEntity_Link_FSBillId": '199556',
                            "FEntity_Link_FSId": "246024",
                            "FEntity_Link_FBaseUnitQtyOld": 1,
                            "FEntity_Link_FBaseUnitQty": 1,
                            "FEntity_Link_FStockBaseQtyOld": 1,
                            "FEntity_Link_FstockBaseQty": 1}]
                    }]
                    }
                    }

        res = ErpClient.Save(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def Save(self, FBillNo='so-api-002'):
        '''
        Save option is new material without materialID.
        :param data:
        :return:
        '''
        self.FBillNo = FBillNo
        app = BillLinkModel(token=self.token, FFormId='SAL_DELIVERYNOTICE', FActionName='Save')
        data = app.dataGen(FBillNo=self.FBillNo)
        print(data)
        res_str = ErpClient.Save(self, formid="SAL_DELIVERYNOTICE", data=data)
        res_obj = json.loads(res_str)
        # print(res_obj)
        flag = res_obj['Result']['ResponseStatus']['IsSuccess']
        if flag:
            msg = "单据" + FBillNo + "保存成功"
            res = {"status": flag, "data": FBillNo, "msg": msg}
        else:
            error = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
            res = {"status": flag, "data": FBillNo, "msg": error}
        return (res)



    def Modify(self, data):
        '''
        Modify is base on the Save option with aditional part is FMATERIALID
        :param data:
        :return:
        '''
        res = ErpClient.Save(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def Query(self,FBillNo='FHTZD22050032'):
        FieldKeys = "FBillNo,FID,FEntity_FEntryID"
        FilterString = "FBillNo='"+FBillNo+"'"
        OrderString = ""
        TopRowCount = 0
        StartRow = 0
        Limit = 0
        self.FieldKeys = FieldKeys
        self.FilterString = FilterString
        self.OrderString = OrderString
        self.TopRowCount = TopRowCount
        self.StartRow = StartRow
        self.Limit = Limit
        data = {
            "FormId": "SAL_DELIVERYNOTICE",
            "FieldKeys": self.FieldKeys,
            "FilterString": self.FilterString,
            "OrderString": self.OrderString,
            "TopRowCount": self.TopRowCount,
            "StartRow": self.StartRow,
            "Limit": self.Limit
        }
        res_str = ErpClient.ExecuteBillQuery(self, data=data)
        data = json.loads(res_str)
        ncount = len(data)
        if ncount >0:
            info = []
            for item in data:
                cell = {}
                cell['FBillNo'] = item[0]
                cell['FInterId'] = item[1]
                cell['FEntryId'] = item[2]
                info.append(cell)
            res = {"status":True,"data":FBillNo,"msg":info}
        else:
            info = "单据"+FBillNo+"不存在内码信息"
            res = {"status": False, "data":FBillNo , "msg": info}



        return(res)
    def QueryInterId(self,FBillNo='FHTZD22050032'):
        FieldKeys = "FBillNo,FID,FEntity_FEntryID"
        FilterString = "FBillNo='"+FBillNo+"'"
        OrderString = ""
        TopRowCount = 0
        StartRow = 0
        Limit = 0
        self.FieldKeys = FieldKeys
        self.FilterString = FilterString
        self.OrderString = OrderString
        self.TopRowCount = TopRowCount
        self.StartRow = StartRow
        self.Limit = Limit
        data = {
            "FormId": "SAL_DELIVERYNOTICE",
            "FieldKeys": self.FieldKeys,
            "FilterString": self.FilterString,
            "OrderString": self.OrderString,
            "TopRowCount": self.TopRowCount,
            "StartRow": self.StartRow,
            "Limit": self.Limit
        }
        res_str = ErpClient.ExecuteBillQuery(self, data=data)
        data = json.loads(res_str)
        ncount = len(data)
        if ncount >0:
            info = []
            for item in data:
                cell = {}
                cell['FBillNo'] = item[0]
                cell['FInterId'] = item[1]
                cell['FEntryId'] = item[2]
                info.append(cell)
            res = {"status":True,"data":FBillNo,"msg":info}
        else:
            info = "单据"+FBillNo+"不存在内码信息"
            res = {"status": False, "data":FBillNo , "msg": info}



        return(res)

    def SaveBatch(self, data_list):
        '''
        *save the data in a batch list
        *put multiple save format data into a list
        :param data_list:
        :return:
        '''
        self.data_list = data_list
        save_data = {"Model": self.data_list}
        res = ErpClient.BatchSave(self, formid='SAL_DELIVERYNOTICE', data=save_data)
        return (res)

    def SaveBatchAsync(self, data_list):
        '''
        *save the data in a batch list in Async way.
        *put multiple save format data into a list
        :param data_list:
        :return:
        '''
        self.data_list = data_list
        save_data = {"Model": self.data_list}
        res = ErpClient.BatchSaveQuery(self, formid='SAL_DELIVERYNOTICE', data=save_data)
        return (res)

    def Submit(self, FBillNo):
        '''
        * the material Submit operation just after save.
        :param Numbers: list of material numbers
        :param Ids:   the Ids of material
        :param SelectedPostId: the SelectedPostId of material
        :param NetworkCtrl:  the NetworkCtrl status of material
        :param IgnoreInterationFlag: the Flag of material
        :return: without the return value or the status of Submit after exec.
        '''
        Numbers = [FBillNo]
        Ids = ""
        SelectedPostId = 0
        NetworkCtrl = ""
        IgnoreInterationFlag = ""
        self.Numbers = Numbers
        self.Ids = Ids
        self.SelectedPostId = SelectedPostId
        self.NetworkCtrl = NetworkCtrl
        self.IgnoreInterationFlag = IgnoreInterationFlag
        data = {
            "CreateOrgId": 0,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "SelectedPostId": self.SelectedPostId,
            "NetworkCtrl": self.NetworkCtrl,
            "IgnoreInterationFlag": self.IgnoreInterationFlag
        }
        res_str = ErpClient.Submit(self, formid="SAL_DELIVERYNOTICE", data=data)
        res_obj = json.loads(res_str)
        flag = res_obj['Result']['ResponseStatus']['IsSuccess']
        if flag:
            msg = "单据" + FBillNo + "提交成功"
            res = {"status": flag, "data": FBillNo, "msg": msg}
        else:
            error = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
            res = {"status": flag, "data": FBillNo, "msg": error}
        return (res)

    def CancelAssign(self, Numbers=[], CreateOrgId=0, Ids="", NetworkCtrl=""):
        '''
        the Cancel operion for submit of material
        :param Numbers: list for number of material
        :param CreateOrgId: the CreateOrgId of material
        :param Ids: the Ids of material
        :param NetworkCtrl: the NetWorkCtrl of material
        :return: the return values
        '''
        self.Numbers = Numbers
        self.CreateOrgId = CreateOrgId
        self.Ids = Ids
        self.NetworkCtrl = NetworkCtrl
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "NetworkCtrl": self.NetworkCtrl
        }
        res = ErpClient.CancelAssign(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def UnSubmit(self, Numbers=[], CreateOrgId=0, Ids="", NetworkCtrl=""):
        '''
        the oposite operation for submit
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param NetworkCtrl:
        :return:
        '''
        res = self.CancelAssign(Numbers=Numbers, CreateOrgId=CreateOrgId, Ids=Ids, NetworkCtrl=NetworkCtrl)
        return (res)

    def Audit(self, FBillNo):
        '''
        the Audit or Check operation of material.
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param InterationFlags:
        :param NetworkCtrl:
        :param IsVerifyProcInst:
        :param IgnoreInterationFlag:
        :return:
        '''
        Numbers = [FBillNo]
        CreateOrgId = 0
        Ids = ""
        InterationFlags = ""
        NetworkCtrl = ""
        IsVerifyProcInst = ""
        IgnoreInterationFlag = ""
        self.Numbers = Numbers
        self.CreateOrgId = CreateOrgId
        self.Ids = Ids
        self.InterationFlags = InterationFlags
        self.NetworkCtrl = NetworkCtrl
        self.IsVerifyProcInst = IsVerifyProcInst
        self.IgnoreInterationFlag = IgnoreInterationFlag
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "InterationFlags": self.InterationFlags,
            "NetworkCtrl": self.NetworkCtrl,
            "IsVerifyProcInst": self.IsVerifyProcInst,
            "IgnoreInterationFlag": self.IgnoreInterationFlag
        }
        res_str = ErpClient.Audit(self, formid="SAL_DELIVERYNOTICE", data=data)
        res_obj = json.loads(res_str)
        flag = res_obj['Result']['ResponseStatus']['IsSuccess']
        if flag:
            msg = "单据" + FBillNo + "审核成功"
            res = {"status": flag, "data": FBillNo, "msg": msg}
        else:
            error = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
            res = {"status": flag, "data": FBillNo, "msg": error}
        return (res)

    def Check(self, FBillNo):
        '''
        create the alias for Audit operation of material.
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param InterationFlags:
        :param NetworkCtrl:
        :param IsVerifyProcInst:
        :param IgnoreInterationFlag:
        :return:
        '''
        res = self.Audit(FBillNo=FBillNo)
        return (res)
    def ApiSave(self, FBillNo):
        info_save = self.Save(FBillNo=FBillNo)
        if info_save['status']:
            info_submit = self.Submit(FBillNo=FBillNo)
            if info_submit['status']:
                info_save = self.Check(FBillNo=FBillNo)
                res = info_save
            else:
                res = info_submit

        else:
            res = info_save


        return(res)
    def ApiDel(self,FBillNo):
        info_uncheck = self.UnCheck(FBillNo=FBillNo)
        if info_uncheck['status']:
            info_del = self.Delete(FBillNo=FBillNo)
            res = info_del
        else:
            res = info_uncheck


        return(res)
    def UnAudit(self, FBillNo):
        Numbers = [FBillNo]
        CreateOrgId = 0
        Ids = ""
        InterationFlags = ""
        NetworkCtrl = ""
        IsVerifyProcInst = ""
        IgnoreInterationFlag = ""
        self.Numbers = Numbers
        self.CreateOrgId = CreateOrgId
        self.Ids = Ids
        self.InterationFlags = InterationFlags
        self.NetworkCtrl = NetworkCtrl
        self.IsVerifyProcInst = IsVerifyProcInst
        self.IgnoreInterationFlag = IgnoreInterationFlag
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "InterationFlags": self.InterationFlags,
            "IgnoreInterationFlag": self.IgnoreInterationFlag,
            "NetworkCtrl": self.NetworkCtrl,
            "IsVerifyProcInst": self.IsVerifyProcInst
        }
        res_str = ErpClient.UnAudit(self, formid="SAL_DELIVERYNOTICE", data=data)
        res_obj = json.loads(res_str)
        flag = res_obj['Result']['ResponseStatus']['IsSuccess']
        if flag:
            msg = "单据" + FBillNo + "反审核成功"
            res = {"status": flag, "data": FBillNo, "msg": msg}
        else:
            error = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
            res = {"status": flag, "data": FBillNo, "msg": error}
        return (res)

    def UnCheck(self, FBillNo):
        '''
        create the alias for UnAudit operation of material.
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param InterationFlags:
        :param NetworkCtrl:
        :param IsVerifyProcInst:
        :param IgnoreInterationFlag:
        :return:
        '''
        res = self.UnAudit(FBillNo=FBillNo)
        return (res)

    def Delete(self, FBillNo):
        '''
        the Delete operation of material
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param NetworkCtrl:
        :return:
        '''
        Numbers = [FBillNo]
        CreateOrgId = 0
        Ids = ""
        NetworkCtrl = ""
        self.Numbers = Numbers
        self.CreateOrgId = CreateOrgId
        self.Ids = Ids
        self.NetworkCtrl = NetworkCtrl
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "NetworkCtrl": self.NetworkCtrl
        }
        res_str = ErpClient.Delete(self, formid="SAL_DELIVERYNOTICE", data=data)
        res_obj = json.loads(res_str)
        flag = res_obj['Result']['ResponseStatus']['IsSuccess']
        if flag:
            msg = "单据" + FBillNo + "删除成功"
            res = {"status": flag, "data": FBillNo, "msg": msg}
        else:
            error = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
            res = {"status": flag, "data": FBillNo, "msg": error}
        return (res)
    def Push(self,FBillNo):
        data = {
            "Numbers": [FBillNo],
            "EntryIds": "",
            "RuleId": "SaleOrder-DeliveryNotice",
            "TargetBillTypeId": "",
            "TargetOrgId": 0,
            "TargetFormId": "SAL_DELIVERYNOTICE",
            "IsEnableDefaultRule": "false",
            "IsDraftWhenSaveFail": "false",
            "CustomParams": {}
        }
        res_str = ErpClient.Push(self,formid="SAL_DELIVERYNOTICE",data=data)
        res_obj = json.loads(res_str)
        # print(res_obj)
        res = {}
        res['status'] = res_obj['Result']['ResponseStatus']['IsSuccess']
        if res['status']:
            res['data'] = res_obj['Result']['ResponseStatus']['SuccessEntitys'][0]['Number']
        else:
            res['data'] = res_obj['Result']['ResponseStatus']['Errors'][0]['Message']
        return(res)

    def Allocate(self, PrdIdString=0, OrgIdString=""):
        '''
        the Allocation operation of material to other organizations
        :param PrdIdString: the Ids string seperate by comma of material,not a list but a string,such as '333115,333116'
        :param OrgIdString: the Ids string seperate by comma of organizations,not a list but a string,'100201,100202'
        :return: return the status
        '''
        '''
        * to do list
        * 1. test the app Interface. done.
        * data6 =material.Allocate(PrdIdString='333115,333116',OrgIdString='100201,100202')
        * print(data6)
        '''
        self.PkIds = PrdIdString
        self.TOrgIds = OrgIdString
        data = {
            "PkIds": self.PkIds,
            "TOrgIds": self.TOrgIds
        }
        res = ErpClient.Allocate(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def CancelAllocate(self, PrdIdString=0, OrgIdString=""):
        '''
        cancel the allocation of matrial.
        :param PrdIdString:
        :param OrgIdString:
        :return:
        '''
        self.PkIds = PrdIdString
        self.TOrgIds = OrgIdString
        data = {
            "PkIds": self.PkIds,
            "TOrgIds": self.TOrgIds
        }
        res = ErpClient.CancelAllocate(self, formid="SAL_DELIVERYNOTICE", data=data)
        return (res)

    def UnAllocate(self, PrdIdString=0, OrgIdString=""):
        res = self.CancelAllocate(PrdIdString=PrdIdString, OrgIdString=OrgIdString)
        return (res)

    def ExcuteOperation(self, opNumber="Forbid", Numbers=[], CreateOrgId=0, Ids="", PkEntryIds=[], NetworkCtrl="",
                        IgnoreInterationFlag=""):
        self.opNumber = opNumber
        self.Numbers = Numbers
        self.CreateOrgId = CreateOrgId
        self.Ids = Ids
        self.PkEntryIds = PkEntryIds
        self.NetworkCtrl = NetworkCtrl
        self.IgnoreInterationFlag = IgnoreInterationFlag
        data = {
            "CreateOrgId": self.CreateOrgId,
            "Numbers": self.Numbers,
            "Ids": self.Ids,
            "PkEntryIds": self.PkEntryIds,
            "NetworkCtrl": self.NetworkCtrl,
            "IgnoreInterationFlag": self.IgnoreInterationFlag
        }
        res = ErpClient.ExcuteOperation(self, formid="SAL_DELIVERYNOTICE", opNumber=self.opNumber, data=data)
        return (res)

    def Disable(self, Numbers=[], CreateOrgId=0, Ids="", PkEntryIds=[], NetworkCtrl="", IgnoreInterationFlag=""):
        '''
        the Disable or Forbid operation of material.
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param PkEntryIds:
        :param NetworkCtrl:
        :param IgnoreInterationFlag:
        :return:
        '''
        res = self.ExcuteOperation(opNumber='Forbid', Numbers=Numbers, CreateOrgId=CreateOrgId, Ids=Ids,
                                   PkEntryIds=PkEntryIds, NetworkCtrl=NetworkCtrl,
                                   IgnoreInterationFlag=IgnoreInterationFlag)
        return (res)

    def Enable(self, Numbers=[], CreateOrgId=0, Ids="", PkEntryIds=[], NetworkCtrl="", IgnoreInterationFlag=""):
        '''
        the Enable of material.
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param PkEntryIds:
        :param NetworkCtrl:
        :param IgnoreInterationFlag:
        :return:
        '''
        res = self.ExcuteOperation(opNumber='Enable', Numbers=Numbers, CreateOrgId=CreateOrgId, Ids=Ids,
                                   PkEntryIds=PkEntryIds, NetworkCtrl=NetworkCtrl,
                                   IgnoreInterationFlag=IgnoreInterationFlag)
        return (res)


if __name__ == '__main__':
    pass