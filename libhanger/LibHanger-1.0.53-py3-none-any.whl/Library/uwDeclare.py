from enum import Enum

class uwDeclare():
    
    """
    各種定義
    """
    
    class result(Enum):
        
        """
        処理結果
        """
        
        success = 0
        """ 成功 """
        
        warning = 1
        """ 警告 """
        
        critical = 2
        """ 致命的エラー """
        
    class resultRegister(Enum):
        
        """
        登録処理結果
        """
        
        success = 0
        """ 成功 """
        
        failure = 1
        """ 失敗 """
