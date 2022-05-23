# -*- coding: utf-8 -*-
class EngineFactory():
    def create_engine(self, engine_class):
        return engine_class()
    
    def __init__(self, engine_class):
        self._fetch_engine = self.create_engine(engine_class)



class SelFutFactorFactory(EngineFactory):
    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.sel_fut_factor(codes=codes, key=key, columns=columns)