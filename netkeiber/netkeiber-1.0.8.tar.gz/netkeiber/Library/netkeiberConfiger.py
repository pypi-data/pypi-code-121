from LibHanger.Library.uwGlobals import configer
from netkeiber.Library.netkeiberGlobals import *

class netkeiberConfiger(configer):
    
    """
    netkeiber共通設定クラス
    """
    
    def __init__(self, tgv:netkeiberGlobal, file, configFolderName):
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__(tgv, file, configFolderName)
        
        # netkeibar.ini
        da = netkeiberConfig()
        da.getConfig(file, configFolderName)

        # gvセット
        tgv.netkeiberConfig = da
        