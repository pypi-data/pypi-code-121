from Scrapinger.Library.scrapingerGlobals import scrapingerGlobal
from netkeiber.Library.netkeiberConfig import netkeiberConfig

class netkeiberGlobal(scrapingerGlobal):
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ呼び出し
        super().__init__()
        
        self.netkeiberConfig:netkeiberConfig = None
        """ netkeiber共通設定 """

# インスタンス生成(import時に実行される)
gv = netkeiberGlobal()