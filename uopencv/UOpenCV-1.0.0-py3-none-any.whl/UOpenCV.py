# -*- coding:utf-8 -*-

# UOpenCV 画像処理用ビットマップクラス
# (C)Copyright 2004,05,06,07,08,10,11,2022 Y.Endou All rights reserved

# 更新履歴
# 1.0    22/10/01    opencv-pythonのラッパーとして全面改定
#                    UBitmapからUOpenCVと改名
#                    バージョン番号リセット
# 5.4    11/03/20    C++Builder用の最後のバージョン
# 5.0    07/11/14    カラーとグレースケールのクラスを統合した
# 4.0    06/02/15    カラー・グレースケール処理等ごっちゃになっていたのを分離
# 3.0    04/06/16    AT-Image ver.2.5のTForm2クラスを全面改定し、クラス(UBitmap)として独立させた
#                    BorlandのVCLのクラス名が「T」から始まるので「U」Bitmapと名付けた
#                    バージョンはAT-Imageと合わせるために3.0から始まる
#                    C++Builder用のクラスライブラリ
# 2.0    99/05/05    AT-Imageの仕様の全面見直し(MDI化、その他)
# 1.0    98/05/14    AT-Image(画像処理ソフト) 初期バージョン
#                    C++Builderで作ったソフトウエア

import warnings
import os
import xml.etree.ElementTree as et # xml.etree.ElementTreeは日本語が通る。openCVは日本語が通らない(ver.4.5)(2022/01/27)

import cv2
import numpy as np  # openCVの画像入出力が日本語に対応していないのでnumpyを使う(2022/01/27)
# --------------------------------------------------
class UOpenCV:
    """UOpenCVをラッパーした画像処理クラス
    """
    # クラス変数の定義
    __soft_name__   = 'UOpenCV'
    __version__     = '1.0' # バージョン番号
    __description__ = 'opencv-pythonのラッパークラス'
    __copyright__   = '(C)Copyright 2004,05,06,07,08,10,11,2022 Y.Endou All rights reserved'
    # 派生クラスでも参照できる。UOpenCV.__version__ などと参照
    # すべてのオブジェクトに共通
    # アクセス制限がないので、変更もできる
# -------------------------
# コンストラクタ
# -------------------------
    def __init__(self,filename: str=None):
        """コンストラクタ
        @param str filename ファイル名　引数にファイル名があれば入力する
        """
        # (疑似)プロテクテッド変数=外部からアクセスできてしまう
        # プログラムからはプロパティーで参照する
        self._bitmap = None          # opencvの画像データ
        self._name: str = ""         # 画像名
        self._kind: str = "no_data"  # 画像種別 enum('no_data','color','gray','binary','fft',...)
        self._log: list = list()     # 処理履歴
        if filename is not None:     # 関数のオーバーロードができないのは型が厳密ではないためなのか
            self.imread(filename)
# -------------------------
# プロパティー
# -------------------------
    def getbitmap(self):
        return self._bitmap

    def getname(self):
        return self._name

    def getkind(self):
        return self._kind

    def getshape(self):
        return self._bitmap.shape

    def getwidth(self):
        return self._bitmap.shape[1]

    def getheight(self):
        return self._bitmap.shape[0]

    def getndim(self):
        return self._bitmap.ndim

    def getlog(self):
        return self._log

    def getchannel(self):
        if len(self._bitmap.shape) == 2:
            return 1
        else:
            return self._bitmap.shape[2]  # 必ずしもチャンネル数を表していない

    bitmap  = property(getbitmap)
    name    = property(getname)
    kind    = property(getkind)
    shape   = property(getshape)
    width   = property(getwidth)
    height  = property(getheight)
    ndim    = property(getndim)
    channel = property(getchannel)
    log     = property(getlog)
# -------------------------
# 入出力
# -------------------------
    def imread(self, filename: str):
        """画像入力 読み込めるファイルの形式は numpy の許すファイル
        読めない場合は例外を発生
        cv2.imreadはパスに日本語が入ると読み込めない(ver.4.5)(2022/01/27)
        @paran str filename 画像名
        @link https://qiita.com/SKYS/items/cbde3775e2143cad7455 (2022/01/01)
        """
        buff = np.fromfile(filename, np.uint8)  # 読めなければ例外が発生する 画像ファイル以外も読み込める
        self._bitmap = cv2.imdecode(buff, cv2.IMREAD_COLOR)
        if self._bitmap is None:
            raise Exception('指定されたファイルは画像ではありません')
        self._name = filename
        self._kind = "color"
        self._log  = list()
        self._log.append(os.path.basename(filename))

        return self # メソッドチェーンを作るため self を返す
# -------------------------
    def imreads(self, dir: str):
        """積分入力
        ディレクトリにある画像ファイルを全て読み込んで平均を取る
        画像はすべて同じ大きさ
        @param str dir: ディレクトリの名前
        fastNlMeansDenoisingColoredMulti が用意されている
        """
        raise NotImplementedError()
# -------------------------
    def imwrite(self, filename: str):
        """画像出力
        ファイルに保存　形式は拡張子で自動的に判別される。PNG形式を推奨
        書き込めない場合は例外を発生
        cv2.imwriteはパスに日本語が入ると画像名が文字化けするので、cv2.imencode を利用してフォーマットを整え、ファイル出力している
        @param str filename: 画像名
                            ディレクトリを作ることはできない
        @link https://qiita.com/SKYS/items/cbde3775e2143cad7455 (2022/01/01)
        """
        ext = os.path.splitext(filename)[1]
        result, buff = cv2.imencode(ext, self._bitmap)  # 拡張子に応じてフォーマットを変えてくれる
        if result:
            with open(filename, mode='w+b') as fd:  # ディレクトリを作ることはできない
                buff.tofile(fd)
            fd.close()
            self._name = filename  # 保存したら名前と履歴をクリアする
            self._log  = list()
            self._log.append(os.path.basename(filename))

        return self
# -------------------------
    def load_clipboard(self):
        """クリップボードから画像データをコピー
        """
        raise NotImplementedError()
# -------------------------
    def save_clipboard(self):
        """クリップボードへ画像データをコピー
        """
        raise NotImplementedError()
# -------------------------
# 画素アクセス
# -------------------------
    def getpixel(self, x: int , y:int):
        """(x,y)の画素の値を得る
        @param int (x,y) 座標
        @return ピクセルの値
        """
        if self._kind == 'fft':
            return self._fft_complex[y , x]
        else:
            return self._bitmap[y , x]
# -------------------------
    def setpixel(self, x: int, y: int, b: int, g: int=0, r: int=0):
        """(x,y)の画素に値を入れる
        @param int (x,y) 座標
        @param int (b,g,r) 値
        """
        if self._kind == 'color':
            self._bitmap[y , x] = [b, g, r]
        else:
            self._bitmap[y , x] = b
#    pixel = property(getpixel, setpixel)  # うまく動かなかった
# -------------------------
# 画像計測
# -------------------------
    def get3data(self, x: int, y: int):
        """3近傍のデータを得る
        1行(Y軸)ごとにnp.ndarrayで出力される
        2次元データの場合 data[y][x]でアクセス
        3次元データの場合 data[y][x][B|G|R]でアクセス
        img[top : bottom , left : right]でスライスする
        @param int (x,y) 中心座標
        @return np.ndarray 
        """
        if self._kind == 'fft':
            img = cv2.copyMakeBorder(self._fft_complex, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.copyMakeBorder(self._bitmap,      1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

        x = x + 1
        y = y + 1
        top    = y - 1
        bottom = y + 1 + 1 # スライスは top以上bottom未満なので +1 する
        left   = x - 1
        right  = x + 1 + 1
        return img[top : bottom , left : right]
# -------------------------
    def get7data(self, x: int, y: int):
        """7近傍のデータを得る
        1行(Y軸)ごとにnp.ndarrayで出力される
        2次元データの場合 data[y][x]でアクセス
        3次元データの場合 data[y][x][B|G|R]でアクセス
        @param int (x,y) 中心座標
        @return np.ndarray 
        """
        if self._kind == 'fft':
            img = cv2.copyMakeBorder(self._fft_complex, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.copyMakeBorder(self._bitmap,      3, 3, 3, 3, cv2.BORDER_CONSTANT, value=0)

        x = x + 3
        y = y + 3
        top    = y - 3
        bottom = y + 3 + 1 # スライスは top以上bottom未満なので +1 する
        left   = x - 3
        right  = x + 3 + 1
        return img[top : bottom , left : right]
# -------------------------
    def get_line_data(self, bx: int, by: int, ex: int, ey: int):
        """線上のデータを得る
        @param int (bx,by) 始点
        @param int (ex,ey) 終点
        @return self.x_axis , self.y_axis 軸
                self.value_b  gray , binary , HSLなど1チャンネルのみの画像
                              color(b) , fft(real) データ
                self.value_g  color(g) , fft(imaginary) データ
                self.value_r  color(r) データ
        """
        ax = ex - bx # 媒介変数で計算
        ay = ey - by
        r  = np.sqrt(ax * ax + ay * ay)
        if r == 0.0:
            raise Exception('始点と終点が同じです')
        ax = ax / r
        ay = ay / r
        n  = int(r)

        if self._kind == 'fft':
            src = self._fft_complex.tolist()
        else:
            src = self._bitmap.tolist()  # numpyの配列要素へのアクセスは遅いのでlistにしてアクセスする

        # 集計
        x_axis  = list()  # 処理の途中に、コンストラクタで定義していないメンバ（インスタンス）を追加できるのは便利だけれども、気味が悪い
        y_axis  = list()
        value_b = list()
        value_g = list()
        value_r = list()

        for i in range(0, n):
            cx = int(i * ax + bx)
            cy = int(i * ay + by)
            if cx < 0 or self.width <= cx + 1 or cy < 0 or self.height <= cy + 1:
                continue
            if self._kind == 'color':
                value_b.append(src[cy][cx][0])
                value_g.append(src[cy][cx][1])
                value_r.append(src[cy][cx][2])
            elif self._kind == 'fft':
                value_b.append(src[cy][cx][0])
                value_g.append(src[cy][cx][1])
            else:
                value_b.append(src[cy][cx])
            x_axis.append(cx)
            y_axis.append(cy)

        # 統計
        self.x_axis  = np.array(x_axis)   # 統計のために numpy データに変換する
        self.y_axis  = np.array(y_axis)
        self.value_b = np.array(value_b)
        self.value_g = np.array(value_g)
        self.value_r = np.array(value_r)

        if self._kind == 'color':
            self.mean_b   = np.mean(self.value_b) # 平均、標準偏差、中央値、最大値、最小値の計算
            self.std_b    = np.std(self.value_b)
            self.median_b = np.median(self.value_b)
            self.max_b    = np.max(self.value_b)
            self.min_b    = np.min(self.value_b)
            st_b = [self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]

            self.mean_g   = np.mean(self.value_g)
            self.std_g    = np.std(self.value_g)
            self.median_g = np.median(self.value_g)
            self.max_g    = np.max(self.value_g)
            self.min_g    = np.min(self.value_g)
            st_g = [self.mean_g, self.std_g, self.median_g, self.max_g, self.min_g]

            self.mean_r   = np.mean(self.value_r)
            self.std_r    = np.std(self.value_r)
            self.median_r = np.median(self.value_r)
            self.max_r    = np.max(self.value_r)
            self.min_r    = np.min(self.value_r)
            st_r = [self.mean_r, self.std_r, self.median_r, self.max_r, self.min_r]
            self.dist_stat = [st_b, st_g, st_r]

        elif self._kind == 'fft':
            del self.value_r
            self.mean_b   = np.mean(self.value_b)
            self.std_b    = np.std(self.value_b)
            self.median_b = np.median(self.value_b)
            self.max_b    = np.max(self.value_b)
            self.min_b    = np.min(self.value_b)
            st_b = [self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]

            self.mean_g   = np.mean(self.value_g)
            self.std_g    = np.std(self.value_g)
            self.median_g = np.median(self.value_g)
            self.max_g    = np.max(self.value_g)
            self.min_g    = np.min(self.value_g)
            st_g = [self.mean_g, self.std_g, self.median_g, self.max_g, self.min_g]
            self.dist_stat = [st_b, st_g]

        else:
            del self.value_g
            del self.value_r
            self.mean_b   = np.mean(self.value_b)
            self.std_b    = np.std(self.value_b)
            self.median_b = np.median(self.value_b)
            self.max_b    = np.max(self.value_b)
            self.min_b    = np.min(self.value_b)
            self.dist_stat = [[self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]]

        return self
# -------------------------
    def calcHist(self, bx:int=0, by:int=0, ex:int=0, ey:int=0):
        """ヒストグラムを集計する
        @param int (bx, by)->(ex,ey) 指定範囲
        引数を省略した場合(すべて 0 の場合)は、全領域
        @return self.hist_b , self.hist_g , self.hist_r  ヒストグラムのデータ
        @return list self.dist_array  集計結果をリストにしたもの
        @return list self.dist_stat   平均、標準偏差、中央値をリストにしたもの
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_histograms/py_histogram_begins/py_histogram_begins.html (2022/01/01)
        """
        if bx == 0 and by == 0 and ex == 0 and ey == 0:  # 引数を省略した場合は全領域
            ex = self.width
            ey = self.height

        # マスク画像を作る
        mask = np.zeros(self._bitmap.shape[:2], np.uint8)
        mask[by:ey, bx:ex] = 255
        #    行,    列
        # ヒストグラムを返す
        if self._kind == 'color':
            self.hist_b = cv2.calcHist([self._bitmap], [0], mask, [256], [0, 256])
            self.hist_g = cv2.calcHist([self._bitmap], [1], mask, [256], [0, 256])
            self.hist_r = cv2.calcHist([self._bitmap], [2], mask, [256], [0, 256])
            self.dist_array = [self.hist_b, self.hist_g, self.hist_r]  # B, G, Rの順であることに注意

            self.mean_b   = np.mean(self._bitmap[by:ey, bx:ex, 0])  # 平均、標準偏差、中央値
            self.std_b    = np.std(self._bitmap[by:ey, bx:ex, 0])
            self.median_b = np.median(self._bitmap[by:ey, bx:ex, 0])
            st_b = [self.mean_b, self.std_b, self.median_b]

            self.mean_g   = np.mean(self._bitmap[by:ey, bx:ex, 1])
            self.std_g    = np.std(self._bitmap[by:ey, bx:ex, 1])
            self.median_g = np.median(self._bitmap[by:ey, bx:ex, 1])
            st_g = [self.mean_g, self.std_g, self.median_g]

            self.mean_r   = np.mean(self._bitmap[by:ey, bx:ex, 2])
            self.std_r    = np.std(self._bitmap[by:ey, bx:ex, 2])
            self.median_r = np.median(self._bitmap[by:ey, bx:ex, 2])
            st_r = [self.mean_r, self.std_r, self.median_r]
            self.dist_stat = [st_b, st_g, st_r]

        else:
            self.hist_b = cv2.calcHist([self._bitmap], [0], mask, [256], [0, 256])
            self.dist_array = [self.hist_b]

            self.mean_b   = np.mean(self._bitmap[by:ey, bx:ex])
            self.std_b    = np.std(self._bitmap[by:ey, bx:ex])
            self.median_b = np.median(self._bitmap[by:ey, bx:ex])
            self.dist_stat = [[self.mean_b, self.std_b, self.median_b]]

        return self
# -------------------------
    def projection_distribution_h(self, bx:int=0, by:int=0, ex:int=0, ey:int=0):
        """水平方向周辺分布
        @param (bx, by)->(ex,ey) 指定範囲
        引数を省略した場合(すべて 0 の場合)は、全領域
        @return self.array_y , self.array_b , self.array_g , self.array_r  ヒストグラムのデータ
        @return list self.dist_array  集計結果をリストにしたもの
        @return list self.dist_stat   平均、標準偏差、中央値、最大値、最小値をリストにしたもの
        @link https://note.nkmk.me/python-numpy-ndarray-slice/ (2022/01/01)
        """
        if bx == 0 and by == 0 and ex == 0 and ey == 0:  # 引数を省略した場合は全領域
            ex = self.width
            ey = self.height

        height = ey - by # 指定範囲の高さ
        if self._kind == 'color':
            self.array_b = np.zeros(height) # 周辺分布のリスト
            self.array_g = np.zeros(height)
            self.array_r = np.zeros(height)
            self.array_y = np.zeros(height) # Y座標のリスト
            for y in range(by,ey):
                self.array_b[y-by] = np.sum(self._bitmap[y,bx:ex,0])  # @link https://note.nkmk.me/python-numpy-ndarray-slice/ (2022/01/01)
                self.array_g[y-by] = np.sum(self._bitmap[y,bx:ex,1])
                self.array_r[y-by] = np.sum(self._bitmap[y,bx:ex,2])
                self.array_y[y-by] = y
            self.dist_array = [self.array_b, self.array_g, self.array_r, self.array_y]  # B, G, R, Y軸の順であることに注意

            self.mean_b   = np.mean(self.array_b) # 平均、標準偏差、中央値、最大値、最小値の計算
            self.std_b    = np.std(self.array_b)
            self.median_b = np.median(self.array_b)
            self.max_b    = np.max(self.array_b)
            self.min_b    = np.min(self.array_b)
            st_b = [self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]

            self.mean_g   = np.mean(self.array_g)
            self.std_g    = np.std(self.array_g)
            self.median_g = np.median(self.array_g)
            self.max_g    = np.max(self.array_g)
            self.min_g    = np.min(self.array_g)
            st_g = [self.mean_g, self.std_g, self.median_g, self.max_g, self.min_g]

            self.mean_r   = np.mean(self.array_r)
            self.std_r    = np.std(self.array_r)
            self.median_r = np.median(self.array_r)
            self.max_r    = np.max(self.array_r)
            self.min_r    = np.min(self.array_r)
            st_r = [self.mean_r, self.std_r, self.median_r, self.max_r, self.min_r]
            self.dist_stat = [st_b, st_g, st_r]

        else:
            self.array_b = np.zeros(height) # 周辺分布のリスト
            self.array_y = np.zeros(height) # Y座標のリスト
            for y in range(by,ey):
                self.array_b[y-by] = np.sum(self._bitmap[y,bx:ex])
                self.array_y[y-by] = y
            self.dist_array = [self.array_b, self.array_y]

            self.mean_b   = np.mean(self.array_b)
            self.std_b    = np.std(self.array_b)
            self.median_b = np.median(self.array_b)
            self.max_b    = np.max(self.array_b)
            self.min_b    = np.min(self.array_b)
            self.dist_stat = [[self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]]

        return self
# -------------------------
    def projection_distribution_v(self, bx:int=0, by:int=0, ex:int=0, ey:int=0):
        """垂直方向周辺分布
        @param (bx, by)->(ex,ey) 指定範囲
        引数を省略した場合(すべて 0 の場合)は、全領域
        @return self.array_x , self.array_b , self.array_g , self.array_r  ヒストグラムのデータ
        @return list self.dist_array  集計結果をリストにしたもの
        @return list self.dist_stat   平均、標準偏差、中央値、最大値、最小値をリストにしたもの
        """
        if bx == 0 and by == 0 and ex == 0 and ey == 0:  # 引数を省略した場合は全領域
            ex = self.width
            ey = self.height

        width = ex - bx # 指定範囲の幅
        if self._kind == 'color':
            self.array_b = np.zeros(width) # 周辺分布のリスト
            self.array_g = np.zeros(width)
            self.array_r = np.zeros(width)
            self.array_x = np.zeros(width) # X座標のリスト
            for x in range(bx,ex):
                self.array_b[x-bx] = np.sum(self._bitmap[by:ey,x,0])
                self.array_g[x-bx] = np.sum(self._bitmap[by:ey,x,1])
                self.array_r[x-bx] = np.sum(self._bitmap[by:ey,x,2])
                self.array_x[x-bx] = x
            self.dist_array = [self.array_b, self.array_g, self.array_r, self.array_x]  # B, G, R, Y軸の順であることに注意

            self.mean_b   = np.mean(self.array_b) # 平均、標準偏差、中央値、最大値、最小値の計算
            self.std_b    = np.std(self.array_b)
            self.median_b = np.median(self.array_b)
            self.max_b    = np.max(self.array_b)
            self.min_b    = np.min(self.array_b)
            st_b = [self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]

            self.mean_g   = np.mean(self.array_g)
            self.std_g    = np.std(self.array_g)
            self.median_g = np.median(self.array_g)
            self.max_g    = np.max(self.array_g)
            self.min_g    = np.min(self.array_g)
            st_g = [self.mean_g, self.std_g, self.median_g, self.max_g, self.min_g]

            self.mean_r   = np.mean(self.array_r)
            self.std_r    = np.std(self.array_r)
            self.median_r = np.median(self.array_r)
            self.max_r    = np.max(self.array_r)
            self.min_r    = np.min(self.array_r)
            st_r = [self.mean_r, self.std_r, self.median_r, self.max_r, self.min_r]
            self.dist_stat = [st_b, st_g, st_r]
            return self

        else:
            self.array_b = np.zeros(width)  # 周辺分布のリスト
            self.array_x = np.zeros(width)  # X座標のリスト
            for x in range(bx,ex):
                self.array_b[x-bx] = np.sum(self._bitmap[by:ey,x])
                self.array_x[x-bx] = x
            self.dist_array = [self.array_b, self.array_x]

            self.mean_b   = np.mean(self.array_b)
            self.std_b    = np.std(self.array_b)
            self.median_b = np.median(self.array_b)
            self.max_b    = np.max(self.array_b)
            self.min_b    = np.min(self.array_b)
            self.dist_stat = [[self.mean_b, self.std_b, self.median_b, self.max_b, self.min_b]]
            return self
# -------------------------
# 幾何変換
# -------------------------
    def resize(self, fx:float, fy:float, interpolation=cv2.INTER_NEAREST):
        """画像サイズを変更する
        @param float fx , fy 倍率(縮小後のサイズではないので注意)
        @param interpolation 補間方法
                cv2.INTER_NEAREST: 最近傍補間
                cv2.INTER_LINEAR: バイリニア補間
                cv2.INTER_CUBIC: バイキュービック補間
                cv2.INTER_AREA: ピクセル領域の関係を利用したリサンプリング
                cv2.INTER_LANCZOS4: Lanczos 補間
        """
        temp = UOpenCV()
        temp._bitmap = cv2.resize(self._bitmap, None, None, fx, fy, interpolation)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("resize(fx={}, fy={}, interpolation={})".format(fx, fy, interpolation))
        return temp  # メソッドチェーンにするため
# -------------------------
# 画像変換
# -------------------------
    def grayscale(self):
        """グレースケール変換
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)
        else:
            temp._bitmap = np.copy(self._bitmap)  # カラー画像以外は処理する必要ない

        temp._name   = self._name
        temp._kind   = 'gray'
        temp._log    = self._log[:]  # スライドという書き方に慣れない
        temp._log.append("grayscale()")
        
        return temp  # このオブジェクトはいつまで生きているのだろうか？
# -------------------------
    def monotone(self,b:int,g:int,r:int):
        """モノトーン変換
        輝度はそのままで色相と彩度を変える
        @param int (b,g,r) 変換する色 np.uint8 のみ
        @return UOpenCV  カラー画像を返す
        @link https://rikoubou.hatenablog.com/entry/2019/02/21/190310 (2022/02/22)
        @link https://tzmi.hatenablog.com/entry/2020/01/07/230036 (2022/02/22)
        @link https://emotionexplorer.blog.fc2.com/blog-entry-84.html (2022/02/22)
        @link https://emotionexplorer.blog.fc2.com/blog-entry-84.html (2022/02/22)
        H (Channel1) - 色相
        0～180の範囲。H/2の値を示す。181～255の範囲は0からの循環.
        S (Channel2) - 彩度
        0～255の範囲。255がS=1.0に相当。
        V (Channel3) - 明度
        0～255の範囲。255がV=1.0に相当。
        """
        tone = np.zeros((1,1,3), np.uint8)
        tone[0][0][0] = b
        tone[0][0][1] = g
        tone[0][0][2] = r
        tone_hsv = cv2.cvtColor(tone, cv2.COLOR_BGR2HSV)
        h = tone_hsv[0][0][0]
        s = tone_hsv[0][0][1]
        v = tone_hsv[0][0][2]

        if self._kind == 'color':
            hsv = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2HSV)
        else:
            color = cv2.cvtColor(self._bitmap, cv2.COLOR_GRAY2BGR)
            hsv   = cv2.cvtColor(color,        cv2.COLOR_BGR2HSV)
        hsv[:,:,0] = h
        hsv[:,:,1] = s
        temp = UOpenCV()
        temp._bitmap = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("monotone(b={}, g={}, r={})".format(b,g,r))
        return temp
# -------------------------
    def applyColorMap(self,colormap:int=cv2.COLORMAP_JET):
        """擬似カラー表示にする
        @param int colormap カラーマップ番号
        cv2.COLORMAP_AUTUMN
        cv2.COLORMAP_BONE 
        cv2.COLORMAP_JET 
        cv2.COLORMAP_WINTER
        cv2.COLORMAP_RAINBOW 
        cv2.COLORMAP_HOT
        cv2.COLORMAP_TURBO など
        """
        temp = UOpenCV()
        temp._bitmap = cv2.applyColorMap(self._bitmap,colormap)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("applyColorMap(colormap={})".format(colormap))
        return temp
# -------------------------
    def cvtColor(self, code:str):
        """色画像分離
        @param str code 分離コマンド
        @return UOpenCV 分離した画像
        """
        if self.kind != 'color':
            raise Exception('カラー画像のみ処理できます')

        temp = UOpenCV()
        temp._name   = self._name
        temp._kind   = code
        temp._log    = self._log[:]
        temp._log.append("cvtColor('{}')".format(code))

        if code == 'X(XYZ)': # switch文がないのは、言語構造の欠陥だと思う  python4では改善されるらしい
            XYZ = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2XYZ)
            temp._bitmap , Y , Z = cv2.split(XYZ)
        elif code == 'Y(XYZ)':
            XYZ = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2XYZ)
            x , temp._bitmap , Z = cv2.split(XYZ)
        elif code == 'Z(XYZ)':
            XYZ = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2XYZ)
            X , Y , temp._bitmap = cv2.split(XYZ)

        elif code == 'Y(YCrCb)': # 輝度
            Yrb = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YCrCb)
            temp._bitmap , r , b = cv2.split(Yrb)
        elif code == 'Cr(YCrCb)':
            Yrb = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YCrCb)
            Y , temp._bitmap , b = cv2.split(Yrb)
        elif code == 'Cb(YCrCb)':
            Yrb = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YCrCb)
            Y , r , temp._bitmap = cv2.split(Yrb)

        elif code == 'H(HSV)': # 色相 Hue
            HSV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HSV_FULL) # 0 ≤ H ≤ 255、0 ≤ S ≤ 255、0 ≤ V ≤ 255
            temp._bitmap , S , V = cv2.split(HSV)
        elif code == 'S(HSV)': # 彩度 Saturation  Chroma
            HSV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HSV_FULL)
            H , temp._bitmap , V = cv2.split(HSV)
        elif code == 'V(HSV)': # 明度 Value  Brightness
            HSV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HSV_FULL)
            H , S , temp._bitmap = cv2.split(HSV)

        elif code == 'H(HLS)': # 色相 Hue
            HLS = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HLS_FULL) # 0 ≤ H ≤ 255、0 ≤ S ≤ 255、0 ≤ L ≤ 255
            temp._bitmap , L , S = cv2.split(HLS)
        elif code == 'L(HLS)': # 輝度 Lightness
            HLS = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HLS_FULL)
            H , temp._bitmap , S = cv2.split(HLS)
        elif code == 'S(HLS)': # 彩度 Saturation  Chroma
            HLS = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2HLS_FULL)
            H , L , temp._bitmap = cv2.split(HLS)

        elif code == 'L(Lab)':
            Lab = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Lab) # 0 ≤ L ≤ 255、0 ≤ a ≤ 255、  0 ≤ b ≤ 255 (cv2.cvtColor メソッドを用いて変換された場合)
            temp._bitmap , a , b = cv2.split(Lab)
        elif code == 'a(Lab)':
            Lab = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Lab)
            L , temp._bitmap , b = cv2.split(Lab)
        elif code == 'b(Lab)':
            Lab = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Lab)
            L , a , temp._bitmap = cv2.split(Lab)

        elif code == 'L(Luv)': # CIE Luv色空間において値域はL [0, 100], u[-100, 100], v[-100, 100]
            Luv = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Luv)
            temp._bitmap , u , v = cv2.split(Luv)
        elif code == 'u(Luv)':
            Luv = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Luv)
            L , temp._bitmap , v = cv2.split(Luv)
        elif code == 'v(Luv)':
            Luv = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2Luv)
            L , u , temp._bitmap = cv2.split(Luv)

        elif code == 'Y(YUV)': # 輝度
            YUV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YUV)
            temp._bitmap , U , V = cv2.split(YUV)
        elif code == 'U(YUV)':
            YUV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YUV)
            Y , temp._bitmap , V = cv2.split(YUV)
        elif code == 'V(YUV)':
            YUV = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2YUV)
            Y , U , temp._bitmap = cv2.split(YUV)

        elif code == 'B(BGR)':
            temp._bitmap , g , r = cv2.split(self._bitmap)
        elif code == 'G(BGR)':
            b , temp._bitmap , r = cv2.split(self._bitmap)
        elif code == 'R(BGR)':
            b , g , temp._bitmap = cv2.split(self._bitmap)

        else:
           raise Exception('無効な分離コマンドです')

        return temp
# -------------------------
    def threshold(self, thresh:int=128, type:int=cv2.THRESH_BINARY):
        """大域的２値化
        カラー画像ならばグレースケール化して２値化する
        グレースケール（１チャンネル）画像ならばそのまま２値化する
        @param int thresh cv2.THRESH_BINARYのときの閾値
        @param int type ２値化の方法
        cv2.THRESH_BINARY threshold 以下の値を0、それ以外の値を maxValue(255) にして2値化
        cv2.THRESH_OTSU 大津の手法で閾値を自動的に決める threshは無視される
        cv2.THRESH_TRIANGLE トライアングルアルゴリズムで閾値を自動的に決める  threshは無視される
        @return UOpenCV(2値化された画像)
        @return UOpenCV.threshold 自動計算した場合の閾値
        @link https://pystyle.info/opencv-image-binarization/ (2022/01/10)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            gray = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # １チェンネルデータにする
            temp.threshold, temp._bitmap = cv2.threshold(gray,         thresh, 255, type) # ２値化データを作る
        else:
            temp.threshold, temp._bitmap = cv2.threshold(self._bitmap, thresh, 255, type)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("threshold(thresh={}, type={})".format(temp.threshold, type))
        return temp
# -------------------------
    def adaptiveThreshold(self, adaptiveMethod:int=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType:int=cv2.THRESH_BINARY, blockSize:int=51, C:float=0):
        """適応的2値化
        カラー画像ならばグレースケール化して２値化する
        グレースケール（１チャンネル）画像ならばそのまま２値化する
        ある近傍領域の中で閾値を計算し、それぞれの領域で2値化処理を行う
        @param int adaptiveMethod 適応的しきい値処理で使用するアルゴリズム cv2.ADAPTIVE_THRESH_MEAN_C、cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C の方が自然な感じがするが、ラベリングを考えると cv2.ADAPTIVE_THRESH_MEAN_C の方が良さそう
        @param int thresholdType 二値化の種類 cv2.THRESH_BINARY、cv2.THRESH_BINARY_INV
        @param int blockSize しきい値計算のための近傍サイズ 1より大きい奇数
        @param float C 計算した閾値からCを引いた値を最終的な閾値にする
        @link https://imagingsolution.net/program/python/opencv-python/adaptivethreshold_algorithm/ (2022/01/23)
        """
        if blockSize % 2 == 0:
            blockSize = blockSize + 1

        temp = UOpenCV()
        if self._kind == 'color':
            gray = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # カラー画像ならばグレースケール化して２値化する
            temp._bitmap = cv2.adaptiveThreshold(gray,         255, adaptiveMethod, thresholdType, blockSize, C) # ２値化データを作る
        else:
            temp._bitmap = cv2.adaptiveThreshold(self._bitmap, 255, adaptiveMethod, thresholdType, blockSize, C)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("adaptiveThreshold(Method={}, thresholdType={}, blockSize={}, C={})".format(adaptiveMethod,thresholdType,blockSize,C))
        return temp
# -------------------------
    def dft(self):
        """FFTを実行しパワースペクトル画像を返す
        カラー画像ならば内部でグレースケール変換する
        @return UOpenCV FFT処理画像(表示できるように正規化（min-max normalization）した画像) １チャンネル画像
        @return UOpenCV._fft_complex 複素数データ
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html (2022/02/23)
        """
        if self._kind == 'color':
            gray = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)
            dft = cv2.dft(np.float32(gray),         flags = cv2.DFT_COMPLEX_OUTPUT)  # カラー画像ならばグレースケール化してFFTする
        else:
            dft = cv2.dft(np.float32(self._bitmap), flags = cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft) # データを４分割て並び替える

        spectrum = 20 * np.log(cv2.magnitude(dft_shift[:,:,0],dft_shift[:,:,1])) # パワースペクトル
        min = spectrum.min()
        max = spectrum.max()
        norm_spect = 255.0 * (spectrum - min) /(max - min) # 正規化（min-max normalization）

        temp = UOpenCV()
        temp._bitmap = norm_spect.astype(np.uint8)
        temp._name   = self._name
        temp._kind   = 'fft'
        temp._log    = self._log[:]
        temp._log.append("dft()")
        temp._fft_complex = dft_shift.copy()
        return temp
# -------------------------
# 画像処理　シェーディング補正
# -------------------------
    def shading_black(self,black_reference,offset:float=128.0):
        """黒基準画像を用いたシェーディング補正
        処理後画像 = 処理前画像 - 黒基準画像 + オフセット の計算を行う
        @param UOpenCV black_reference 黒基準画像
        @param float offset オフセット
        @retuen UOpenCV
        @link https://emotionexplorer.blog.fc2.com/blog-entry-158.html (2022/01/27)
        """
        if self._kind != 'color':
            raise Exception('カラー画像以外対応していません')

        if self._bitmap.shape != black_reference._bitmap.shape:
            raise Exception('画像の大きさやチャンネル数が合っていません')

        before = self._bitmap.astype(dtype=np.float32)  # 実数計算できるようにする
        black = black_reference._bitmap.astype(dtype=np.float32)
        after = before - black + offset  # シェーディング補正

        temp = UOpenCV()
        temp._bitmap = np.clip(after, 0, 255).astype(dtype=np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("shading_black(black={}, offset={})".format(black_reference.name, offset))
        return temp
# -------------------------
    def shading_white_black(self,white_reference,black_reference,multi:float=255.0):
        """白・黒基準画像を用いたシェーディング補正
        処理後画像 = (補正前画像 - 黒基準画像) / (白基準画像 - 黒基準画像) * nulti の計算を行う
        @param UOpenCV white_reference 白基準画像
        @param UOpenCV black_reference 黒基準画像
        @param float multi 倍率
        @retuen UOpenCV
        @refer 「画像処理応用技術」、田中弘、工業調査会、1989,p110
        """
        if self._kind != 'color':
            raise Exception('カラー画像以外対応していません')

        if self._bitmap.shape != white_reference._bitmap.shape:
            raise Exception('画像(white)の大きさやチャンネル数が合っていません')

        if self._bitmap.shape != black_reference._bitmap.shape:
            raise Exception('画像(black)の大きさやチャンネル数が合っていません')

        before = self._bitmap.astype(dtype=np.float32) # 実数計算できるようにする
        white = white_reference._bitmap.astype(dtype=np.float32)
        black = black_reference._bitmap.astype(dtype=np.float32)

        warnings.resetwarnings()          # RuntimeWarning をこのブロックだけ例外にしている
        with warnings.catch_warnings():   # https://note.nkmk.me/python-warnings-ignore-warning/ (2022/05/19)
            warnings.simplefilter('error')
            try:
                after = multi * (before - black) / (white - black) # シェーディング補正
            except Exception as e:
                raise Exception('白画像と黒画像で同じ輝度のピクセルがあります')

        temp = UOpenCV()
        temp._bitmap = np.clip(after, 0, 255).astype(dtype=np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("shading_white_black(white={}, black={}, multi={})".format(white_reference.name, black_reference.name, multi))
        return temp
# -------------------------
    def shading_unevenness(self,ksize:int=31):
        """シェーディング補正(凹凸係数)
        シェーディング画像に良好なしきい値を設定できる変動しきい値式2値化処理法(凹凸係数)
        @param int ksize カーネルサイズ
        @retuen UOpenCV
        @link https://kakasi.hatenablog.com/entry/2020/03/02/151053 (2022/05/10)
        @link https://www.jstage.jst.go.jp/article/iieej/36/3/36_3_204/_article/-char/ja/ (2022/05/10)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()

        blur = cv2.blur(self._bitmap, (ksize, ksize)) # 平均化処理を行う
        blur = np.clip(blur, 1, 255)  # 0で割ることはできない
        img = self._bitmap / blur  # 要素ごとの割り算

        temp._bitmap = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("shading_unevenness(ksize={})".format(ksize))
        return temp
# -------------------------
    def shading_blackhat(self,ksize:int=15):
        """シェーディング補正(モルフォロジー演算)
        モルフォロジー演算(BLACKHAT)を行った後、ネガポジ変換する
        @param int ksize カーネルサイズ
        @retuen UOpenCV
        @link https://kakasi.hatenablog.com/entry/2020/03/02/151053 (2022/01/28)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize,ksize))
        img = cv2.morphologyEx(self._bitmap, cv2.MORPH_BLACKHAT, kernel)  # こんなことでシェーディング補正ができるんだ！
        temp._bitmap = cv2.bitwise_not(img)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("shading_blackhat(ksize={})".format(ksize))
        return temp
# -------------------------
# 画像処理　ヒストグラム変換
# -------------------------
    def equalizeHist_CLAHE(self,clipLimit:float=40.0, tile:int=8):
        """コントラスト制限適応ヒストグラム平坦化
        (CLAHE, Contrast Limited Adaptive Histogram Equalization) 
        カラー画像ならば輝度のみヒストグラムを変更する
        @param float clipLimit 大きくすればコントラストが強くなる
        @param int tile 大きいと大局的に平坦化、小さいと部分的に平坦化
        @return UOpenCV
        @link https://qiita.com/yoya/items/a11085f90f555b887cf6 (2022/05/10)
        @link https://kp-ft.com/717 (2022/05/10)
        """
        clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=(tile,tile))
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = clahe.apply(y)
            yuv     = cv2.merge((y,u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            temp._bitmap = clahe.apply(self._bitmap)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("equalizeHist_CLAHE(clipLimit={}, tile={})".format(clipLimit, tile))
        return temp
# -------------------------
    def equalizeHist(self):
        """ヒストグラム平坦化
        カラー画像ならば輝度のみヒストグラムを変更する
        @return UOpenCV
        @link https://qiita.com/yoya/items/a11085f90f555b887cf6 (2022/01/01)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = cv2.equalizeHist(y)
            yuv     = cv2.merge((y,u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            temp._bitmap = cv2.equalizeHist(self._bitmap)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("equalizeHist()")
        return temp
# -------------------------
    def normalize(self,alpha:float=0,beta:float=255,norm_type:int=cv2.NORM_MINMAX):
        """ヒストグラム正規化
        カラー画像ならば輝度のみヒストグラムを変更する
        norm_type=cv2.NORM_MINMAX の場合、alpha – 範囲の下界
                                          beta  – 範囲の上界
                                          alpha から beta の範囲にヒストグラムを変換する
        norm_type=cv2.NORM_INF , 
                  cv2.NORM_L1  ,
                  cv2.NORM_L2 の場合、    alpha – 正規化されるノルム値
                                          beta  – 未使用
        @return UOpenCV
        @link http://opencv.jp/opencv-2svn/cpp/operations_on_arrays.html#cv-normalize (2022/01/02)
        @link https://www.codetd.com/ja/article/7031167 (2022/01/02)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = cv2.normalize(y, None, alpha, beta, norm_type)
            yuv     = cv2.merge((y,u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            temp._bitmap = cv2.normalize(self._bitmap, None, alpha, beta, norm_type)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("normalize(alpha={}, beta={}, type={})".format(alpha, beta, norm_type))
        return temp
# -------------------------
    def expand_histogram(self,min:float,max:float):
        """ヒストグラム拡張
        輝度の分布を min から maxに収める
        カラー画像ならば輝度のみヒストグラムを変更する
        y' = y_max * (y - min) / (max - min) の計算を行う
        @param float min , max 輝度の分布を min から maxに収める
        @return UOpenCV
        @link https://algorithm.joho.info/image-processing/tone-curve/#toc5 (2022/01/04)
        @link https://codezine.jp/article/detail/214 (2022/01/04)
        """
        if max == min:
            raise Exception('パラメータが不適切(max = min)です')
        d = max - min
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y = y.astype(np.float32)
#           y_max = y.max()
#           y = y_max * (y - min) / d  # @link https://algorithm.joho.info/image-processing/tone-curve/#toc5 (2022/01/04)
            y = 255.0 * (y - min) / d  # @link https://codezine.jp/article/detail/214 (2022/01/04)
            y = np.clip(y,0,255)
            yuv     = cv2.merge((y.astype(np.uint8),u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            g = self.bitmap.astype(np.float32)
            g = 255.0 * (g - min) / d
            temp._bitmap = np.clip(g,0,255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("expand_histogram(min={}, max={})".format(min, max))
        return temp
# -------------------------
    def stretch_histogram(self,min1:float,max1:float,min2:float=0.0,max2:float=255.0):
        """ヒストグラム伸張
        カラー画像ならば輝度のみヒストグラムを変更する
        grad = (max2 - min2) / (max1 - min1)
        y' = grad * (y - min1) + min2 の計算を行う
        @param float min1,max1 拡大する前の輝度
        @param float min2,max2 拡大した後の輝度
        @return UOpenCV
        @refer 「デジタル画像処理入門」、酒井幸一、コロナ社、1997,p17
        """
        if max1 == min1:
            raise Exception('パラメータが不適切(max1 = min1)です')
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y = y.astype(np.float32)
            grad = (max2 - min2) / (max1 - min1)
            y = grad * (y - min1) + min2
            y = np.clip(y,0,255)
            yuv     = cv2.merge((y.astype(np.uint8),u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            g = self.bitmap.astype(np.float32)
            grad = (max2 - min2) / (max1 - min1)
            g = grad * (g - min1) + min2
            temp._bitmap = np.clip(g,0,255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("stretch_histogram(min1={}, max1={}, min2={}, max2={})".format(min1, max1, min2, max2))
        return temp
# -------------------------
    def bitwise_not_brightness(self):
        """輝度反転
        輝度のみ反転する
        カラー画像以外は、bitwise_notと同じ結果になる
        @return UOpenCV
        """
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = cv2.bitwise_not(y)
            yuv     = cv2.merge((y,u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            temp._bitmap = cv2.bitwise_not(self._bitmap)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("bitwise_not_brightness()")
        return temp
# -------------------------
    def bitwise_not(self):
        """ネガポジ反転
        ３チャンネル反転する
        @return UOpenCV
        """
        temp = UOpenCV()
        temp._bitmap = cv2.bitwise_not(self._bitmap)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("bitwise_not()")
        return temp
# -------------------------
    def convert_histogram_avg_std(self,avg:float=128,std:float=32):
        """輝度の平均と標準偏差を指定してヒストグラム変更
        カラー画像ならば輝度のみヒストグラムを変更する
         y' = (y - mean(y)) * std / std(y) + avg の計算をする
        @param avg:変更後の輝度の平均
        @param std:変更後の輝度の標準偏差
        @return UOpenCV
        @link https://lp-tech.net/articles/nCvfb (2022/01/04)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = y.astype(np.float32)
            y       = ((y - np.mean(y)) * std) / np.std(y) + avg
            y       = np.clip(y,0,255)
            yuv     = cv2.merge((y.astype(np.uint8),u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            g = self._bitmap.astype(np.float32)
            g = ((g - np.mean(g)) * std) / np.std(g) + avg
            temp._bitmap = np.clip(g,0,255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("convert_histogram(avg={}, std={})".format(avg, std))
        return temp
# -------------------------
    def convert_contrast_brightness(self,alpha:float=1.0,beta:float=0.0):
        """輝度コントラスト、明るさを変更
        カラー画像ならば輝度のみヒストグラムを変更する
        y' = (alpha * (y - 127) + 127 ) + beta の計算を行う
        @param float alpha 1<alpha コントラスト上昇  0<alpha<1コントラスト低下
        @param float beta  0<beta 輝度上昇 beta<0 輝度低下
        @return UOpenCV
        @link https://algorithm.joho.info/image-processing/tone-curve/#toc3 (2022/01/04)
        @refer 「Ｃ言語で学ぶ実践画像処理」、井上誠喜ほか、オーム社、1999,p71
        """
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = y.astype(np.float32)
            y       = alpha * (y - 127.0) + 127.0 + beta
            y       = np.clip(y,0,255)
            yuv     = cv2.merge((y.astype(np.uint8),u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            g = self.bitmap.astype(np.float32)
            g = alpha * (g - 127.0) + 127.0 + beta
            temp._bitmap = np.clip(g,0,255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("convert_contrast_brightness(a={}, b={})".format(alpha, beta))
        return temp
# -------------------------
    def convertScaleAbs(self,alpha:float=1.0,beta:float=0):
        """コントラスト、明るさを変更する
        3つのチャンネルについて、dst = src * alpha + beta の計算を行う
        @param float alpha 1<alpha コントラスト上昇  0<alpha<1コントラスト低下
        @param float beta  0<beta 輝度上昇 beta<0 輝度低下
        @link https://qiita.com/sitar-harmonics/items/2dcc27fc959e42ebbc44 (2022/01/03)
        @return UOpenCV
        """
        temp = UOpenCV()
        temp._bitmap = cv2.convertScaleAbs(self._bitmap,alpha=alpha,beta=beta)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("convertScaleAbs(alpha={}, beta={})".format(alpha,beta))
        return temp
# -------------------------
# 画像処理　画像フィルタ
# -------------------------
    def filter2D(self,kernel,offset:float,comment:str='-'):
        """空間フィルタ処理
        すべてのチャンネルに同じフィルタ処理をする
        @param numpy.ndarray kernel 畳み込み演算のカーネル
        @param float offset 畳み込み演算後の加算値
        @return UOpenCV
        @link https://pystyle.info/opencv-filtering/ (2022/01/06)
        """
        temp = UOpenCV()
        temp._bitmap = cv2.filter2D(self._bitmap,-1,kernel,delta=offset)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("filter2D(comment={})".format(comment))
        return temp
# -------------------------
    def blur(self,ksize:int=3):
        """単純平滑化
        @param int ksize カーネルの大きさ 奇数のみ
        @return UOpenCV
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        temp._bitmap = cv2.blur(self._bitmap,(ksize,ksize))
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("blur(ksize={})".format(ksize))
        return temp
# -------------------------
    def medianBlur(self,ksize:int=5):
        """メディアンフィルタ
        @param int ksize カーネルの大きさ 奇数のみ
        @return UOpenCV
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        temp._bitmap = cv2.medianBlur(self._bitmap,ksize)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("medianBlur(ksize={})".format(ksize))
        return temp
# -------------------------
    def GaussianBlur(self, ksize:int=5, sigmaX:float=3):
        """ガウシアンフィルタ
        @param int ksize カーネルサイズ。1以上～31以下の奇数
        @param float sigmaX 標準偏差
        @return UOpenCV
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        temp._bitmap = cv2.GaussianBlur(self._bitmap,(ksize,ksize), sigmaX)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("GaussianBlur(ksize={}, sigmaX={})".format(ksize, sigmaX))
        return temp
# -------------------------
    def unsharp(self, ksize:int=5, sigmaX:float=3, k:float=1):
        """アンシャープフィルタ エッジを残した鮮鋭化
        元画像から平滑化(ガウシアン)したデータを差く
        引き算された画像をある定数倍したうえで、入力画像に足す
        @param int ksize ガウシアンフィルタのカーネルサイズ
        @param float sigmaX ガウシアンフィルタの標準偏差
        @param float k 倍率
        @link https://qiita.com/tanaka_benkyo/items/2b4460f1cc0ed6a685eb (2022/02/23)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        img_copy = self._bitmap.astype(np.int16).copy()
        img_mean = cv2.GaussianBlur(img_copy, (ksize, ksize), sigmaX)
        diff_img = img_copy - img_mean
        result = img_copy + diff_img * k
        temp = UOpenCV()
        temp._bitmap = np.clip(result, 0, 255).astype(np.uint8)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("unsharp(ksize={}, sigmaX={}, k={})".format(ksize, sigmaX, k))
        return temp
# -------------------------
    def bilateralFilter(self,d:int=15,sigmaColor:float=25,sigmaSpace:float=25):
        """バイラテラルフィルタ
        エッジを残した平滑化
        @param int d 処理する隣接ピクセル
        @param float sigmaColor 色空間に関する標準偏差　この値が大きいほど、色がより異なるピクセル同士を混合して平滑化を実施
        @param float sigmaSpace 距離空間に関する標準偏差　この値が大きいほど、より遠くのピクセル同士を混合して平滑化
        デフォルトの引数は、いい加減
        @return UOpenCV
        """
        temp = UOpenCV()
        temp._bitmap = cv2.bilateralFilter(self._bitmap,d,sigmaColor,sigmaSpace)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("bilateralFilter(d={}, sigmaColor={}, sigmaSpace={})".format(d, sigmaColor, sigmaSpace))
        return temp
# -------------------------
    def edgePreservingFilter(self, flags:int=cv2.RECURS_FILTER, sigma_s:float=3.0, sigma_r:float=0.1):
        """エッジを保持しつつ平滑化を行うフィルタ
        OpenCV のマニュアルには、"Input 8-bit 3-channel image" とあるが、グレースケール画像も処理できる
        @param int flags  cv2.RECURS_FILTER or cv2.NORMCONV_FILTER
        @param float sigma_s Range between 0 to 200  sigma spatial 近接領域のサイズ
        @param float sigma_r Range between 0 to 1    sigma range   近接領域の異なる色を平均化します。sigma_rを大きくすると、特定の色の領域が広くなります。
        @return UOpenCV
        @link https://qiita.com/shoku-pan/items/454855a8340962eaa05e#%E6%B3%A8%E9%87%88 (2022/05/16)
        """
        temp = UOpenCV()
        temp._bitmap = cv2.edgePreservingFilter(self._bitmap, flags=flags, sigma_s=sigma_s, sigma_r=sigma_r)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("edgePreservingFilter(flag={}, sigma_s={}, sigma_r={})".format(flags, sigma_s, sigma_r))
        return temp
# -------------------------
    def detailEnhance(self, sigma_s:float=10, sigma_r:float=0.15):
        """細部強調フィルタ
        detailEnhanceはカラー画像以外処理できないので、カラー画像以外は内部で３チャンネル化している
        @param float sigma_s Range between 0 to 200  sigma spatial 近接領域のサイズ
        @param float sigma_r Range between 0 to 1    sigma range   近接領域の異なる色を平均化します。sigma_rを大きくすると、特定の色の領域が広くなります。
        @return UOpenCV
        @link https://qiita.com/shoku-pan/items/454855a8340962eaa05e#%E6%B3%A8%E9%87%88 (2022/05/16)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = cv2.detailEnhance(self._bitmap, sigma_s=sigma_s, sigma_r=sigma_r)
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap, cv2.COLOR_GRAY2BGR)
            temp._bitmap = cv2.detailEnhance(temp._bitmap, sigma_s=sigma_s, sigma_r=sigma_r)
            temp._bitmap = cv2.cvtColor(temp._bitmap,cv2.COLOR_BGR2GRAY)
        if self._kind == 'binary':
            threshold, temp._bitmap = cv2.threshold(temp._bitmap, 128, 255, cv2.THRESH_BINARY)  # ２値画像でフィルタを使うかどうかわからないが、２値画像に戻している
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("detailEnhance(sigma_s={}, sigma_r={})".format(sigma_s, sigma_r))
        return temp
# -------------------------
    def fastNlMeansDenoising(self, h:float=10, hColor:float=10, templateWindowSize:int=7, searchWindowSize:int=21):
        """ノンローカルミーンフィルタ(Non-Local Means Filter)
        ノイズ除去に用いる
        処理に時間が掛かる
        内部で fastNlMeansDenoisingColored と fastNlMeansDenoising を使い分けている
        @param float h ノイズ除去の強度
        @param float hColor hと同じにしておく  カラー画像のみ有効
        @param int search_window 
        @param int block_size  
        @return UOpenCV
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = cv2.fastNlMeansDenoisingColored(self._bitmap, dst=None, h=h, hColor=hColor, templateWindowSize=templateWindowSize, searchWindowSize=searchWindowSize)
        else:
            temp._bitmap = cv2.fastNlMeansDenoising(       self._bitmap, dst=None, h=h,                templateWindowSize=templateWindowSize, searchWindowSize=searchWindowSize)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("fastNlMeansDenoising(h={}, hColor={}, templateWindowSize={}, searchWindowSize={})".format(h, hColor, templateWindowSize, searchWindowSize))
        return temp
# -------------------------
    def Sobel(self, dx:int=1, dy:int=0, ksize:int=3, offset:float=128):
        """Sobelフィルタ １次微分フィルタ
        @param int dx , dy 微分の次数と方向を決定する
        (dx, dy)=(1, 0)    横方向の輪郭検出
        (dx, dy)=(0, 1)    縦方向の輪郭検出
        (dx, dy)=(1, 1)    斜め右上方向の輪郭検出
        @param int ksize カーネルサイズ。-1から7までの奇数 -1(cv2.CV_SCHARR )は3x3のScharrフィルタ
        @param offset 加算値
        @return UOpenCV
        @link http://whitewell.sakura.ne.jp/OpenCV/py_tutorials/py_imgproc/py_gradients/py_gradients.html (2022/02/01)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        temp._bitmap = cv2.Sobel(self._bitmap, -1, dx, dy, ksize=ksize, delta=offset)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("Sobel(dx={}, dy={}, size={}, offset={})".format(dx, dy, ksize, offset))
        return temp
# -------------------------
    def Laplacian(self, ksize:int=3, offset:float=128):
        """Laplacianフィルタ ２次微分フィルタ
        @param int ksize カーネルサイズ。1～31の奇数
        @param offset 加算値
        @return UOpenCV
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        temp = UOpenCV()
        temp._bitmap = cv2.Laplacian(self._bitmap, -1, None, ksize=ksize, delta=offset)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("Laplacian(ksize={}, offset={})".format(ksize,offset))
        return temp
# -------------------------
# 画像処理　ルックアップテーブル
# -------------------------
    def lookup_table(self,lut,comment:str='-'):
        """ルックアップテーブル処理
        ３チャンネル同じ処理を行う
        @param numpy.ndarray lut ルックアップテーブル 値の型はnp.uint8 これ以外は処理がおかしくなる
        配列は255個　これ以外のサイズはエラーになる
        @param str comment logに記録するコメント。通常はファイル名を入れる
        @return UOpenCV
        """
        lut = lut.astype(np.uint8)  # 値の型はnp.uint8 これ以外は処理がおかしくなる
        temp = UOpenCV()
        temp._bitmap = cv2.LUT(self._bitmap, lut)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("lookup_table(comment={})".format(comment))
        return temp
# -------------------------
    def lookup_table_brightness(self,lut,comment:str='-'):
        """ルックアップテーブル処理
        輝度のみルックアップテーブル処理を行う
        カラー画像以外は、lookup_tableと同じ結果になる
        @param numpy.ndarray lut ルックアップテーブル 値の型はnp.uint8 これ以外は処理がおかしくなる
        配列は255個　これ以外のサイズはエラーになる
        @param str comment logに記録するコメント。通常はファイル名を入れる
        @return UOpenCV
        """
        lut = lut.astype(np.uint8)
        temp = UOpenCV()
        if self._kind == 'color':
            yuv     = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2YUV)
            y, u, v = cv2.split(yuv)
            y       = cv2.LUT(y, lut)
            yuv     = cv2.merge((y,u,v))
            temp._bitmap = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            temp._bitmap = cv2.LUT(self._bitmap, lut)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("lookup_table_brightness(comment={})".format(comment))
        return temp
# -------------------------
# 画像処理　モルフォロジー(形態学)処理
# -------------------------
    def erode(self,ksize:int=3,iterations:int=1):
        """（白い部分の）収縮(erosion)処理
        ２値画像で利用するがカラー画像でも利用できる
        @param int ksize カーネルサイズ
        @param int iterations 反復回数
        @return UOpenCV
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html (2022/01/23)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize,ksize))  # cv2.MORPH_RECT , cv2.MORPH_ELLIPSE , cv2.MORPH_CROSS
        temp = UOpenCV()
        temp._bitmap = cv2.erode(self._bitmap, kernel, iterations=iterations)  # 名前引数は良いと思うのだが、このような書き方(iterations=iterations)ができるのは嫌だ
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("erode(ksize={}, iterations={})".format(ksize, iterations))
        return temp
# -------------------------
    def dilate(self,ksize:int=3,iterations:int=1):
        """（白い部分の）膨張(dilate)処理
        ２値画像で利用するがカラー画像でも利用できる
        @param int ksize カーネルサイズ
        @param int iterations 反復回数
        @return UOpenCV
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html (2022/01/23)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize,ksize))  # cv2.MORPH_ELLIPSE , cv2.MORPH_CROSS
        temp = UOpenCV()
        temp._bitmap = cv2.dilate(self._bitmap, kernel, iterations=iterations)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("dilate(ksize={}, iterations={})".format(ksize, iterations))
        return temp
# -------------------------
    def morphologyEx(self,op:int,ksize:int=3,iterations:int=1):
        """（白い部分の）各種モルフォロジー処理 
        ２値画像で利用するがカラー画像でも利用できる
        @param int op モルフォロジー処理の方法
        cv2.MORPH_ERODE erode() と同じ
        cv2.MORPH_DILATE erode() と同じ
        cv2.MORPH_OPEN 収縮→膨張
        cv2.MORPH_CLOSE 膨張→収縮
        cv2.MORPH_GRADIENT 膨張した画像と収縮した画像の差を取る 物体の外郭(境界線)が得られます
        cv2.MORPH_TOPHAT 入力画像とオープニングした画像の差を取る
        cv2.MORPH_BLACKHAT 入力画像とクロージングした画像の差を取る
        @param int ksize カーネルサイズ
        @param int iterations 反復回数
        @return UOpenCV
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html (2022/01/23)
        """
        if ksize % 2 == 0:
            ksize = ksize + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(ksize,ksize))  # cv2.MORPH_ELLIPSE , cv2.MORPH_CROSS
        temp = UOpenCV()
        temp._bitmap = cv2.morphologyEx(self._bitmap, op, kernel, iterations=iterations)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("morphologyEx(op={}, ksize={}, iterations={})".format(op, ksize, iterations))
        return temp
# -------------------------
# 画像処理　エッジ検出
# -------------------------
    def morphologyGradient(self, dilate_ksize:int=3, dilate_it:int=1, erode_ksize:int=3, erode_it:int=0):
        """モルフォロジー処理を利用したエッジ検出
        n回膨張した画像から、n回縮小した画像を引く
        @param int dilate_ksize dilate(膨張)のカーネルサイズ
        @param int dilate_it dilateの繰り返し回数
        @param int erode_ksize erode(縮小)のカーネルサイズ
        @param int erode_it erodeの繰り返し回数
        """
        if dilate_it == 0 and erode_it == 0:  # 何もしない
            return self
        if dilate_it != 0:  # 膨張画像
            dilate_bitmap = self.dilate(dilate_ksize, dilate_it)._bitmap
        else:
            dilate_bitmap = np.copy(self._bitmap)
        if erode_it != 0:  # 縮小画像
            erode_bitmap  = self.erode(erode_ksize, erode_it)._bitmap
        else:
            erode_bitmap  = np.copy(self._bitmap)
        temp = UOpenCV()
        temp._bitmap = cv2.subtract(dilate_bitmap, erode_bitmap)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("morphologyGradient(dilate_ksize={}, dilate_it={}, erode_ksize={}, erode_it={})".format(dilate_ksize, dilate_it, erode_ksize, erode_it))
        return temp
# -------------------------
    def Canny(self, threshold1:float=50, threshold2:float=150, apertureSize:int=3):
        """Canny法
        カラー画像の場合は内部でグレースケール画像にしてから処理する
        @param float threshold1 最小しきい値 少しづつ大きくして、エッジの数を減らす。連続性の大きさ
        @param float threshold2 最大しきい値 少しづつ大きくして、エッジの数を減らす。この輝度ならばエッジである
        @param int apertureSize ゾーベルフィルタのサイズ 3 , 5 , 7のいずれか
        @return UOpenCV  ２値画像を返すことに注意
        @link https://kuroro.blog/python/wOt3yEohr7oQt1qzif71/ (2022/01/28)
        """
        if apertureSize % 2 == 0:
            apertureSize = apertureSize + 1
        temp = UOpenCV()  # ２値画像を返す
        if self._kind == 'color':
            img = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # 8ビット画像にする
            temp._bitmap = cv2.Canny(image=img,          threshold1=threshold1, threshold2=threshold2, apertureSize=apertureSize)  # ２値画像になっている
        else:
            temp._bitmap = cv2.Canny(image=self._bitmap, threshold1=threshold1, threshold2=threshold2, apertureSize=apertureSize)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("Canny(threshold1={}, threshold2={}, apertureSize={})".format(threshold1, threshold2, apertureSize))
        return temp
# -------------------------
    def HoughCircles(self, method:int=cv2.HOUGH_GRADIENT, dp:float=0.8, minDist:float=50, param1:float=100, param2:float=100, minRadius:int=0, maxRadius:int=0, pcolor=(0,0,255)):
        """ハフ変換で円を求め、元画像に描画して返す(元画像は変更しない)
        エッジの勾配を使っているので、ぼかした画像を処理するほうが良い。ぼかし具合によって検出感度が変わる
        ２値画像は、ぼかさないと検出できない
        cv2.HoughCirclesは１チャンネル(グレースケール)画像のみ
        カラー画像の場合は、内部でグレースケール画像にしてから処理する
        @param int method ハフ変換の手法 cv2.HOUGH_GRADIENT and cv2.HOUGH_GRADIENT_ALT
        @param float dp 投票器の解像度 0.8 ～ 1.2 くらい
        @param float minDist 円同士が最低限離れていなければならない距離
        @param float param1 = 100 Canny法のHysteresis処理の閾値
        @param float param2 = 100 円の中心を検出する際の閾値  閾値を低い値にすると円の誤検出が多くなり、高い値にすると未検出が多くなります
        @param int minRadius = 0 検出する円の半径の下限
        @param int maxRadius = 0 検出する円の半径の上限 maxRadius <=0 ならば最大まで
        @param tuple pcolor 抽出した円を描画する色

        @return UOpenCV 抽出した円を描画した画像（カラー画像を返す）
        @return UOpenCV.circles [ [ [円の中心点のx座標, 円の中心点のy座標, 円の半径] ...] ]
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html (2022/01/29)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = np.copy(self._bitmap)  # 描画先の画像を確保
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("HoughCircles(method={}, dp={}, minDist={}, param1={}, param2={}, minRadius={}, maxRadius={})".format(method, dp, minDist, param1, param2, minRadius, maxRadius))

        if self._kind == 'color':  # HoughCirclesはグレースケール画像のみ
            img = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # カラー画像はグレースケールにする
            circles = cv2.HoughCircles(image=img,          method=method, dp=dp, minDist=minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
        else:
            circles = cv2.HoughCircles(image=self._bitmap, method=method, dp=dp, minDist=minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

        if circles is None:
            temp.circles = None  # 円のデータはない
            return temp

        temp.circles = np.uint16(np.around(circles))
        for i in temp.circles[0,:]:
            # 円を描く
            cv2.circle(temp._bitmap,(i[0],i[1]),i[2],pcolor,2)
            # 中心点を描く
            cv2.circle(temp._bitmap,(i[0],i[1]), 2  ,pcolor,3)

        return temp
# -------------------------
    def HoughLinesP(self, rho:float=1, theta:float=np.radians(1), threshold:int=100, minLineLength:float=0, maxLineGap:float=0, pcolor=(0,0,255)):
        """ハフ変換で線分を求め、元画像に描画して返す(元画像は変更しない) 確率的ハフ変換 
        白い部分の処理を行う。Canny法で輪郭検出をしておくと良い
        cv2.HoughLinesPは１チャンネル(グレースケール)画像のみ
        カラー画像の場合は、内部でグレースケール画像にしてから処理する
        ぼかさなくても処理できる。  ２値画像でもできる
        @param float rho 直角座標点と直線の距離 = 1  ρ = xcosθ + ysinθのρの値。1以上の値を指定する。
        @param float theta 直角座標点と直線の角度 ランダムに線を判断するための回転角。大きくすれば複雑な線を認識する。 ρ = xcosθ + ysinθ のθの値。
        @param int threshold 閾値(直線と判断する投票数)
        @param float minLineLength 直線とみなす最小の長さ
        @param float maxLineGap 同一直線とみなす点間隔の長さ
        @param tuple pcolor 抽出した円を描画する色

        @return UOpenCV 線分が描画された画像（カラー画像を返す）
        @return UOpenCV.lines 線分の始点と終点の座標 (x1, y1) - (x2, y2)
        @link https://shikaku-mafia.com/cv2-houghlinesp/ (2022/01/28)
        @link https://kuroro.blog/python/nNffXtmWKE3lEa6bbbSw/?msclkid=4fe47fd0d0d111ec806084accc8a4b46 (2022/05/11)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = np.copy(self._bitmap)  # 描画先の画像を確保
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("HoughLinesP(rho={}, theta={}, threshold={}, minLineLength={}, maxLineGap={})".format(rho, theta, threshold, minLineLength, maxLineGap))

        if self._kind == 'color':  # HoughLinesPはグレースケール画像のみ
            img = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # カラー画像はグレースケールにする
            temp.lines = cv2.HoughLinesP(image=img,    rho=rho, theta=theta, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)
        else:
            temp.lines = cv2.HoughLinesP(self._bitmap, rho=rho, theta=theta, threshold=threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

        if temp.lines is None:
            return temp

        for line in temp.lines: # 線分を描画する
            x1, y1, x2, y2 = line[0]
            line_img = cv2.line(temp._bitmap, (x1, y1), (x2, y2), pcolor, 1)

        return temp
# -------------------------
    def FastLineDetector(self,length_threshold=5, distance_threshold=1.41421356, canny_th1=50, canny_th2=150, canny_aperture_size=3, do_merge=False, pcolor=(0,0,255)):
        """Fast Line Detector 線分検出
        カラー画像の場合は、内部でグレースケール画像にしてから処理する
        ぼかさなくても処理できる。  ２値画像でもできる
        @param length_threshold - 長さ閾値 これより短いセグメントは破棄されます
        @param distance_threshold - 距離閾値 これより遠い仮説線分から配置されたポイントは、外れ値と見なされます。
        @param canny_th1 - Cannyヒステリシス1 Canny()のヒステリシス手順の最初のしきい値
        @param canny_th2 - Cannyヒステリシス1 Canny()のヒステリシス手順の2番目のしきい値
        @param canny_aperture_size - Cannyソベルオペレータ アパチャーサイズ Canny()のソベルオペレータ アパチャーサイズ
        @param do_merge - 増分マージオプション Trueの場合、セグメントの増分マージが実行されます
        @param tuple pcolor 抽出した円を描画する色

        @return UOpenCV 線分が描画された画像（カラー画像を返す）
        @return UOpenCV.lines 線分のリスト (x1, y1) - (x2, y2)の組 float型なので注意
        Fast Line Detector は openCV conribution library の ximgprocを利用する
        pip install opencv-python
        pip install opencv-contrib-python 
        として、ライブラリをインストールしておく必要がある。同時に入れないと動かないことがあった
        @link https://nsr-9.hatenablog.jp/entry/2021/08/12/200000 (2022/02/22)
        @link https://emotionexplorer.blog.fc2.com/blog-entry-128.html (2022/02/22)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = np.copy(self._bitmap)  # 描画先の画像を確保
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("FastLineDetector(length_threshold={}, distance_threshold={}, canny_th1={}, canny_th2={}, canny_aperture_size={}, do_merge={})".format(length_threshold, distance_threshold, canny_th1, canny_th2, canny_aperture_size, do_merge))

        fld = cv2.ximgproc.createFastLineDetector(length_threshold=length_threshold, distance_threshold=distance_threshold, canny_th1=canny_th1, canny_th2=canny_th2, canny_aperture_size=canny_aperture_size, do_merge=do_merge)
        if self._kind == 'color':  # FastLineDetectorはグレースケール画像のみ
            img = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # カラー画像はグレースケールにする
            temp.lines = fld.detect(img)      # 線分検出
        else:
            temp.lines = fld.detect(self._bitmap)

        if temp.lines is None:
            return temp

#        temp._bitmap = fld.drawSegments(temp._bitmap, temp.lines, draw_arrow=False, linecolor=pcolor, linethickness=1) # 線の描画 グレースケール画像になる
        for line in temp.lines: # 線分を描画する
            x1, y1, x2, y2 = line[0]  # float型のデータになっている
            line_img = cv2.line(temp._bitmap, (int(x1), int(y1)), (int(x2), int(y2)), pcolor, 1)

        return temp
# -------------------------
    def LineSegmentDetector(self, refine=cv2.LSD_REFINE_STD, scale=0.8, sigma_scale=0.6, quant=2.0, ang_th=22.5, log_eps=0, density_th=0.7, n_bins=1024, pcolor=(0,0,255)):
        """Line Segment Detector(線分検出器)による線分検出
        カラー画像の場合は、内部でグレースケール画像にしてから処理する
        ぼかさなくても処理できる。  ２値画像でもできる
        @return UOpenCV 線分が描画された画像（カラー画像を返す）
        @return UOpenCV.lines 線分のリスト (x1, y1) - (x2, y2)の組
        @link https://emotionexplorer.blog.fc2.com/blog-entry-129.html (2022/02/22)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = np.copy(self._bitmap)  # 描画先の画像を確保
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("LineSegmentDetector(refine={}, scale={}, sigma_scale={}, quant={}, ang_th={}, log_eps={}, density_th={}, n_bins={})".format(refine, scale, sigma_scale, quant, ang_th, log_eps, density_th, n_bins))

        lsd = cv2.createLineSegmentDetector(refine=refine, scale=scale, sigma_scale=sigma_scale, quant=quant, ang_th=ang_th, log_eps=log_eps, density_th=density_th, n_bins=n_bins)
        if self._kind == 'color':  # LineSegmentDetectorはグレースケール画像のみ
            img = cv2.cvtColor(self._bitmap,cv2.COLOR_BGR2GRAY)  # カラー画像はグレースケールにする
            temp.lines, width, prec, nfa = lsd.detect(img) # 線分検出
        else:
            temp.lines, width, prec, nfa = lsd.detect(self._bitmap)

        if temp.lines is None:
            return temp

#        temp._bitmap = lsd.drawSegments(temp._bitmap, temp.lines) # 線の描画
        for line in temp.lines: # 線分を描画する
            x1, y1, x2, y2 = line[0]  # float型のデータになっている
            line_img = cv2.line(temp._bitmap, (int(x1), int(y1)), (int(x2), int(y2)), pcolor, 1)

        return temp
# -------------------------
    def HoughLines(self, rho:float=1.0, theta:float=np.pi/180, threshold:int=200, pcolor=(0,0,255)):
        """ハフ変換で線を求める  古典的ハフ変換  <- 例題どおり動かない
        HoughLinesは２値画像のみ 事前に細線化、または、エッジ検出しておく必要がある
        @param float rho 距離分解能
        @param float theta 角度分解能  180なのか360なのか？
        @param int threshold 投票の閾値パラメータ．十分な票を得た直線のみが出力される
        @param pcolor 描画色

        @return UOpenCV 線分が描画された画像
        @return UOpenCV.lines 直線のベクトル (rho, theta)． rho は原点（画像の左上コーナー）からの距離， theta はラジアン単位で表される直線の回転角度
        @link https://www.hello-python.com/2018/02/27/opencv%E3%82%92%E4%BD%BF%E3%81%84%E3%83%8F%E3%83%95%E5%A4%89%E6%8F%9B%E3%81%A7%E7%94%BB%E5%83%8F%E3%81%8B%E3%82%89%E7%9B%B4%E7%B7%9A%E3%82%92%E6%8E%A2%E3%81%99/ (2022/01/28)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません。事前に細線化しておく必要があります')

        temp = UOpenCV()
        temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("HoughLines(rho={}, theta={}, threshold={})".format(rho, theta, threshold))

        temp.lines = cv2.HoughLines(image=self._bitmap, rho=rho, theta=theta, threshold=threshold)

        temp.lines = np.copy(temp.lines) 
        if temp.lines is None:
            return temp

        for line in temp.lines: # 線分を描画する
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(temp._bitmap, (x1, y1), (x2, y2), pcolor, 1)

        return temp
# -------------------------
    def findContours(self, mode:int=cv2.RETR_TREE, method:int=cv2.CHAIN_APPROX_SIMPLE, minsize:int=100, pcolor=(255,255,255), thickness:int=1):
        """輪郭線を抽出して描画する(輪郭化として利用)
        findContoursは２値画像のみ
        縁が白くなる
        @param int mode 輪郭を検索する方法 cv2.RETR_TREE , cv2.RETR_EXTERNAL
        @param int method 輪郭を近似する方法 cv2.CHAIN_APPROX_SIMPLE 
        @param int minsize 最小サイズ　ノイズを除去する
        @param tuple pcolor 描画色
        @param int thickness 線幅

        @return UOpenCV 輪郭が描画された画像
        @return UOpenCV.contours 抽出された輪郭のリスト
        @return UOpenCV.hierarchy 階層構造
        @link https://pystyle.info/opencv-find-contours/ (2022/01/26)
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_contours/py_contours_begin/py_contours_begin.html (2022/01/26)
        @link https://note.com/npaka/n/naae77d6af87d (2022/01/26)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
#        temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._bitmap = np.full((self.height, self.width, 3), 0, np.uint8)  # 同じ大きさの黒色画像
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("findContours(mode={}, method={}, minsize={})".format(mode, method, minsize))

        temp.contours, temp.hierarchy = cv2.findContours(self._bitmap, mode=mode, method=method)    # 輪郭を抽出する。
        temp.select_contours = list(filter(lambda x: cv2.contourArea(x) > minsize, temp.contours))  # 小さい輪郭は誤検出として削除する
        cv2.drawContours(temp._bitmap, temp.select_contours, -1, color=pcolor, thickness=thickness) # 輪郭を描画する。

        return temp
# -------------------------
# 画像処理　アート効果
# -------------------------
    def oilPainting(self, size:int=3, dynRatio:int=5):
        """油絵のような画像に変換する
        @param int size  近接領域のサイズ
        @param int dynRatio 画像の滑らかさ
        @return UOpenCV
        """
        temp = UOpenCV()
        temp._bitmap = cv2.xphoto.oilPainting(src=self._bitmap, size=size, dynRatio=dynRatio)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("oilPainting(size={}, dynRatio={})".format(size, dynRatio))
        return temp
# -------------------------
    def stylization(self, sigma_s:float=60, sigma_r:float=0.5):
        """水彩画のような画像に変換する
        @param float sigma_s Range between 0 to 200  sigma spatial 近接領域のサイズ
        @param float sigma_r Range between 0 to 1    sigma range   近接領域の異なる色を平均化します。sigma_rを大きくすると、特定の色の領域が広くなります。
        @return UOpenCV
        @link https://qiita.com/shoku-pan/items/454855a8340962eaa05e#%E6%B3%A8%E9%87%88 (2022/05/16)
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._bitmap = cv2.stylization(src=self._bitmap, dst=None, sigma_s=sigma_s, sigma_r=sigma_r)
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)  # カラー画像以外は３チャンネル化する
            temp._bitmap = cv2.stylization(src=temp._bitmap, dst=None, sigma_s=sigma_s, sigma_r=sigma_r)
            temp._bitmap = cv2.cvtColor(temp._bitmap,cv2.COLOR_BGR2GRAY)  # 元に戻す
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("stylization(sigma_s={}, sigma_r={})".format(sigma_s, sigma_r))
        return temp
# -------------------------
    def pencilSketch(self, sigma_s:float=60, sigma_r:float=0.07,shade_factor:float=0.05):
        """鉛筆画のような画像に変換する
        @param float sigma_s Range between 0 to 200  sigma spatial 近接領域のサイズ
        @param float sigma_r Range between 0 to 1    sigma range   近接領域の異なる色を平均化します。sigma_rを大きくすると、特定の色の領域が広くなります。
        @param float shade_factor Range between 0 to 0.1 明るさを調整するパラメータで、0に近いほど暗く、1に近いほど明るくなります。
        @return UOpenCV
        @link https://qiita.com/shoku-pan/items/454855a8340962eaa05e#%E6%B3%A8%E9%87%88 (2022/05/16)
        @return UOpenCV
        """
        temp = UOpenCV()
        if self._kind == 'color':
            temp._gray , temp._bitmap = cv2.pencilSketch(src=self._bitmap, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
        else:
            temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)  # カラー画像以外は３チャンネル化する
            temp._bitmap , temp._temp = cv2.pencilSketch(src=temp._bitmap, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
        if self._kind == 'binary':  # 2値画像はグレースケールになるために、調整している
            threshold, temp._bitmap = cv2.threshold(temp._bitmap, 128, 255, cv2.THRESH_BINARY)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("pencilSketch(sigma_s={}, sigma_r={}, shade_factor={})".format(sigma_s, sigma_r, shade_factor))
        return temp
# -------------------------
    def posterization(self, n:int=4):
        """ポスタリゼーション（減色）
        RGBの全てのチャンネルで色数を n にする。
        @param int n 減色数 (減色して n 階調にする)
        @return UOpenCV
        @link https://qiita.com/ZESSU/items/01b5cefbef7112722f45 (2022/04/21)
        """
        x = np.arange(256)                     # 0,1,2...255までの整数が並んだ配列
        ibins = np.linspace(0, 255, n + 1)     # LUTより入力は255/(n+1)で分割
        obins = np.linspace(0, 255, n)         # LUTより出力は255/nで分割
        num = np.digitize(x, ibins) - 1        # インプットの画素値をポスタリゼーションするために番号付けを行う
        num[255] = n - 1                       # digitize処理で外れてしまう画素値255の番号を修正する
        lut = np.array(obins[num], dtype=int)  # ポスタリゼーションするLUT(LookUpTable)を作成する

        lut = lut.astype(np.uint8)
        temp = UOpenCV()
        temp._bitmap = cv2.LUT(self._bitmap, lut)
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("posterization(n={})".format(n))
        return temp
# -------------------------
# 画像処理　２値画像処理
# -------------------------
    def thinning(self, thinningType:int=cv2.ximgproc.THINNING_ZHANGSUEN):
        """(白い部分の)細線化(スケルトン化) 
        OpenCVは白の部分に着目して処理を行う
        @param int thinningType 細線化の方法 cv2.ximgproc.THINNING_ZHANGSUEN , cv2.ximgproc.THINNING_GUOHALL
        @return UOpenCV
        @link https://emotionexplorer.blog.fc2.com/blog-entry-200.html (2022/01/27)
        thinning は openCV conribution library の ximgprocを利用する
        pip install opencv-python
        pip install opencv-contrib-python 
        として、ライブラリをインストールしておく必要がある。同時に入れないと動かないことがあった
        https://techacademy.jp/magazine/51404 (2022/01/27)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
        temp._bitmap = cv2.ximgproc.thinning(self._bitmap, thinningType=thinningType)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("thinning(thinningType={})".format(thinningType))
        return temp
# -------------------------
    def solation_point_elimination_white(self):
        """白孤立点除去
        @return UOpenCV
        @rink https://mojitoba.com/2018/10/28/fastest_access_numpy_array/ (2022/02/03)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
        temp._bitmap = np.copy(self._bitmap)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("solation_point_elimination_white()")

        src = self._bitmap.tolist() # numpyの配列要素へのアクセスは遅いのでlistにしてアクセスする
        for y in range(1,self.height-1):
            for x in range(1,self.width-1):
                if src[y][x] == 0:
                    continue # 注目する点が黒ならばcontinue
                px = src[y-1][x-1] + src[y-1][x] + src[y-1][x+1] + src[y][x-1] + src[y][x+1] + src[y+1][x-1] + src[y+1][x] + src[y+1][x+1]
                if px == 0:
                    temp._bitmap[y,x] = 0
        return temp
# -------------------------
    def solation_point_elimination_black(self):
        """黒孤立点除去
        @return UOpenCV
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
        temp._bitmap = np.copy(self._bitmap)
        temp._name   = self._name
        temp._kind   = 'binary'
        temp._log    = self._log[:]
        temp._log.append("solation_point_elimination_black()")

        src = self._bitmap.tolist()
        for y in range(1,self.height-1):
            for x in range(1,self.width-1):
                if src[y][x] == 255:
                    continue # 注目する点が白ならばcontinue
                px = src[y-1][x-1] + src[y-1][x] + src[y-1][x+1] + src[y][x-1] + src[y][x+1] + src[y+1][x-1] + src[y+1][x] + src[y+1][x+1]
                if px == 2040:
                    temp._bitmap[y,x] = 255
        return temp
# -------------------------
    def labeling_paint(self, minsize:int, pcolor=(0,0,255)):
        """ラベリング処理  「物体(白)」に色を塗る
        @param int minsize 物体の最小サイズ
        @param pcolor 塗りつぶす色(B,G,R)

        @return UOpenCV 塗りつぶした画像
        @return UOpenCV.num 「物体(白)」の数
        @return UOpenCV.labels ラベル番号が振られた配列(入力画像と同じ大きさ)  サイズでフィルタリングしていない
        @return UOpenCV.selected_stats 物体ごとの座標と面積(ピクセル数)
        label_num, x, y, w, h, size   x, y, w, h は、物体の外接矩形の左上のx座標、y座標、高さ、幅、size は、面積（pixcel）
        label_num は連続していない
        @return UOpenCV.selected_centroids 物体ごとの重心座標 (label_num, x0, y0) 
        @link https://qiita.com/spc_ehara/items/72e878fc131b151c01fa (2022/01/24)
        @link https://dronebiz.net/tech/opencv/labeling (2022/01/24)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
        temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("labeling_paint(minsize={})".format(minsize))

        retval, temp.labels, stats, centroids = cv2.connectedComponentsWithStats(self._bitmap)
        centroids = centroids.astype(np.uint16)

        # 色を塗る
        height = self.height
        width  = self.width
        for y in range(0, height):
            for x in range(0, width):
                lb = temp.labels[y][x]
                if lb > 0 and stats[lb][4]  >= minsize:
                    temp._bitmap[y][x] = pcolor

        # 戻り値を整える
        temp.num = 0; # 最小サイズ以上の物体の数
        temp.selected_stats = np.zeros((1,6),dtype=np.uint16) # 物体ごとの座標と面積 i, x, y, w, h, size
        temp.selected_centroids = np.zeros((1,3),dtype=np.uint16) # 物体ごとの重心座標 i, x, y
        for i in range(1,retval): # 0 は背景の番号
            if stats[i][4] > minsize: # stats[i][4]はsize
                st = np.append(i,stats[i,:]) # 物体のデータを抽出
                temp.selected_stats = np.append(temp.selected_stats,[st],axis=0)
                cr = np.append(i,centroids[i,:])
                temp.selected_centroids = np.append(temp.selected_centroids,[cr],axis=0)
                temp.num = temp.num + 1

        if temp.num > 0: # 物体を検出している場合は、配列の先頭行を除く
            temp.selected_stats = np.delete(temp.selected_stats,0,axis=0)
            temp.selected_centroids = np.delete(temp.selected_centroids,0,axis=0)

        return temp
# -------------------------
    def labeling_overlay(self, minsize:int, pcolor=(0,0,255)):
        """ラベリング処理  「物体(白)」を四角形で囲む
        @param int minisize 最小サイズ
        @param pcolor 描画色(B,G,R)

        @return UOpenCV ラベリングした画像
        @return UOpenCV.num 「物体(白)」の数
        @return UOpenCV.labels ラベル番号が振られた配列(入力画像と同じ大きさ)  サイズでフィルタリングしていない
        @return UOpenCV.selected_stats 物体ごとの座標と面積(ピクセル数)  サイズでフィルタリングしていない
        label_num, x, y, w, h, size   x, y, w, h は、物体の外接矩形の左上のx座標、y座標、高さ、幅、size は、面積（pixcel）
        @return np.ndarray selected_centroids 物体ごとの重心座標 (label_num, x, y)   サイズでフィルタリングしていない
        @link https://okkah.hateblo.jp/entry/2018/08/02/163045 (2022/01/26)
        """
        if self._kind != 'binary':
            raise Exception('２値画像ではありません')

        temp = UOpenCV()
        temp._bitmap = cv2.cvtColor(self._bitmap,cv2.COLOR_GRAY2BGR)
        temp._name   = self._name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("labeling_overlay(minsize={})".format(minsize))

        retval, temp.labels, stats, centroids = cv2.connectedComponentsWithStats(self._bitmap)
        centroids = centroids.astype(np.uint16)

        temp.num = 0; # 最小サイズ以上の物体の数
        temp.selected_stats = np.zeros((1,6),dtype=np.uint16) # 物体ごとの座標と面積 i, x, y, w, h, size
        temp.selected_centroids = np.zeros((1,3),dtype=np.uint16) # 物体ごとの重心座標 i, x, y
        # 物体情報を利用してラベリング結果を表示
        for i in range(1,retval): # 0 は背景の番号
            if stats[i][4] > minsize: # stats[i][4]はsize
                # 各物体の外接矩形を赤枠で表示
                x0 = stats[i][0]
                y0 = stats[i][1]
                x1 = stats[i][0] + stats[i][2]
                y1 = stats[i][1] + stats[i][3]
                cv2.rectangle(temp._bitmap, (x0, y0), (x1, y1), pcolor)

            # 各物体のラベル番号と面積を表示
            #   cv2.putText(temp._bitmap, "ID: " +str(i + 1), (x0, y1 + 15), cv2.FONT_HERSHEY_PLAIN, 1, pcolor)
                cv2.putText(temp._bitmap, str(i), (x0, y1), cv2.FONT_HERSHEY_PLAIN, 1, pcolor)
            #   cv2.putText(temp._bitmap, "S: " +str(stats[i][4]), (x0, y1 + 30), cv2.FONT_HERSHEY_PLAIN, 1, pcolor)
            # 各物体の重心座標を表示
            #   cv2.putText(temp._bitmap, "X: " + str(int(centroids[i][0])), (x1 - 10, y1 + 15), cv2.FONT_HERSHEY_PLAIN, 1, pcolor)
            #   cv2.putText(temp._bitmap, "Y: " + str(int(centroids[i][1])), (x1 - 10, y1 + 30), cv2.FONT_HERSHEY_PLAIN, 1, pcolor)
                st = np.append(i,stats[i,:]) # 物体のデータを抽出
                temp.selected_stats = np.append(temp.selected_stats,[st],axis=0)
                cr = np.append(i,centroids[i,:])
                temp.selected_centroids = np.append(temp.selected_centroids,[cr],axis=0)
                temp.num = temp.num + 1

        if temp.num > 0: # 物体を検出している場合は、配列の先頭行を除く
            temp.selected_stats = np.delete(temp.selected_stats,0,axis=0)
            temp.selected_centroids = np.delete(temp.selected_centroids,0,axis=0)

        return temp
# -------------------------
# 画像処理　逆FFT変換(マスク指定)
# -------------------------
    def idft(self, mask=None):
        """逆FFT変換
        @param mask マスク画像
                    ２値画像でない場合は、内部で２値化する
        @return UOpenCVオブジェクト
        @link http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html (2022/02/23)
        @refer 「実践OpenCV4 for Python」永田雅人、豊沢聡、2021年、(株)カットシステム p241
        """
        if self._kind != 'fft':
            raise Exception("FFT画像ではありません")

        if mask is not None: # 逆fftでマスクをかける
            if mask.width != self.width or mask.height != self.height:
                raise Exception("マスク画像の大きさが合っていません")
            if mask.kind == 'color' or mask.kind == 'gray': # ２値化する
                mask = cv2.cvtColor(mask._bitmap,cv2.COLOR_BGR2GRAY)
                threshold, mask01 = cv2.threshold(mask, 128, 1, cv2.THRESH_BINARY)
            elif mask.kind == 'binary':
                mask01 = mask._bitmap / 255 # 0,1画像にする

            # mask01を3次元にしなければならない
            re = self._fft_complex[:,:,0]
            im = self._fft_complex[:,:,1]
            re = re * mask01 # フーリエ変換象にマスク適用
            im = im * mask01
            fft_complex = cv2.merge((re,im))
        else:
            fft_complex = self._fft_complex[:,:,:]

        fshift = np.fft.fftshift(fft_complex) # データを４分割て並び替える
        dst = cv2.idft(fshift) # 逆FFT変換
        re, im = cv2.split(dst)
        real_image = cv2.normalize(re, None, 0.0, 255.0, cv2.NORM_MINMAX) # 正規化 虚部は0なので使わない

        temp = UOpenCV()
        temp._bitmap = real_image.astype(np.uint8)
        temp._name   = self._name
        temp._kind   = 'gray'
        temp._log    = self._log[:]
        temp._log.append("idft()")
        return temp
# -------------------------
# 画像処理　画像間演算
# -------------------------
    def addWeighted(self,alpha:float, src2, beta:float, gamma:float):
        """画像ブレンド
        画像は同じ大きさ、同じチャンネル数でなければならない
        dst = self * alpha + src2 * beta + gamma の計算を行う
        alpha , beta を足して１にする必要はない
        @param float alpha 重み
        @param UOpenCV src2 演算画像
        @param float beta 重み
        @param float gamma オフセット
        @return カラー画像オブジェクト
        """
        if self.width != src2.width or self.height != src2.height:
            raise Exception('画像の大きさが違います')

        if self._kind != 'color':
            src_a = cv2.cvtColor(self._bitmap, cv2.COLOR_GRAY2BGR)
        else:
            src_a = np.copy(self._bitmap)

        if src2._kind != 'color':
            src_b = cv2.cvtColor(src2.bitmap,cv2.COLOR_GRAY2BGR)
        else:
            src_b = np.copy(src2.bitmap)

        temp = UOpenCV()
        temp._bitmap = cv2.addWeighted(src_a, alpha, src_b, beta, gamma)
        temp._name   = self._name + ' + ' + src2.name
        temp._kind   = 'color'
        temp._log    = self._log[:]
        temp._log.append("addWeighted(alpha={}, src2={}, beta={}, gamma={})".format(alpha, src2.name, beta, gamma))
        return temp
# -------------------------
    def operation(self, src2, op:str):
        """画像間演算
        @param UOpenCV src2  演算する画像
        @param op 演算
        @return カラー画像オブジェクト
        """
        if self.width != src2.width or self.height != src2.height:
            raise Exception('画像の大きさが違います')

        if self._kind != 'color':
            src_a = cv2.cvtColor(self._bitmap, cv2.COLOR_GRAY2BGR)
        else:
            src_a = np.copy(self._bitmap)

        if src2._kind != 'color':
            src_b = cv2.cvtColor(src2.bitmap,cv2.COLOR_GRAY2BGR)
        else:
            src_b = np.copy(src2.bitmap)

        temp = UOpenCV()
        if op == 'ADD': # switch文がないからこんな書き方になる
            temp._bitmap = cv2.add(src_a, src_b)
        elif op == 'SUB':
            temp._bitmap = cv2.subtract(src_a, src_b)
        elif op == 'MUL':
            temp._bitmap = cv2.multiply(src_a, src_b)
        elif op == 'DIV':
            temp._bitmap = cv2.divide(src_a, src_b)
        elif op == 'ABS':
            temp._bitmap = cv2.absdiff(src_a, src_b)
        elif op == 'MAX':
            temp._bitmap = cv2.max(src_a, src_b)
        elif op == 'MIN':
            temp._bitmap = cv2.min(src_a, src_b)
        elif op == 'AND':
            temp._bitmap = cv2.bitwise_and(src_a, src_b)
        elif op == 'OR':
            temp._bitmap = cv2.bitwise_or(src_a, src_b)
        elif op == 'XOR':
            temp._bitmap = cv2.bitwise_xor(src_a, src_b)
        else:
            raise Exception('未定義演算')

        temp._name = '{} {} {}'.format(self._name, op, src2.name)
        temp._kind = 'color'
        temp._log  = self._log[:]
        temp._log.append("operation(op={}, {})".format(op, src2.name))
        return temp
# -------------------------
# 物体抽出
# -------------------------
    def sampling_bgr(self, lower, upper):
        """BGR指定で物体を抽出する
        @param np.array lower 抽出する色の下限(BGR) (0,   0, 200) 
        @param np.array upper 抽出する色の上限(BGR) (50, 50, 255) 
        @return UOpenCV
        @link https://rikoubou.hatenablog.com/entry/2019/02/21/190310 (2022/01/24)
        """
        if self._kind != 'color':
            raise Exception('カラー画像以外対応していません')

        temp = UOpenCV()
        img_mask = cv2.inRange(self._bitmap, tuple(lower), tuple(upper)) # BGRからマスクを作成
        temp._bitmap = cv2.bitwise_and(self._bitmap, self._bitmap, mask=img_mask) # 元画像とマスクを合成
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("sampling_bgr(lower={}, upper={})".format(lower, upper))
        return temp
# -------------------------
    def sampling_hsv(self, lower, upper):
        """HSV指定で物体を抽出する
        @param np.array lower 抽出する色の下限(HSV) (30, 153, 255) 
        @param np.array upper 抽出する色の上限(HSV) 
        @return UOpenCV
        @link https://rikoubou.hatenablog.com/entry/2019/02/21/190310 (2022/01/24)
        """
        if self._kind != 'color':
            raise Exception('カラー画像以外対応していません')

        temp = UOpenCV()
        hsv = cv2.cvtColor(self._bitmap, cv2.COLOR_BGR2HSV)      # 画像をHSVに変換
        img_mask = cv2.inRange(hsv, tuple(lower), tuple(upper))  # HSVからマスクを作成
        temp._bitmap = cv2.bitwise_and(self._bitmap, self._bitmap, mask=img_mask) # 元画像とマスクを合成
        temp._name   = self._name
        temp._kind   = self._kind
        temp._log    = self._log[:]
        temp._log.append("sampling_hsv(lower={}, upper={})".format(lower, upper))
        return temp
# -------------------------
# 補助関数
# -------------------------
    def imshow(self,id=None,flags=cv2.WINDOW_NORMAL):
        """画像を表示する
        日本語のキャプションは文字化けする
        @param id ウインドウの識別文字　識別文字は他の表示ウインドウと重ならないようにする
        @param flags cv2.WINDOW_NORMAL ウインドウの大きさ可変 
                     cv2.WINDOW_AUTOSIZE ウインドウの大きさ変更不可
        """
        if self._bitmap is None:
            return

        if id is None:
            caption = self._name + ' ' + self._log[-1]
        else:
            caption = str(id)

        cv2.namedWindow(caption, flags)
        # cv2.moveWindow(wname, x, y) ウインドウの初期位置を調整する場合
        cv2.resizeWindow(caption, self.width, self.height)
        cv2.imshow(caption, self._bitmap) # 日本語のキャプションは文字化けする
        return self
# -------------------------
    def waitKey(self):
        """キー入力待ち
        """
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return self
# -------------------------
    @staticmethod
    def read_lookuptable(fname: str):
        """ルックアップテーブルのデータを読み込む
        openCVは日本語のファイル名には対応していないので、xml.etree.ElementTree を利用している
        @link https://qiita.com/tatamyiwathy/items/059ec57b8291ca3ff890 (2022/01/07)
        @param str fname : ファイル名
        @return np.darray lookup_table : ルックアップテーブルデータ
        @return str name : ルックアップテーブルの名前
        @return str description : 説明
        @usage lut, name, description = UOpenCV.read_lookuptable(fname)
        """
        tree = et.parse(fname)
        root = tree.getroot()

        xml_kind = root.find('xml_kind').text
        if xml_kind != 'ルックアップテーブル':
            raise Exception('ルックアップテーブルのデータではありません')

        name = root.find('name').text
        description = root.find('description').text

        lut = root.find('lut')
        rows = int(lut.find('rows').text)  # 256
        cols = int(lut.find('cols').text)  # 1
        dt = lut.find('dt').text  # u  np.uint8

        data = lut.find('data').text
        lut = np.array(data.split(), dtype=np.uint8)  # 整数の１次元配列
        return lut, name, description
# -------------------------
    @staticmethod
    def read_2Dfilter(fname: str):
        """空間フィルタのデータを読み込む
        openCVは日本語のファイル名には対応していない
        @link https://qiita.com/tatamyiwathy/items/059ec57b8291ca3ff890 (2022/01/07)
        @param str fname : ファイル名
        @return float multiplier : 乗数
        @return float divisor : 除数
        @return np.darray kernel : カーネル
        @return float offset : 加算する数
        @return name : フィルタの名前
        @return description : 説明
        @usage multiplier, divisor, k_mat, offset, name, description = UOpenCV.read_2Dfilter(fname)
        """
        tree = et.parse(fname)
        root = tree.getroot()

        xml_kind = root.find('xml_kind').text
        if xml_kind != '空間フィルタ':
            raise Exception('空間フィルタのデータではありません')

        name = root.find('name').text
        description = root.find('description').text
        multiplier = float(root.find('multiplier').text)
        divisor = float(root.find('divisor').text)
        offset = float(root.find('offset').text)

        kernel = root.find('kernel')
        rows = int(kernel.find('rows').text)
        cols = int(kernel.find('cols').text)
        dt = kernel.find('dt').text

        data = kernel.find('data').text
        k_mat = np.array(data.split(), dtype=float)  # 実数の１次元配列
        k_mat = np.reshape(k_mat, (rows, cols))  # 多次元配列

        return multiplier, divisor, k_mat, offset, name, description
# -------------------------
    @staticmethod
    def blank_image(height:int,width:int,color:int=0):
        """高さと幅を指定して単色の画像を作る
        @param int height 高さ
        @param int width 幅
        @param int color 色
        @return UOpenCV
        """
        temp = UOpenCV()
        temp._bitmap = np.full((height, width, 3),color, np.uint8)
        temp._name: str = "blank"
        temp._kind: str = "color"
        temp._log: list = list() # 処理履歴
        temp._log.append("blank_image()")
        return temp
# -------------------------
