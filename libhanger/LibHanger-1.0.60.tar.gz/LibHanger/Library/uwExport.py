import os
import json

class BaseExport():
    
    """
    エクスポートクラス基底
    """
    
    pass

class ExcelExporter(BaseExport):
    
    """
    Excelエクスポートクラス
    """
    
    pass

class JsonExporter(BaseExport):
    
    """
    Jsonファイルエクスポートクラス
    """
    
    def __init__(self, __file__) -> None:
        
        """
        コンストラクタ
        """

        super().__init__()

        self.rootPath = os.path.dirname(__file__)
        """ ルートパス """
        
    def putJsonFile(self, output_dir, fileName, data_dict):
        
        """
        dict型データをjsonファイルに出力する

        Parameters
        ----------
        output_dir : str
            出力先ディレクトリ
        fileName : str
            ファイル名
        data_dict : dict
            出力対象dict型データ
            
        """
        
        # jsonファイル出力
        with open(os.path.join(output_dir, fileName), 'w', newline='', encoding='utf-8') as f:
            f.write(json.dumps(data_dict, ensure_ascii = False, indent = 4))
        
        # ファイルClose
        f.close()

    