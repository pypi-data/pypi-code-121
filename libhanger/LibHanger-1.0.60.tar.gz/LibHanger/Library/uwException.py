
import os
import traceback

def writeErrorLog(outputFilePath, errorText):
    
    """
    エラーログ出力
    
    Parameters
    ----------
    outputFilePath : str
        ログ出力先パス
    errorText : str
        エラー内容
    """

    # エラーログの出力先がない場合、作成する
    if os.path.exists(outputFilePath) == False:
        os.mkdir(outputFilePath)
    
    # エラー出力
    with open(outputFilePath, 'a') as f:
        traceback.print_exc(file=f)
        f.write(errorText)

class iniFilePathError(Exception):

    """
    設定ファイル(config.ini)エラー例外
    """

    def __init__(self):

        """
        コンストラクタ
        """

        pass

    def __str__(self):
        
        """
        例外をプリントした時に出力する文字列
        """

        return "config.ini Not Found"