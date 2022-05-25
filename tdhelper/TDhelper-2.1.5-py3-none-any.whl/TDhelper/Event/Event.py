from enum import Enum
import functools
import threading
import TDhelper.bin.globalvar

class Event:
    '''
        Initialization event class,and set this class state flag,if has EventList Variable state is True,else state is False
    '''
    def __init__(self):
        self._state=True
        self._currentEvent= None
        if TDhelper.bin.globalvar.getGlobalVariable("EventList")==None: #Check eventList object is define
            self._state=False

    def _keyconvert(self,key):
        if isinstance(key,str):
            return (str(self.__hash__())+key).lower()
        elif isinstance(key,Enum):
            return (str(self.__hash__())+key.value).lower()
        else:
            return None
    '''
        Check event key haven't set
        Return:
        if event key haven't set return True,else it return False
    '''
    def _checkKeyNotInEventList(self,key):
        return self._keyconvert(key) not in TDhelper.bin.globalvar.getGlobalVariable("EventList")

    def _getEventListObject(self,key):
        return TDhelper.bin.globalvar.getGlobalVariable("EventList")[self._keyconvert(key)]

    def getEventList(self):
        return TDhelper.bin.globalvar.getGlobalVariable("EventList")

    '''
        Register an event
        Parameter
            key:
                event index key
            func:
                if sys has happend an event,then callback func
            sync:
                default value is True so callback by synchronous,if you set value is False then call back by asynchronous
    '''
    def registerEvent(self,key,func,sync=True):
        if self._state:
            if self._checkKeyNotInEventList(self._keyconvert(key)):
                TDhelper.bin.globalvar.getGlobalVariable("EventList")[self._keyconvert(key)]={"func":func,"sync":sync}


    '''
        Delete an event in the Event List;if you delete then this event has happend we don't callback
    '''
    def delEvent(self,key):
        if self._state:
            if not self._checkKeyNotInEventList(self._keyconvert(key)):
                del TDhelper.bin.globalvar.getGlobalVariable("EventList")[self._keyconvert(key)]

    '''
        Callback
    '''
    def on(self,key,*args,**kw):
        try:
            if key:
                if self._state:
                    if self._keyconvert(key) in TDhelper.bin.globalvar.getGlobalVariable("EventList"):
                        self._currentEvent= key
                        if self._getEventListObject(key)["sync"]:
                            return self._getEventListObject(key)["func"](*args,**kw)
                        else:
                            #todo asynchronous call back
                            pass#threading.Thread(target=self._getEventListObject(key)["func"],args=[*args,**kw,]).start()
        except Exception as e:
            raise e
    def EVENT(self):
        return self._currentEvent

def keyconvert(key):
    if isinstance(key,str):
        return key.lower()
    elif isinstance(key,Enum):
        return key.value.lower()

def call(key,*args,**kw):
    try:
        key=keyconvert(key)
        if len(args)>0:
            if key in TDhelper.bin.globalvar.getGlobalVariable("EventList"):
                if TDhelper.bin.globalvar.getGlobalVariable("EventList")[key]["sync"]:
                    return TDhelper.bin.globalvar.getGlobalVariable("EventList")[key]["func"](*args,**kw)
                else:
                    pass#threading.Thread(target=bin.globalvar.getGlobalVariable("EventList")[key]["func"],args=[*args,**kw,]).start()
    except Exception as e:
        raise e

def trigger(EventType):
        def decorator(func):
            @functools.wraps(func)
            def expand(*args,**kw):
                #to add event start event
                args[0].on("begin"+str(EventType),*args,**kw)
                #to add event start event
                result=func(*args,**kw)
                #to add event complate event
                args[0].on("on"+str(EventType)+"complete",*args,**kw)
                #to add event complate event
                return result
            return expand
        return decorator    