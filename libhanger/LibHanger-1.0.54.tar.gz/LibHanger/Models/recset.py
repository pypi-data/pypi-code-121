import inspect
import pandas as pd
import copy
import LibHanger.Library.uwLogger as Logger
from typing import TypeVar, Generic
from enum import Enum
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import and_, or_
from sqlalchemy import asc
from LibHanger.Models.fields import fields
from LibHanger.Library.DataAccess.Base.uwDataAccess import uwDataAccess
from LibHanger.Library.uwDeclare import uwDeclare as en
from LibHanger.Models.saWhere import saWhere
from LibHanger.Models.saOrderBy import saOrderBy

T = TypeVar('T')

class recset(Generic[T]):
    
    """
    レコードセットクラス
    """

    __ROWSTATE_COLNAME__ = '__rowState'
    """ 行状態列名 """

    __SA_INSTANCE_STATE__ = '_sa_instance_state'
    """ _sa_instance_state """
    
    class rowState(Enum):

        """
        行状態クラス
        """
        
        noChanged = 0
        """ 変更なし """
        
        added = 1
        """ 追加 """
        
        modified = 2
        """ 変更 """
        
        deleted = 3
        """ 削除 """
    
    class findOption(Enum):
        
        """
        検索モード
        """
        
        cacheOnly = 0
        """ キャッシュのみ検索 """

        cacheAndDataBase = 1
        """ キャッシュとDBの両方検索 """
    
    class upsertResult():
        
        """
        upsert処理結果クラス
        """
        
        result = en.resultRegister.success
        """ 処理結果 """

        exceptInfo = None
        """ 例外情報 """
    
    def __init__(self, t, __da:uwDataAccess = None, __where = None) -> None:
        
        """
        コンストラクタ
        
        Parameters
        ----------
        t : Any
            Modelクラス
        __da : Any
            データアクセスクラスインスタンス
        __where : Any
            Where条件
        """
        
        # Modelクラス
        self.modelType = t

        # DataAccessクラス保持
        self.__da = __da
        
        # カラム情報
        self.__columns = self.__getColumnAttr()
        
        # 主キー情報
        self.__primaryKeys = self.__getPrimaryKeys()

        # 行情報初期化
        self.__rows = []
        self.__dfrows = None
        if not self.__da is None and not self.__da.session is None and not __where is None:
            self.filter(__where)
        else:
            self.__initRows()
            
        # 現在行位置初期化
        self.__currentRowIndex = -1

        # フィールドクラス
        self.__fields = fields(self.__rows, self.__dfrows)
        
        # 一時セッションフラグ
        self.__tempSessionFlg = False
        
    @property
    def recSetName(self):
        
        """
        レコードセット名
        """
        
        return self.modelType.__tablename__
    
    @property
    def recordCount(self):
        return len(self.rows)
    
    @property
    def session(self):
        
        """
        DBセッション
        """
        
        #return self.__session
        return self.__da.session
    
    @property
    def rows(self):
        
        """
        行情報(List)
        """
        
        return self.__rows
    
    @property
    def dfrows(self):
        
        """
        行情報(DataFrame)
        """
        
        return self.__fields.dfrows
    
    @property
    def columns(self):
        
        """
        カラム情報
        """
        
        return self.__columns
    
    @property
    def primaryKeys(self):
        
        """
        主キー情報プロパティ
        """
        
        return self.__primaryKeys

    @property
    def State(self) ->int:
        
        """
        行状態(getter)
        """
        
        return self.__rows[self.__currentRowIndex].__rowState
    
    @State.setter
    def State(self, __rowState):
        
        """
        行状態(setter)
        """
        
        # rowsのカレント行の行状態をmodifiedに変更
        if self.__rows[self.__currentRowIndex].__rowState == self.rowState.noChanged:
            self.__rows[self.__currentRowIndex].__rowState = __rowState

        # dfrowsのカレント行の行状態をmodifiedに変更
        if self.__dfrows.loc[self.__currentRowIndex, self.__ROWSTATE_COLNAME__] == self.rowState.noChanged:
            self.__dfrows.loc[self.__currentRowIndex, self.__ROWSTATE_COLNAME__] = __rowState

    def fields(self, __columnName:T):
        
        """
        レコードセットフィールド情報
        """
        
        # カラム名をfieldsに渡す
        self.__fields.columnName = __columnName
        
        # カレント行インデックスをfieldsに渡す
        self.__fields.currentRowIndex = self.__currentRowIndex
        
        return self.__fields
    
    def __initdfrows(self):
        
        """
        dfrows初期化(Dataframe)
        """
        
        # 列リスト生成
        colList = []
        for col in self.__columns:
            colList.append(col[0])
        colList.append(self.__ROWSTATE_COLNAME__)
        colList.sort()
        
        # DataFrame化
        df = pd.DataFrame(columns=colList)
        
        # 主キーセット
        if len(self.__primaryKeys) > 0:
            df = df.set_index(self.__primaryKeys, drop=False)

        # 戻り値を返す
        return df
    
    def __getColumnAttr(self):
        
        """
        モデルクラスのインスタンス変数(列情報)取得

        Parameters
        ----------
        None
        
        """
        
        # インスタンス変数取得
        attributes = inspect.getmembers(self.modelType, lambda x: not(inspect.isroutine(x)))
        
        # 特定のインスタンス変数を除外してリストとしてインスタンス変数を返す
        return list(filter(lambda x: not(x[0].startswith("__") or x[0].startswith("_") or x[0] == "metadata" or x[0] == "registry"), attributes))
    
    def __getPrimaryKeys(self):
        
        """
        主キー情報取得

        Parameters
        ----------
        None
        
        """
        
        # 主キーリスト作成
        primaryKeys = []
        for col in self.__columns:

            memberInvoke = getattr(self.modelType, col[0])
            if memberInvoke.primary_key == True:
                primaryKeys.append(col[0])
        
        # 主キー情報を返す
        return primaryKeys
    
    def __getPKeyFilter_sa(self, row):
        
        """
        主キー条件取得(SQL Alchemy用)
        
        row : Any
            行情報
        """
        
        # 主キー条件リスト初期化
        pKeyList = []
        
        # 主キーのみで条件を組み立て
        for key in self.__getPrimaryKeys():
            w = (getattr(self.modelType, key) == getattr(row, key))
            pKeyList.append(w)
        
        # 主キー条件リストをtupleに変換して返す
        return and_(*tuple(pKeyList))
    
    def __rowSetting(self, row):
        
        """
        行情報を生成する
        
        Parameters
        ----------
        row : Any
            行情報
        """
        
        for col in self.__columns:

            # Modelのインスタンス変数取得
            memberInvoke = getattr(self.modelType, col[0])
            # 既定値の設定
            setattr(row, col[0], memberInvoke.default.arg)
        
        # 生成した行を返す
        return row
    
    def __addRecrow(self):
        
        """
        レコードセット行追加処理
        """
        
        # カレント行インデックス++
        self.__currentRowIndex += 1

        # 行生成
        row = self.modelType()
        
        # 行状態列を追加
        row.__rowState = self.rowState.noChanged

        # List - add
        self.__rows.append(self.__rowSetting(row))

        # DataFrame - add
        self.__addRecrowDataFrame(row, self.__currentRowIndex)
    
        # 行状態をaddedに変更
        self.State = self.rowState.added

    def __addRecrowDataFrame(self, row, targetRowIndex):
        
        """
        対象行をレコードソース(DataFrame)に追加する
        
        Parameters
        ----------
        row : Any
            行情報
        targetRowIndex : int
            DataFrame行インデックス

        """
        
        # 行情報コピー
        lrow = []
        lrow.append(row)
        targetRow = self.__deepCopyRow(lrow)[0]

        # deepcopyしたrowをdict化
        dictRow = vars(targetRow)
        dictRow_sorted = sorted(dictRow.items())
        
        # value取得
        dfValList = [val[1] for val in dictRow_sorted]

        # カレント行にvalue設定
        self.__dfrows.loc[targetRowIndex] = dfValList
    
    def __editRecrow(self):
        
        """
        レコードセットを編集状態にする
        """
        
        # 行状態をmodifiedに変更
        self.State = self.rowState.modified
        
    def __initRows(self):
        
        """
        行情報をリセットする
        """
        
        self.__rows = []
        self.__dfrows = self.__initdfrows()
    
    def __deepCopyRow(self, rows:list) -> list:
        
        """
        行情報をコピーする
        
        Parameters
        ----------
        rows : list
            行情報リスト
        """

        # 行インスタンスをDeepCopy
        targetRows = copy.deepcopy(rows)
        # DataFrame化で不要な列を削除
        for rowInstance in targetRows:
            delattr(rowInstance, self.__SA_INSTANCE_STATE__)
            
        return targetRows

    def __getKeyTuple(self, row):
        
        """
        rowのキー値をtupleで取得

        Parameters
        ----------
        row : Any
            行情報
        """
        
        # 主キー値リスト初期化
        pKeyValueList = []
    
        # 主キー値をリストに追加
        for key in self.__getPrimaryKeys():
            pKeyValueList.append(getattr(row, key))
        
        # tupleに変換(dictrowのKeyにする)
        return tuple(pKeyValueList)

    def __checkSessionOpen(self, __autoCommit = True, __beginTransaction = False):

        """
        セッションチェック(Open)

        Parameters
        ----------
        __autoCommit : bool
            AutoCommit
        __beginTransaction : bool
            Sessionを開いた時にトランザクションを開始するか

        """
        
        # sessionがNoneの場合はautocommit=Onで接続を開く
        if self.__da.session is None:
            self.__da.openSession(__autoCommit)
            self.__da.beginTransaction()
            self.__tempSessionFlg = True
        else:
            # autocommit=Onの場合はtransactionを開始する
            if self.__da.autoCommit and \
               self.__da.session.transaction is None and \
               __beginTransaction:
                self.__da.beginTransaction()
    
    def __checkSessionClose(self):
        
        """
        セッションチェック(Close)

        Parameters
        ----------
        None
        
        """
        
        if not self.__da.session is None and self.__tempSessionFlg:
            self.__da.closeSession()
            self.__tempSessionFlg = False

    def setDA(self, __da:uwDataAccess):

        """
        DataAccessクラスインスタンスセット

        Parameters
        ----------
        __da : uwDataAccess
            DataAccessクラスインスタンス
        """

        if self.__da is None:
            self.__da = __da

    def newRow(self):
        
        """
        新規行を生成する

        Parameters
        ----------
        None

        """

        # 新規行情報生成
        self.__addRecrow()
    
    def editRow(self):
        
        """
        レコードセットを編集状態にする

        Parameters
        ----------
        None

        """
        
        # 編集状態にする
        self.__editRecrow()

    def delRow(self):
        
        """
        レコードセットのカレント行を削除対象とする
        """

        # 行状態をdeletedに変更
        self.State = self.rowState.deleted

    def first(self):
        
        """
        カレント行を先頭にする
        """
        
        self.__currentRowIndex = -1
    
    def eof(self):
        
        """
        レコードセットの行情報有無を返す
        
        Parameters
        ----------
        None
        
        """

        # カレント行インデックス++
        self.__currentRowIndex += 1

        return False if len(self.__rows) > self.__currentRowIndex else True
    
    def getDataFrame(self, __rows = None):
        
        """
        Model⇒DataFrameに変換する

        Parameters
        ----------
        __rows : list
            行情報リスト

        """
        
        rows = self.__rows if __rows is None else __rows
        collist = []
        if len(rows) == 0:
            for column in self.__columns:
                collist.append(column[0])
        else:
            
            # 行情報コピー
            targetRows = self.__deepCopyRow(rows)
            
            # 行インスタンスをリスト化
            rowlist = list(map(lambda f: vars(f), targetRows))

        # rowlistをDataFrame変換
        df = pd.DataFrame(rowlist) if len(rows) > 0 else pd.DataFrame(columns=collist)
        
        # DataFrameに主キー設定
        if len(self.__primaryKeys) > 0 and len(rows) > 0:
            df = df.set_index(self.__primaryKeys, drop=False)
        
        # 戻り値を返す
        return df
    
    def filterExpr(self, w, s = None):
        
        """
        フィルタ条件適用
        
        Parameters
        ----------
        w : Any | asWhere
            抽出条件
        s : Any | asOrderBy
            ソート順
        """
        
        # Where条件
        if not type(w) is saWhere:
            q = self.__da.session.query(self.modelType).filter(w)
        else:
            q = self.__da.session.query(self.modelType)
            
            # where条件キャスト
            wx:saWhere = w
            
            # AND
            if len(wx.andList) > 0:
                q = q.filter(and_(*tuple(wx.andList)))
            
            # OR
            if len(wx.orList) > 0:
                q = q.filter(or_(*tuple(wx.orList)))
        
        # Sort順
        if s is None:
            for pKey in self.__primaryKeys:
                q = q.order_by(asc(getattr(self.modelType, pKey)))
        elif not type(s) is saOrderBy:
            q = q.order_by(s)
        else:
            
            # OrderByキャスト
            sx:saOrderBy = s
            
            # OrderBy 組み立て
            if len(sx.orderBy) > 0:
                # keyでソート
                sort_orderBy = sorted(sx.orderBy.items())
                for sortKey in sort_orderBy:
                    q = q.order_by(sortKey[1])
        
        # 戻り値を返す
        return q
    
    def convertDataFrameExpr(self, df, w):
        
        """
        sqlAlchemyのfilter条件をDataFrameのfilter条件に変換
        
        df : DataFrame
            対象DataFrame
        w : any | asWhere
            where条件
        """
        
        if not type(w) is saWhere:
            return w
        else:
            # where条件キャスト
            wx:saWhere = w

            # 条件格納用リスト初期化
            andExprList = []
            orExprList = []
            
            # AND
            if len(wx.andList) > 0:
                for expr in wx.andList:
                    andExpr:BinaryExpression = expr
                    if not type(andExpr.right.value) is list:
                        andExprList.append(df[andExpr.left.key] == andExpr.right.value)
                    else:
                        dfInExpr = None
                        for rval in andExpr.right.value:
                            dfInExprTmp = (df[andExpr.left.key] == rval)
                            dfInExpr = (dfInExpr | dfInExprTmp) if not dfInExpr is None else dfInExprTmp
                        andExprList.append(dfInExpr)
            # OR
            if len(wx.orList) > 0:
                for expr in wx.orList:
                    orExpr:BinaryExpression = expr
                    orExprList.append(df[orExpr.left.key] == orExpr.right.value)
            
            # DataFrame用のwhere条件組み立て
            retExpr = None
            for expr in andExprList:
                retExpr = retExpr & expr if not retExpr is None else expr
            for expr in orExprList:
                retExpr = retExpr | expr if not retExpr is None else expr

            # 戻り値を返す
            return retExpr
        
    def filter(self, w, s = None):
        
        """
        レコードセットをフィルタする
        結果セットはdbから取得

        Parameters
        ----------
        w : any | asWhere
            where条件
        s : Any | asOrderBy
            ソート順
        """
        
        # 行情報初期化
        self.__initRows()
        
        # フィールドクラス
        self.__fields = fields(self.__rows, self.__dfrows)

        # セッションチェック
        self.__checkSessionOpen(False, False)

        # クエリ実行
        rowIndex = 0
        q = self.filterExpr(w, s).all()
        for row in q:
            # 行状態をnoChangedに変更
            row.__rowState = self.rowState.noChanged
            # rowsにクエリ結果を追加
            self.__rows.append(row)
            # DataFrame - add
            self.__addRecrowDataFrame(row, rowIndex)
            rowIndex += 1
        
        # セッションチェック
        self.__checkSessionClose()
        
        # カレント行インデックス初期化
        self.__currentRowIndex = -1

    def find(self, w, searchOption = findOption.cacheOnly):
        
        """
        現在保持しているレコードセットに指定した条件に合致するレコードが存在するか返す

        Parameters
        ----------
        w : Any
            抽出条件
        searchOption : findOption
            検索方法
        """
        
        # 条件抽出
        dfw = self.convertDataFrameExpr(self.__dfrows, w)
        dfCheck = self.__dfrows[dfw]
        
        # filter
        if searchOption == self.findOption.cacheOnly:
            # 戻り値を返す
            return True if len(dfCheck) > 0 else False
        elif searchOption == self.findOption.cacheAndDataBase:
            
            # セッションチェック
            self.__checkSessionOpen(False, False)
            # クエリ実行
            q = self.filterExpr(w).all()
            # セッションチェック
            self.__checkSessionClose()
            # 戻り値を返す
            return True if len(dfCheck) > 0 or len(q) > 0 else False

    def existsPKeyRec(self, row, sessionCheck = False):
        
        """
        対象行に対して主キー制約に違反しているか

        Parameters
        ----------
        row : Any
            行情報
        """

        # セッションチェック
        if sessionCheck:
            self.__checkSessionOpen(False, False)
        
        # 主キーを条件として該当レコードが存在するか確認
        w = self.__getPKeyFilter_sa(row)
        q = self.__da.session.query(self.modelType).filter(w).all()
        for qrow in q:
            
            dictRow = vars(row)
            dictRow_sorted = sorted(dictRow.items())
            for col in dictRow_sorted:
                if col[0] == self.__SA_INSTANCE_STATE__: continue
                setattr(qrow, col[0], getattr(row, col[0]))
            
            self.__rows.append(qrow)
            self.rows.remove(row)

        # セッションチェック
        if sessionCheck:
            self.__checkSessionClose()

        # 結果を返す
        return len(q) > 0

    def merge(self, srcRecset):
        
        """
        レコードセットをマージする

        Parameters
        ----------
        srcRecset : Any
            マージ元レコードセット
            
        Notes
        -----
            マージ先に同一のキー情報が存在した場合はマージ対象から除外
        """
        
        # rows⇒dict変換
        dictrows = dict()
        for row in self.__rows:
            
            # tupleに変換(dictrowのKeyにする)
            pKeyTuple = self.__getKeyTuple(row)
            
            # rowをdictrowsにセット
            if not pKeyTuple in dictrows:
                dictrows[pKeyTuple] = row
            
        # マージ対象レコードセットをrowsに追加
        for mergeRow in srcRecset.rows:
            
            # rowのキー値取得
            pKeyTuple = self.__getKeyTuple(mergeRow)
            
            # キー値がdictrowに無ければ__dictrowsに追加
            if not pKeyTuple in dictrows:
                dictrows[pKeyTuple] = mergeRow

        # dictrowsをソート
        rows_sorted = sorted(dictrows.items())
        
        # rows再構築
        self.__rows.clear()
        for row in rows_sorted:
            self.__rows.append(row[1])
        
        # dfrows再構築
        self.__dfrows = self.__dfrows.drop(range(len(self.__dfrows)))
        rowIndex = 0
        for row in rows_sorted:
            self.__addRecrowDataFrame(row[1], rowIndex)
            rowIndex += 1
        
        # fields再構築
        self.__fields = fields(self.__rows, self.__dfrows)
    
    def upsert(self):

        """
        データ更新(upsert用)
        
        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反している場合、強制的にmodifiedとして扱う。\n
            recsetに存在する追加行(rowState = added)全てに対して存在チェックが走るので \n
            件数によっては更新にかなりの時間を要する。
            削除行に関してはレコード抽出後にdeleteメソッドを走らせるはずなので存在チェックは行っていない。
        """

        return self.update(True)
    
    def update(self, upsert = False) -> upsertResult:
        
        """
        データ更新(通常用)
        
        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反していればSQLAlchemyErrorとなる。\n
            recset側でDBとの制約を解決していればupsertよりこちらのほうが速度は上
        """
        
        # 処理結果クラスインスタンス
        upResult = self.upsertResult()
        
        try:
            
            # セッションチェック
            self.__checkSessionOpen(True, True)
            
            # 新規行はaddする
            newRows = [row for row in self.__rows if row._recset__rowState == self.rowState.added]
            for newRow in newRows:
                # 主キー違反していない行のみadd
                if upsert == False or not self.existsPKeyRec(newRow):
                    self.__da.session.add(newRow)

            # 削除行はdeleteする
            delRows = [row for row in self.__rows if row._recset__rowState == self.rowState.deleted]
            for delRow in delRows:
                self.__da.session.delete(delRow)
            
            # flush
            self.__da.session.flush()
            
            # Commit
            if self.__da.autoCommit and not self.__da.session.transaction is None:
                self.__da.session.commit()

            # セッションチェック
            self.__checkSessionClose()

            # 処理結果セット
            upResult.result = en.resultRegister.success
            
        except SQLAlchemyError as e:
            
            # エラーログ出力
            Logger.logging.error(e)

            # 処理結果セット
            upResult.result = en.resultRegister.failure
            upResult.exceptInfo = e
            
            # Rollback
            if self.__da.autoCommit:
                self.__da.session.rollback()
            
        # 処理結果を返す
        return upResult