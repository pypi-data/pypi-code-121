from __future__ import annotations
#from enum import Enum
from sqlalchemy import asc,desc

class saOrderBy():
    
    __orderBy = dict()
    """ Orderby格納用ディクショナリ """

    def __init__(self) -> None:
        
        """
        コンストラクタ
        """
        
        self.__sortLevel = 0
        
    @property
    def orderBy(self):
        
        """
        orderBy句dict
        """
        
        return self.__orderBy

    def clear(self):
        
        """
        初期化
        """
        
        self.__sortLevel = 0
        self.__orderBy.clear()
    
    def asc_(self, s) -> saOrderBy:

        """
        asc(昇順)追加
        
        Parameters
        ----------
        s : Any
            ソート条件

        """

        # sortLevel++
        self.__sortLevel += 1

        # dict追加
        self.__orderBy[self.__sortLevel] = asc(s)

        # 戻り値を返す
        return self
    
    def desc_(self, s) -> saOrderBy:

        """
        desc(降順)追加
        
        Parameters
        ----------
        s : Any
            ソート条件

        """

        # sortLevel++
        self.__sortLevel += 1
        
        # dict追加
        self.__orderBy[self.__sortLevel] = desc(s)

        # 戻り値を返す
        return self
