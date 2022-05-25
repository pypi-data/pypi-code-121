
class clientLogger(object):

    def __init__(self, source=None, host=None, source_random=None, file_no=None) -> None:
        """扩展logger类
            @source          日志来源
            @host            日志主机字段
            @source_random   是否随机source_id，True or False

            example         logger示例
                            import loggging
                            from mf_python_tools import log_init,clientLogger
                            log_init()
                            clog = clientLogger()
                            logger = logging.getLogger(__name__)
                            md = clog.data('app init.','fffffff',event="app.init",aa="bbb",source="aaa",data=['ddd','cccc'],extra={"abc":"dddddffff","data":{"cccc":"sss","mf":['aaa','bbb']}})

                            logger.info(md[0],*md[1],**md[2])

        """
        self.source= source
        self.source_random= source_random
        self.host = host
        self.file_no = file_no

    def _extra_info(self,kwargs, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None):
        extra_info = {}
        if file_no is not None:
            extra_info['file_no'] = file_no
        else:
            if self.file_no is not None:
                extra_info['file_no'] = self.file_no
        if event is not None:
            extra_info['event'] = event
        if source_id is not None:
            extra_info['source_id'] = source_id
        if data is not None:
            extra_info['data'] = data
        if source is not None:
            extra_info['source'] = source
        else:
            if self.source is not None:
                extra_info['source'] = self.source
        if source_random is not None:
            extra_info['source_random'] = source_random
        else:
            if self.source_random is not None:
                extra_info['source_random'] = self.source_random
        if host is not None:
            extra_info['host'] = host
        else:
            if self.host is not None:
                extra_info['host'] = self.host
        if len(extra_info)>0:
            if 'extra' in kwargs:
                kwargs['extra'].update(extra_info)
            else:
                 kwargs['extra'] = extra_info
        return kwargs

    def _kwargs_extra(self, kwargs):
        re_kwargs = None
        keep_key = ['extra','exc_info','stack_info','stacklevel']
        if len(kwargs) >0:
            re_kwargs = {}
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
                re_kwargs['extra'] = {}
            else:
                re_kwargs['extra'] =  kwargs['extra']
                for key,value in kwargs.items():
                    if key not in  keep_key:
                        re_kwargs['extra'].update({key:value})
                    else:
                        if key != 'extra':
                            re_kwargs['extra'].update({key:value})

        else:
            re_kwargs = kwargs
        return re_kwargs

    def handle(self, kwargs, event, source, source_id, source_random, host, file_no, data):
        kwargs = self._kwargs_extra(kwargs)
        kwargs = self._extra_info(kwargs, event, source, source_id, source_random, host,file_no, data)
        return kwargs

    def data(self, msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, **kwargs):
        kwargs = self.handle(kwargs, event, source, source_id, source_random, host, file_no,data)
        return (msg, args, kwargs)

    def exception(self,msg, *args, event=None, source=None, source_id=None, source_random=None, host=None,file_no=None, data=None, exc_info=True, **kwargs):
        kwargs = self.handle(kwargs, event, source, source_id, source_random, host, file_no, data)
        return (msg, args, exc_info, kwargs)
