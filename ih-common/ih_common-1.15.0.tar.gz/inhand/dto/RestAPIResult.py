class BasicResult:
    def __init__(self,error=None,error_code=None,result=None):
        self.error=error
        self.error_code=error_code
        self.result=result

class PageResult:
    def __init__(self,error=None,error_code=None,total=0,pageNumber=1,pageSize=None,result=None,stats=None):
        self.error=error
        self.error_code=error_code
        self.result=result
        self.total=total
        self.pageNumber=pageNumber
        self.pageSize=pageSize
        self.stats=stats