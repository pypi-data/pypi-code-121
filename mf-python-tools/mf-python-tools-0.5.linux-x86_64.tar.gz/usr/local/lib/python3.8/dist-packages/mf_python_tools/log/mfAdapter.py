import logging
from .loggers import clientLogger

from inspect import getframeinfo,stack
def fileNo():
    # logging.info(stack())
    caller = getframeinfo(stack()[1][0])
    return caller.filename+' '+ str(caller.lineno) +': '+ caller.function

class mfAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra=None, source=None, host=None, source_random=None) -> None:
        """扩展logger类
            logger          logger示例
                            import logging
                            from mf_python_tools import log_init,JSONLOGFormatter,mfAdapter
                            log_init()
                            logger = mfAdapter(logging.getLogger(__name__))
                            logger.info('this is example',event='init')
            source          日志来源
            host            日志主机字段
            source_random   是否随机source_id，True or False
        """
        super(mfAdapter, self).__init__(logger, extra or {})
        self.source= source
        self.source_random= source_random
        self.host = host
        self.client = clientLogger(source, host, source_random)
        self.logger = logger



    def debug(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """debug
        """
        self._print('debug',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)


    def info(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """info"""
        self._print('info',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def warning(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """warning"""
        self._print('warning',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def warn(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """warn"""
        self._print('warn',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def error(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """error"""
        self._print('error',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def exception(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, exc_info=True, **kwargs):
        """exception"""
        self._print('exception',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def critical(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        """critical"""
        self._print('critical',msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)

    def _print(self,fun,msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        if file_no is None:
            file_no=fileNo()
        md = self.client.data( msg, *args, event=event, source=source, source_id=source_id, source_random=source_random, host=host,file_no=file_no, data=data,**kwargs)
        if hasattr(self.logger,fun):
            getattr(self.logger, fun, '')(md[0], *md[1], **md[2])

