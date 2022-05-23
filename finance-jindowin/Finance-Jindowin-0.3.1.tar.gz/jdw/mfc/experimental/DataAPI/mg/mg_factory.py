# -*- coding: utf-8 -*-
import pdb
class EngineFactory():
    def create_engine(self, engine_class):
        return engine_class()
    
    def __init__(self, engine_class=None):
        self._engine = self.create_engine(engine_class) \
            if engine_class is not None else None

class Research(EngineFactory):
    def operation(self, **kwargs):
        return self._engine.research(table_name='research', **kwargs)


class Account(EngineFactory):
    def operation(self, **kwargs):
        return self._engine.account(table_name='account', **kwargs)