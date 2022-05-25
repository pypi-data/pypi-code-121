import baostock as bs
from IutyLib.file.files import CsvFile

class BaoStock:
    loginflg = False
    def login(self):
        if not self.loginflg:
            bs.login()
            self.loginflg = True
        pass
    
    def logout(self):
        bs.logout()
        self.loginflg = False
        pass
    
    def getKLineByCode(self,code,start="2000-1-1"):
        self.login()
        cd = "sz."+code
        if code[0] == "6":
            cd = "sh."+code
        rst = bs.query_history_k_data_plus(cd,"date,open,high,low,close,amount,volume,turn",start)
        return rst
    
    def writeCsvFile(self,root,code):
        rst = self.getKLineByCode(code)
        data = []
        while (rst.error_code == "0") & rst.next():
            data.append(rst.get_row_data())
        csv = CsvFile(code,root)
        csv.delete()
        csv.appends(data)
        
        pass
    
    def getKLineLocal(self,root,code):
        csv = CsvFile(code,root)
        kline = csv.getData()
        return kline


if __name__ == "__main__":
    
    ins = BaoStock()
    #ins.writeCsvFile(r"e:/data/test","600703")
    print(len(ins.getKLineLocal(root= r"e:/data/kline",code="600703")))