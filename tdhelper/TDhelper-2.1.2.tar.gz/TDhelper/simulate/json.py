#! python 3.6
#--------------------------------------------------------
#| @File    :   json.py
#| @ClsName :   simulateJson
#| @Version :   1.0.0
#| @History :
#|-------------------------------------------------------------------------|
#| Type     | Author   | Contact          | Time                           |
#|-------------------------------------------------------------------------|
#| Create   | Tony.Dom  | yeihizhi@163.com  | 2021-10-30 22:30:33          |
#|-------------------------------------------------------------------------|
#| @License :   MIT
#| @Desc    :   simulate json record by json cfg.

#| import lib by pypi

#| import lib by project
# 
#--------------------------------------------------------

class simulateJson:
    def __init__(self, cfg):
        '''__init__
        
        init simulateJson.
        
        Args:
            cfg (dict): json record template config. you can get help by file test.json 
        
        Returns:
            None.
        
        Raises:
        
            arguments 'cfg' can not is none: the cfg can not is none.
            serviceBase return False: call back has an error.

        '''
        try:
            self.status = False
            self.cfg = cfg
            self.__AST__=[]
            assert self.cfg and hasattr(self.cfg,'baseCfg') and hasattr(self.cfg,"dataCfg"), "arguments 'cfg' can not is none."
            if(self.__serviceBase__(self.baseCfg)):
                self.execute(self.dataCfg)
            else:
                raise "serviceBase return False."
        except Exception as e:
            self.status = True
            raise e

    def __serviceBase__(self,cfg):
        return True

    def __analysis__(self,cfg):
        '''analysis
        
        analysis dataCfg, to create AST.
        
        Args:
            cfg (dict): desc
        
        Returns:
            True: analysis success.
            False: analysis fail.
        
        Raises:
            config file dataCfg must is [] object: dataCfg type must is [].
            config file dataCfg node can not found node 'name' or 'cfg': data Cfg node must has 'name' and 'cfg' node.
        
        '''
        assert isinstance(cfg,list), "config file dataCfg must is [] object."
        for v1 in cfg:
            assert hasattr(v1,"name") and hasattr(v1,"cfg"), "config file dataCfg node can not found node 'name' or 'cfg'."

        pass
    
    def __intType__(self,cfg):
        pass

    def __strType__(self,cfg):
        pass

    def __doubleType__(self,cfg):
        pass

    def __booleType__(self,cfg):
        pass
    def __arrayType__(self,cfg):
        pass
    
    def __objectType__(self,cfg):
        pass