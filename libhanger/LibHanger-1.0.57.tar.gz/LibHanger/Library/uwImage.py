import os
import textwrap
import LibHanger.Library.uwGetter as Getter
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class uwImage():
    
    """
    イメージ操作クラス
    """
    
    def __init__(self, rootPath, imageFileName, orgFolderPath = '', outputFolderPath = '') -> None:
        
        """
        コンストラクタ
        """
        
        # ルートパス
        self.rootPathFull = rootPath
        self.rootPath = os.path.dirname(rootPath)

        # ファイル名
        self._imageFileName = imageFileName
        
        # オリジナルフォルダパス
        self._orgFolderPath = orgFolderPath
        
        # 出力先フォルダパス
        self._outputFolderPath = outputFolderPath
        
        # 出力先ファイルパス
        self._imageOutputPath = self.getOutputImagePath()
        
        # イメージ
        self._image = Image.open(self.getOrgImagePath())
        
        # フォント
        self._font = None
        
    def getOrgImagePath(self):
        
        """
        オリジナルイメージのパスを取得する
        """

        return os.path.join(self.rootPath, self._orgFolderPath, self._imageFileName)

    def getOutputImagePath(self):
        
        """
        リサイズ後イメージのパスを取得する
        """

        # リサイズフォルダ未指定の場合はオリジナルイメージと同じ位置にファイル名を変更して出力する
        resizeimageFileName = self._imageFileName
        if self._outputFolderPath == '':
            nowDatetimeString = Getter.getNow(Getter.datetimeFormat.yyyyMMddhhmmss)
            fileExt = Path(self._imageFileName).suffix
            fileNonExt = Path(self._imageFileName).stem
            resizeimageFileNameFormat = '{0}_resize_{1}' + fileExt
            resizeimageFileName = resizeimageFileNameFormat.format(fileNonExt, nowDatetimeString)
        
        return os.path.join(self.rootPath, self._outputFolderPath, resizeimageFileName)
    
    def Resize(self, width):
    
        """
        イメージをリサイズする(アスペクト比固定)
        """
        
        # イメージをリサイズする
        self._image = self.Resize_Image(width)

    def Resize_Image(self, width):
        
        """
        イメージをリサイズする(アスペクト比固定)
        """
        
        # 画像のリサイズ
        return self._image.resize((width, int(width * self._image.size[1] / self._image.size[0]))) 
    
    def setFont(self, fontFilePath, size):
        
        """
        フォント設定
        """
        
        self._font = ImageFont.truetype(os.path.join(self.rootPath,fontFilePath), size)
    
    def insertText(self, insertText, insertPoint:tuple, indentationYPoint, textHeight, fontColor=(255,255,255)):
        
        """
        イメージにテキストを挿入する
        """
        
        # テキストを14文字で改行しリストwrap_listに代入
        wrap_list = textwrap.wrap(insertText, indentationYPoint)

        # 行数カウンター
        line_counter = 0  

        # drawオブジェクトを生成
        draw = ImageDraw.Draw(self._image)

        # wrap_listから1行づつ取り出しlineに代入
        for line in wrap_list:
            
            # y座標をline_counterに応じて下げる
            y = (line_counter * textHeight) + insertPoint[1]
            # 1行分の文字列を画像に描画
            draw.multiline_text((insertPoint[0], y),line, fill=fontColor, font=self._font)
            # 行数カウンターup
            line_counter += 1
            
    def saveImage(self):
        
        """
        イメージを保存する
        """
        
        # 画像の保存
        self._image.save(self._imageOutputPath)
        
        # 保存先パスを返す
        return self._imageOutputPath
    