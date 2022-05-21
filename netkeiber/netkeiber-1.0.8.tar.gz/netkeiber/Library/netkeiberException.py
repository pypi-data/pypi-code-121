import sys
import traceback
import uuid

class baseException(Exception):
    
    """
    例外クラス(基底)
    """
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        super().__init__()
        
        # 例外情報取得
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.__exc_type = exc_type
        self.__exc_value = exc_value
        self.__exc_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.__exc_uuid = str(uuid.uuid4())
    
    @property
    def exc_type(self):
        return self.__exc_type
    
    @property
    def exc_value(self):
        return self.__exc_value
    
    @property
    def exc_traceback(self):
        return self.__exc_traceback

    @property
    def exc_uuid(self):
        return self.__exc_uuid

class getterError(baseException):
    
    """
    getter例外クラス
    """
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        super().__init__()
    
    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "getter runtime error"

class registerError(baseException):
    
    """
    register例外クラス
    """
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        super().__init__()
    
    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "register runtime error"

class resultDataGenerateError(baseException):

    """
    検索結果生成時例外クラス
    """

    def __init__(self):

        """
        コンストラクタ
        """

        super().__init__()

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "Failed to generate search dictionary"
    
class arrivalOrderValueError(getterError):
    
    """
    着順構造体値エラー時例外クラス
    """
    
    def __init__(self):

        """
        コンストラクタ
        """

        super().__init__()

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "Arraival Order Value Error"
    
class racdIdCheckError(getterError):
    
    """
    レースIDチェックエラー例外クラス
    """
    
    def __init__(self):

        """
        コンストラクタ
        """

        super().__init__()

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "race_id is not digit"

class gettingValueError(getterError):
    
    """
    取得値エラー例外クラス
    """
    
    def __init__(self):

        """
        コンストラクタ
        """

        super().__init__()

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "value is invaild"
    
