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
from ..billModel import BillModel
import json
'''
* class definition for material object in ERP system
'''


class PrdMoRpt(ErpClient):
    def __init__(self, api_token='BEC6002E-C3AE-4947-AD70-212CF2B4218B',
                 meta_token="AD64F20D-6063-4E87-81E8-A24C1751D758",
                 timeout=120):
        self.api_token = api_token
        data_info = api_getInfo(api_token=self.api_token)
        print(data_info)
        self.acct_id = data_info['Facct_id']
        self.user_name = data_info['Fuser_name']
        print(self.user_name)
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
        data = {"FormId": "PRD_MORPT"}
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
        res = ErpClient.View(self, formid="PRD_MORPT", data=data)
        return (res)

    def Save_demo(self, FNumber='API-01', FName='demo-02'):
        self.FNumber = FNumber
        self.FName = FName
        data = {
                "Model": {
                    "BillNo": "SCHB2022050002",
                    "FBillType": {"FNUMBER": "SCHBD01_SYS"},
                    "FDocumentStatus": "A",
                    "FDate": "2022-05-19",
                    "FPrdOrgId": {"FNumber": "100"},
                    "FDescription": "",
                    "FEntity": [{
                        "FMaterialId": {"FNumber": "800788"},
                        "FProductType": "1",
                        "FReportType": {"FNumber": "HBLX01_SYS"},
                        "FUnitID": {"FNumber": "Pcs"},
                        "FWorkshipId": {"FNumber": "BM000040"},
                        "FCheckProduct": "true",
                        "FIsEntrust": "false",
                        "FSrcBillType": "PRD_MO",
                        "FMoBillNo": "MO202203632",
                        "FHumanQty": 0,
                        "FSrcBillNo": "MO202203632",
                        "FMachineQty": 0,
                        "FStartTime": "2022-05-19",
                        "FEndTime": "2022-05-19",
                        "FTimeUnitId": "1",
                        "FMoEntrySeq": 1,
                        "FStandHourUnitId": "3600",
                        "FStdManHour": 0,
                        "FHrPrepareTime": 0,
                        "FHrWorkTime": 0,
                        "FMacPrepareTime": 0,
                        "FMacWorkTime": 0,
                        "FSrcInterId": 136820,
                        "FSrcEntrySeq": 1,
                        "FMoId": 136820,
                        "FMoEntryId": 137488,
                        "FBaseUnitId": {"FNumber": "Pcs"},
                        "FStockInOrgId": {"FNumber": "100"},
                        "FBomId": {"FNumber": "800788_V1.0"},
                        "FOwnerTypeId": "BD_OwnerOrg",
                        "FOwnerId": {"FNumber": "100"},
                        "FCostRate": 100.0000000000,
                        "FISBACKFLUSH": "true",
                        "FMOMAINENTRYID": 137488,
                        "FStockInSelQty": 0,
                        "FBaseStockInSelQty": 0,
                        "FPickMtrlSelQty": 0,
                        "FBasePickMtrlSelQty": 0,
                        "FIsFirstinspect": "false",
                        "FEntity_Link": [{
                            "FEntity_Link_FRuleId": 'PRD_MO2MORPT',
                            "FEntity_Link_FSTableName": 'T_PRD_MOENTRY',
                            "FEntity_Link_FSBillId": '136820',
                            "FEntity_Link_FSId": "137488",
                            "FEntity_Link_FBaseUnitQtyOld": 1,
                            "FEntity_Link_FBaseUnitQty": 1,
                            "FEntity_Link_FStockBaseQtyOld": 1,
                            "FEntity_Link_FstockBaseQty": 1}]
            }
        ]
    }
}

        res = ErpClient.Save(self, formid="PRD_MORPT", data=data)
        return (res)

    def Save(self, FBillNo='so-api-002'):
        '''
        Save option is new material without materialID.
        :param data:
        :return:
        '''
        self.FBillNo = FBillNo
        app = BillModel(token=self.token, FFormId='PRD_MORPT', FActionName='Save')
        data = app.dataGen(FBillNo=self.FBillNo)
        print(data)
        res_str = ErpClient.Save(self, formid="PRD_MORPT", data=data)
        res_obj = json.loads(res_str)
        res = res_obj['Result']['ResponseStatus']['IsSuccess']
        return (res)

    def Modify(self, data):
        '''
        Modify is base on the Save option with aditional part is FMATERIALID
        :param data:
        :return:
        '''
        res = ErpClient.Save(self, formid="PRD_MORPT", data=data)
        return (res)

    def Query(self,FBillNo='XSDD22050025'):
        FieldKeys = "FBillNo,FID,FSaleOrderEntry_FEntryId"
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
            "FormId": "PRD_MORPT",
            "FieldKeys": self.FieldKeys,
            "FilterString": self.FilterString,
            "OrderString": self.OrderString,
            "TopRowCount": self.TopRowCount,
            "StartRow": self.StartRow,
            "Limit": self.Limit
        }
        res_str = ErpClient.ExecuteBillQuery(self, data=data)
        res = json.loads(res_str)
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
        res = ErpClient.BatchSave(self, formid='PRD_MORPT', data=save_data)
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
        res = ErpClient.BatchSaveQuery(self, formid='PRD_MORPT', data=save_data)
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
        res_str = ErpClient.Submit(self, formid="PRD_MORPT", data=data)
        res_obj = json.loads(res_str)
        res = res_obj['Result']['ResponseStatus']['IsSuccess']
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
        res = ErpClient.CancelAssign(self, formid="PRD_MORPT", data=data)
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
        res_str = ErpClient.Audit(self, formid="PRD_MORPT", data=data)
        res_obj = json.loads(res_str)
        res = res_obj['Result']['ResponseStatus']['IsSuccess']
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
        self.Save(FBillNo=FBillNo)
        self.Submit(FBillNo=FBillNo)
        res = self.Check(FBillNo=FBillNo)
        return(res)
    def ApiDel(self,FBillNo):
        self.UnCheck(FBillNo=FBillNo)
        res = self.Delete(FBillNo=FBillNo)
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
        res_str = ErpClient.UnAudit(self, formid="PRD_MORPT", data=data)
        res_obj = json.loads(res_str)
        res = res_obj['Result']['ResponseStatus']['IsSuccess']
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
        res_str = ErpClient.Delete(self, formid="PRD_MORPT", data=data)
        res_obj = json.loads(res_str)
        res = res_obj['Result']['ResponseStatus']['IsSuccess']
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
        res_str = ErpClient.Push(self,formid="PRD_MORPT",data=data)
        res_obj = json.loads(res_str)
        # print(res_obj)
        res = {}
        res['status'] = res_obj['Result']['ResponseStatus']['IsSuccess']
        if res['status']:
            res['FId'] = res_obj['Result']['ResponseStatus']['SuccessEntitys'][0]['Id']
            res['data'] = res_obj['Result']['ResponseStatus']['SuccessEntitys'][0]['Number']
        else:
            res['FId'] = 0
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
        res = ErpClient.Allocate(self, formid="PRD_MORPT", data=data)
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
        res = ErpClient.CancelAllocate(self, formid="PRD_MORPT", data=data)
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
        res = ErpClient.ExcuteOperation(self, formid="PRD_MORPT", opNumber=self.opNumber, data=data)
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