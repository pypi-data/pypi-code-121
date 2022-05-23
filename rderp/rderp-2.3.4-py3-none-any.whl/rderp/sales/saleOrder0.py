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
from ..model import Model
'''
* class definition for material object in ERP system
'''


class SaleOrder(ErpClient):
    def __init__(self, acct_id, user_name, app_id, app_secret, server_url, token="AD64F20D-6063-4E87-81E8-A24C1751D758",
                 timeout=120):
        self.acct_id = acct_id
        self.user_name = user_name
        self.app_id = app_id
        self.app_secret = app_secret
        self.server_url = server_url
        self.timeout = timeout
        self.token = token
        ErpClient.__init__(self, acct_id=self.acct_id, user_name=self.user_name, app_id=self.app_id,
                           app_secret=self.app_secret, server_url=self.server_url, timeout=self.timeout)

    def Meta(self):
        '''
        query the business info or metadata info for material.
        :return:
        '''
        data = {"FormId": "SAL_SaleOrder"}
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
        res = ErpClient.View(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def Save_demo(self, FNumber='API-01', FName='demo-02'):
        self.FNumber = FNumber
        self.FName = FName
        data = {"Model": {
            "FBillTypeID": {"FNUMBER": "XSDD01_SYS"},
            "FBillNo": "so-api-002",
            "FDate": "2022-04-16 00:00:00",
            "FSaleOrgId": {"FNumber": "100"},
            "FCustId": {"FNumber": "100011"},
            "FHeadDeliveryWay": {"FNumber": "JHFS01_SYS"},
            "FReceiveId": {"FNumber": "100011"},
            "FHEADLOCID": {"FNumber": "BIZ202103081002351"},
            "FSaleDeptId": {"FNumber": "BM000003"},
            "FSaleGroupId": {"FNumber": "XS021"},
            "FSalerId": {"FNumber": "HR043_GW000052_1"},
            "FSettleId": {"FNumber": "100011"},
            "FChargeId": {"FNumber": "100011"},
            # "FISINIT": 'false',
            # "FIsMobile": 'false',
             "F_RQAE_Commission": 'false',
             "F_RQAE_HC": 'false',
             "F_RQAE_AC": 'false',
            "F_SZSP_XSLX": {"FNumber": "1"},
            "F_SZSP_JJCD": {"FNumber": "JJ"},
            "F_SZSP_NMJSY": "个人客户",
            "FSaleOrderFinance": {
                "FSettleCurrId": {"FNumber": "PRE001"},
                "FRecConditionId": {"FNumber": "SKTJ01_SP"},
                "FIsPriceExcludeTax": 'true',
                "FSettleModeId": {"FNumber": "JSFS04_SYS"},
                "FIsIncludedTax": 'true',
                "FExchangeTypeId": {"FNumber": "HLTX01_SYS"}
                #,
                # "FOverOrgTransDirect": 'false'
            },
            "FSaleOrderEntry": [
                {"FRowType": "Standard",
                "FMaterialId": {"FNumber": "300201-1"},
                "FUnitID": {"FNumber": "carton"},
                "FQty": 200.0,
                "FPriceUnitId": {"FNumber": "carton"},
                "FPrice": 442.477876,
                "FTaxPrice": 500.0,
                "FIsFree": 'false',
                "FEntryTaxRate": 13.00,
                "FDeliveryDate": "2022-04-16 17:20:04",
                "FStockOrgId": {"FNumber": "100"},
                "FSettleOrgIds": {"FNumber": "100"},
                "FSupplyOrgId": {"FNumber": "100"},
                "FOwnerTypeId": "BD_OwnerOrg",
                "FOwnerId": {"FNumber": "100"},
                "F_SZSP_YWTC": 50.00,
                "FReserveType": "1",
                "FPriceBaseQty": 200.0,
                # "FStockUnitID": {"FNumber": "carton"},
                # "FStockQty": 200.0,
                # "FStockBaseQty": 200.0,
                # "FOUTLMTUNIT": "SAL",
                # "FOutLmtUnitID": {"FNumber": "carton"},
                "FISMRP": 'false',
                "F_SZSP_FSPC1": 'false',
                "FAllAmountExceptDisCount": 100000.0,
                "F_SZSP_ZLTC": 5.56
                    # ,
                # "FOrderEntryPlan": [{
                #     "FDetailLocId": {"FNumber": "BIZ202103081002351"},
                #     "FPlanDate": "2022-04-16 17:20:04",
                #     "FPlanQty": 200.0
                #     }]
                },
                {
                "FRowType": "Standard",
                "FMaterialId": {"FNumber": "300203-1"},
                "FUnitID": {"FNumber": "carton"},
                "FQty": 400.0,
                "FPriceUnitId": {"FNumber": "carton"},
                "FPrice": 530.973451,
                "FTaxPrice": 600.0,
                "FIsFree": 'false',
                "FEntryTaxRate": 13.00,
                "FDeliveryDate": "2022-04-16 17:20:26",
                "FStockOrgId": {"FNumber": "100"},
                "FSettleOrgIds": {"FNumber": "100"},
                "FSupplyOrgId": {"FNumber": "100"},
                "FOwnerTypeId": "BD_OwnerOrg",
                "FOwnerId": {"FNumber": "100"},
                "F_SZSP_YWTC": 120.00,
                "FReserveType": "1",
                "FPriceBaseQty": 400.0,
                # "FStockUnitID": {"FNumber": "carton"},
                # "FStockQty": 400.0,
                # "FStockBaseQty": 400.0,
                # "FOUTLMTUNIT": "SAL",
                # "FOutLmtUnitID": {"FNumber": "carton"},
                "FISMRP": 'false',
                "F_SZSP_FSPC1": 'false',
                "FAllAmountExceptDisCount": 240000.0,
                "F_SZSP_ZLTC": 13.33
                #    ,
                # "FOrderEntryPlan": [{
                #     "FDetailLocId": {"FNumber": "BIZ202103081002351"},
                #     "FPlanDate": "2022-04-16 17:20:26",
                #     "FPlanQty": 400.0
                #     }]
                }
                ],
                "FSaleOrderPlan": [
                    {
                    "FNeedRecAdvance": 'true',
                    "FRecAdvanceRate": 10.0000000000,
                    "FRecAdvanceAmount": 34000.00,
                    "FIsOutStockByRecamount": 'false'
                    },
                    {
                        "FNeedRecAdvance": 'false',
                        "FRecAdvanceRate": 90.0000000000,
                        "FRecAdvanceAmount": 306000.00,
                        "FIsOutStockByRecamount": 'false'
                    }
                ]
            }
            }
        res = ErpClient.Save(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def Save(self, sql_where="FNumber = 'api-02'"):
        '''
        Save option is new material without materialID.
        :param data:
        :return:
        '''
        app = Model(token=self.token, FFormId='SAL_SaleOrder', FActionName='Save')
        data = app.dataGen(sql_where=sql_where)
        res = ErpClient.Save(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def Modify(self, data):
        '''
        Modify is base on the Save option with aditional part is FMATERIALID
        :param data:
        :return:
        '''
        res = ErpClient.Save(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def Query(self, FieldKeys="FName,FNumber",
              FilterString="FNumber in ('Webb2021083117391510001','Webb2021083117400510001','Webb2021083117401510001')",
              OrderString="", TopRowCount=0, StartRow=0, Limit=0):
        '''
        query the list of material.
        :param FieldKeys:
        :param FilterString:[{"Left":"(","FieldName":"Field1","Compare":"=","Value":"111","Right":")","Logic":"AND"},{"Left":"(","FieldName":"Field2","Compare":"=","Value":"222","Right":")","Logic":""}]
            1、Left：左括号
            2、FieldName：字段名
            3、Compare：比较运算符，如　大于">"、小于"<"、等于"="、包含"like"、左包含"llike"、右包含"rlike"
            4、Value：比较值
            5、Right：右括号
            6、Logic：逻辑运算符，如 "and"、"or"
        :param OrderString:
        :param TopRowCount:
        :param StartRow:
        :param Limit:
        :return:
        '''
        self.FieldKeys = FieldKeys
        self.FilterString = FilterString
        self.OrderString = OrderString
        self.TopRowCount = TopRowCount
        self.StartRow = StartRow
        self.Limit = Limit
        data = {
            "FormId": "SAL_SaleOrder",
            "FieldKeys": self.FieldKeys,
            "FilterString": self.FilterString,
            "OrderString": self.OrderString,
            "TopRowCount": self.TopRowCount,
            "StartRow": self.StartRow,
            "Limit": self.Limit
        }
        res = ErpClient.ExecuteBillQuery(self, data=data)

    def SaveBatch(self, data_list):
        '''
        *save the data in a batch list
        *put multiple save format data into a list
        :param data_list:
        :return:
        '''
        self.data_list = data_list
        save_data = {"Model": self.data_list}
        res = ErpClient.BatchSave(self, formid='SAL_SaleOrder', data=save_data)
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
        res = ErpClient.BatchSaveQuery(self, formid='SAL_SaleOrder', data=save_data)
        return (res)

    def Submit(self, Numbers=[], Ids="", SelectedPostId=0, NetworkCtrl="", IgnoreInterationFlag=""):
        '''
        * the material Submit operation just after save.
        :param Numbers: list of material numbers
        :param Ids:   the Ids of material
        :param SelectedPostId: the SelectedPostId of material
        :param NetworkCtrl:  the NetworkCtrl status of material
        :param IgnoreInterationFlag: the Flag of material
        :return: without the return value or the status of Submit after exec.
        '''
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
        res = ErpClient.Submit(self, formid="SAL_SaleOrder", data=data)
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
        res = ErpClient.CancelAssign(self, formid="SAL_SaleOrder", data=data)
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

    def Audit(self, Numbers=[], CreateOrgId=0, Ids="", InterationFlags="", NetworkCtrl="", IsVerifyProcInst="",
              IgnoreInterationFlag=""):
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
        res = ErpClient.Audit(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def Check(self, Numbers=[], CreateOrgId=0, Ids="", InterationFlags="", NetworkCtrl="", IsVerifyProcInst="",
              IgnoreInterationFlag=""):
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
        res = self.Audit(Numbers=Numbers, CreateOrgId=CreateOrgId, Ids=Ids, InterationFlags=InterationFlags,
                         NetworkCtrl=NetworkCtrl, IsVerifyProcInst=IsVerifyProcInst,
                         IgnoreInterationFlag=IgnoreInterationFlag)
        return (res)

    def UnAudit(self, Numbers=[], CreateOrgId=0, Ids="", InterationFlags="", NetworkCtrl="", IsVerifyProcInst="",
                IgnoreInterationFlag=""):
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
        res = ErpClient.UnAudit(self, formid="SAL_SaleOrder", data=data)
        return (res)

    def UnCheck(self, Numbers=[], CreateOrgId=0, Ids="", InterationFlags="", NetworkCtrl="", IsVerifyProcInst="",
                IgnoreInterationFlag=""):
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
        res = self.UnAudit(Numbers=Numbers, CreateOrgId=CreateOrgId, Ids=Ids, InterationFlags=InterationFlags,
                           NetworkCtrl=NetworkCtrl, IsVerifyProcInst=IsVerifyProcInst,
                           IgnoreInterationFlag=IgnoreInterationFlag)
        return (res)

    def Delete(self, Numbers=[], CreateOrgId=0, Ids="", NetworkCtrl=""):
        '''
        the Delete operation of material
        :param Numbers:
        :param CreateOrgId:
        :param Ids:
        :param NetworkCtrl:
        :return:
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
        res = ErpClient.Delete(self, formid="SAL_SaleOrder", data=data)
        return (res)

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
        res = ErpClient.Allocate(self, formid="SAL_SaleOrder", data=data)
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
        res = ErpClient.CancelAllocate(self, formid="SAL_SaleOrder", data=data)
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
        res = ErpClient.ExcuteOperation(self, formid="SAL_SaleOrder", opNumber=self.opNumber, data=data)
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