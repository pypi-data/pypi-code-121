import os, datetime, uuid, time, ast
from typing import List, Dict

from alphaz.models.database.main_definitions import Requests, Answers
from alphaz.models.database.structure import AlphaDatabase
from alphaz.models.main import AlphaTransaction

from core import core

LOG = core.get_logger('requests')

def delete_requests(db: AlphaDatabase, uuids: List[str]):
    db.delete(Requests,filters=[Requests.uuid.in_(uuids)])

def get_requests(db: AlphaDatabase, message_types:List[str]=[], limit=20, close=True) -> List[Requests]:
    filters = []
    if len(message_types) != 0:
        filters.append(Requests.message_type.in_(message_types))
    return db.select(Requests, filters=filters, limit=limit, order_by=Requests.creation_date.desc(),close=close)

def send_raw_request(db: AlphaDatabase, message_type:str, request: Dict[str,object], request_lifetime: int = 3600, uuid_:str = None, pid=None):
    uuid_request = str(uuid.uuid4()) if uuid_ == False else uuid_
    pid = os.getpid() if pid is None else pid
    db.add(Requests, values={
        Requests.uuid: uuid_request,
        Requests.message: str(request),
        Requests.process: pid,
        Requests.message_type: message_type.upper(),
        Requests.lifetime: request_lifetime
    })
    return uuid_request

def send_request(db: AlphaDatabase, transaction, close=True):
    db.add(Requests, values={
        Requests.uuid: transaction.uuid,
        Requests.message: str(transaction.message),
        Requests.process: transaction.process,
        Requests.message_type: transaction.message_type.upper(),
        Requests.lifetime: transaction.lifetime
    }, close=True)

def send_answer(db: AlphaDatabase, transaction):
    db.add(Answers, values={
        Answers.uuid: transaction.uuid,
        Answers.message: str(transaction.message),
        Answers.process: transaction.process,
        Answers.message_type: transaction.message_type.upper(),
        Answers.lifetime: transaction.lifetime
    })

    return transaction.uuid,

def get_answer(db: AlphaDatabase, answer):
    answer_uuid = answer if type(answer) == str else answer.uuid
    
    answer_db   = db.select(Answers, filters = [Answers.uuid==answer_uuid], first=True, close=True)
    answer      = AlphaTransaction()
    return answer.map(answer_db)

def send_raw_request_and_wait_answer(db: AlphaDatabase, request: Dict[str,object], message_type: str, timeout:int = None) -> Answers:
    request = AlphaTransaction(
        request, message_type=message_type
    )
    return send_request_and_wait_answer(db,request,timeout=timeout)

def send_request_and_wait_answer(db: AlphaDatabase, request: AlphaTransaction, timeout:int = None, wait_time:int = None) -> Answers:
    send_request(db,request, close=True)

    answer = None

    LOG.info(f'Try to get an answer for {request.uuid}')

    if timeout is None:
        timeout = core.config.get('transactions/timeout',default=10,type_=int)
    if wait_time is None:
        wait_time = core.config.get('transactions/wait_time',default=1,type_=int)

    waited_time = 0
    while waited_time < timeout and (answer is None or answer.message is None):
        answer = get_answer(db, request.uuid)
        if not answer or not answer.message:
            time.sleep(wait_time)
        waited_time += wait_time

    if (answer is None or answer.message is None) and waited_time >= timeout:
        answer.message  = 'timeout'
        answer.error    = True
        LOG.error(f'Timeout for request {request.uuid}')
    return answer.message

def process_requests(db: AlphaDatabase, fct, delete=True):
    requests = get_requests(db, limit=core.config.get("transactions/pool_size"),close=True)

    if len(requests) == 0:
        return

    requests = [AlphaTransaction(x) for x in requests]
    LOG.info('Processing %s requests ...'%len(requests))

    uuids   = []
    for request in requests:
        uuids.append(request.uuid)

        try:
            answer = fct(request)
        except Exception as ex:
            request.message = ""
            answer = request
            LOG.error("Cannot send answser",ex=ex)
        
        send_answer(db, answer)

    if delete:
        delete_requests(db, uuids)