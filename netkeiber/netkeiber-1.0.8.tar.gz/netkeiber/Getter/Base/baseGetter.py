from LibHanger.Models.recset import recset
from netkeiber.Library.netkeiberController import netkeibaBrowserController

class baseGetter(netkeibaBrowserController):
    
    """
    Getter基底
    """
    
    __dictResult = {}
    """ 処理結果 """

    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        super().__init__()

        self.__dictResult = {}
        
    @property
    def scrapingCount(self):
        
        """
        スクレイピング回数
        """
        
        return self.wdc.browserCtl.loadPageCount if not self.wdc.browserCtl is None else 0

    class getterResult():
        
        """
        Getter処理結果
        """
        
        def __init__(self, __recordCount:int, __recSet:recset):
        
            """
            コンストラクタ
            """
            
            self.recordCount:int = __recordCount
            """ 取得件数 """
            
            self.recSet:recset = __recSet
            """ 取得したレコードセット """
    
    def addResult(self, __key, __recordCount:int, __recSet:recset):
        
        """
        処理結果追加
        """
        
        self.__dictResult[__key] = self.getterResult(__recordCount, __recSet)
        
        return self.__dictResult
