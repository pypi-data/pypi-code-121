from enum import Enum
from LibHanger.Library.uwDeclare import uwDeclare

class netkeiberDeclare(uwDeclare):
    
    class getterResult(Enum):
        
        """
        取得処理結果
        """
        
        success = 0
        """ 正常 """
        
        error = 1
        """ エラーあり """

    class getStatus(Enum):
        
        """
        取得状況
        """
        
        unacquired = 0
        """ 未取得 """
        
        acquired = 1
        """ 取得済 """
        
    class refundKbn(Enum):
        
        """
        払戻区分
        """
        
        win = 0
        """ 単勝 """
        
        dwin = 1
        """ 複勝 """
        
        fcwin = 2
        """ 枠連 """
        
        hcwin = 3
        """ 馬連 """
        
        wdwin = 4
        """ ワイド """
        
        hswin = 5
        """ 馬単 """
        
        tdwin = 6
        """ 三連複 """
        
        tswin = 7
        """ 三連単 """
