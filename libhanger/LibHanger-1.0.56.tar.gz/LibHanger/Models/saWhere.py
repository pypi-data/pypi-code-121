from __future__ import annotations
from enum import Enum

class saWhere():
    
    __and = []
    """ and条件格納用配列 """

    __or = []
    """ or条件格納用配列 """

    __where = dict()
    """ Where条件格納用ディクショナリ """
    
    class whereKind(Enum):
        
        """
        Where句種別列挙体
        """
        
        _and = 0
        """ and条件 """

        _or = 1
        """ or条件 """
        
    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        self.__where[self.whereKind._and] = self.__and
        self.__where[self.whereKind._or] = self.__or
    
    @property
    def where(self):

        """ 
        where条件dict 
        """
        
        return self.__where
    
    @property
    def andList(self):

        """ 
        and条件list 
        """

        return self.__and

    @property
    def orList(self):

        """ 
        or条件list 
        """

        return self.__or
    
    def clear(self):
        
        """
        初期化
        """
        
        self.__and.clear()
        self.__or.clear()
        self.__where.clear()
        
    def and_(self, w) -> saWhere:

        """ 
        and条件list追加 
        
        Parameters
        ----------
        w : Any
            抽出条件
        """

        # list追加
        self.__and.append(w)

        # 戻り値を返す
        return self
    
    def or_(self, w) -> saWhere:

        """ 
        or条件list追加 

        Parameters
        ----------
        w : Any
            抽出条件
        """

        # list追加
        self.__or.append(w)

        # 戻り値を返す
        return self
