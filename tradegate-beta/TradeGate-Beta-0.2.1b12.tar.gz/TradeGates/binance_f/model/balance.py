class Balance:

    def __init__(self):
        self.asset = ""
        self.accountAlias = ""
        self.balance = 0.0
        self.withdrawAvailable = 0.0

    @staticmethod
    def json_parse(json_data):
        result = Balance()
        result.asset = json_data.get_string("asset")
        result.accountAlias = json_data.get_string("accountAlias")
        result.balance = json_data.get_float("balance")
        result.withdrawAvailable = json_data.get_float("withdrawAvailable")

        return result

    @staticmethod
    def makeFreeBalance(asset):
        outDict = {}
        
        outDict['asset'] = asset
        outDict['free'] = str(0.0)
        outDict['locked'] = str(0.0)

        return outDict


    def toDict(self):
        outDict = {}
        
        outDict['asset'] = self.asset
        outDict['free'] = str(self.withdrawAvailable)
        outDict['locked'] = str(self.balance - self.withdrawAvailable)

        return outDict
