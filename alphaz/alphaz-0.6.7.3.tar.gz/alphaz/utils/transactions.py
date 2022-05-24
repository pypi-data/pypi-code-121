from threading import Thread, Event
import os, datetime, uuid, time, math, ast
from typing import List, Dict

from alphaz.models.database.structure import AlphaDatabase
from alphaz.models.main import AlphaClass, AlphaTransaction

from ..libs import transactions_lib

from core import core

LOG = core.get_logger('requests')
DB = core.db

class TransactionsThread(Thread):    # PowerCounter class
    def __init__(self, function, 
            message_types:List[str] = [], 
            database: AlphaDatabase = DB, 
            interval: int = 2,
            timeout: int = 0, 
            pool_size:int = 20, 
            answer_lifetime = 3600,
            args = [], 
            kwargs = {}
        ):

        Thread.__init__(self)

        self.function = function
        self.message_types:List[str]  = message_types
        self.database: AlphaDatabase = database
        self.interval:str = interval
        self.timeout = timeout
        self.pool_size:int = pool_size
        self.answer_lifetime: int = answer_lifetime
        self.args:list = args
        self.kwargs:dict = kwargs

        self.started: Event = Event()
        self.running: Event= Event()
        self.finished: Event = Event()        

    def ensure(self):
        if not self.started.is_set() and not self.running.is_set():
            self.start()

    def run(self):
        self.started.set()

        count = 0
        offset = 0
        elapsed = 0
        dts = datetime.datetime.now()
        while not self.finished.is_set() and (self.timeout <= 0 or elapsed < self.timeout):
            dt = datetime.datetime.now()
            
            if not self.running.is_set():
                self.running.set()

            if count == 0:
                #secs = (math.ceil(dt) - dt).total_seconds()
                secs = 0
            else:
                secs = self.interval - offset
                
            self.finished.wait(secs)
            if not self.finished.is_set():
                t = time.time()

                self.process()

                offset = time.time() - t
                count += 1
            
            elapsed = (dt - dts).total_seconds()

        if self.timeout > 0 and elapsed > self.timeout:
            LOG.info("Thread reachs its limit")
        else:
            LOG.info("Thread ended")

    def process(self):
        requests = transactions_lib.get_requests(self.database, message_types=self.message_types, limit=self.pool_size)

        if len(requests) == 0:
            return

        requests = [AlphaTransaction(x) for x in requests]

        LOG.info(f'Processing {len(requests)} requests ...')

        uuids   = []
        for request in requests:
            answer = ''
            try:
                uuid = request.uuid
                parameters = request.message
                uuids.append(uuid)
                LOG.debug('REQUEST: \n\n'+str(parameters)+'\n')

                if type(parameters) is not dict:
                    LOG.error('Answer is of the wrong type')
                    continue

                answer = self.function(request, *self.args, **self.kwargs)
                        
                if answer is not None:
                    answer            = str(answer)
                    LOG.debug('Sending answer: '+answer)
            except Exception as ex:
                LOG.error("Cannot send answser",ex=ex)
            finally:
                transactions_lib.send_answer(self.database, uuid, answer, 
                    message_type=str(request.message_type), answer_lifetime=self.answer_lifetime)

        transactions_lib.delete_requests(self.database, uuids)

    def cancel(self):
        self.finished.set()
        self.started.clear()
        self.running.clear()