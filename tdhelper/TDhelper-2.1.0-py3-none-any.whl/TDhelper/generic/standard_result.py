#! python 3.6

#########################################################
#| @File    :   standard_result.py
#| @ClsName :   standard_result
#| @Version :   1.0.0
#| @History :
#|----------------------------------------------------------------------------------------------------------|
#| version       | Type                | Author        | Contact                     | Time                 |
#|----------------------------------------------------------------------------------------------------------|
#| 1.0.0         | Create              | Tony.Don      | yeihizhi@163.com            | 2022-01-27 20:34:44  |
#|----------------------------------------------------------------------------------------------------------|
#| @License :   BSD-3-Clause, Copyright (c) <2021>, <Tang Jing>
#| @Desc    :   None.
#########################################################

# import lib by pypi
# import lib by project

#code start


class standard_result(object):
    state = False
    code = 0
    msg = ""
    data = None
    _hook_log_ = []
    _log_handle_ = None

    @classmethod
    def set_log_handle(self, handle):
        '''
        set logging handle
        
        args:
            handle: logging handle.
        '''
        self._log_handle_ = handle

    @classmethod
    def set_log_hook(self, hooks={}):
        '''
        hook state auto write log.
        
        args:
            hooks: {state_code:code}
        '''
        self._hook_log_ = hooks

    @classmethod
    def append_log_hook(self, state, code=None, log_type="info"):
        '''
        append an log hook config.
        
        args:
            state: Boolen.
            code: user define state code.
            log_type: str, emun(info,error,warning,debug)
        '''
        self._hook_log_[state+"_"+code if code else ""]= {"code":code,"log_type":log_type.lower()}

    @classmethod
    def log_fiter(self):
        '''
        auto write log.
        '''
        if self.state+"_"+self.code if self.code else "" in self._hook_log_:
            if self._log_handle_:
                method= getattr(self._log_handle_, self._hook_log_[self.state+"_"+self.code if self.code else ""]['log_type'].lower())
                if method:
                    log_formatter=""
                    method(log_formatter)
                else:
                    raise Exception("Log handle method '%s' can not found."% self._hook_log_[self.state+"_"+self.code if self.code else ""]['log_type'].lower())
            else:
                raise Exception('Log handle is none.')
    
    @classmethod
    def dumps(self, state, code, msg, data):
        '''
        dumps result.

        args:
            state: <Boolen>
            code: <int>, user define state code
            msg: <str>, message
            data: <object>, return data.
        '''
        self.state = (state,)
        self.code = (code,)
        self.msg = (msg,)
        self.data = (data,)
        return self.state, {
            "code": self.code,
            "msg": self.msg,
            "data": self.data,
        }

    @classmethod
    def loads(self, state, result):
        '''
        make result transformation to object.

        args:
            state:<Boolen>
            result:<dict>
        '''
        assert "code" in result, "result must have 'code' key."
        assert "msg" in result, "result must have 'msg' key."
        assert "data" in result, "result must have 'data' key."
        self.state = state
        self.code = result["code"]
        self.code = result["msg"]
        self.data = result["data"]
        return self


class web_result(standard_result):
    state = False
    code = 200
    msg = "success"
    data = {}
