import functools, traceback


CRAWLING_STARTED = 'CRAWINGL_STARTED'
CRAWLING_COMPLETED = 'CRAWLING_COMPLETED'
CRAWLING_STOPPED = 'CRAWLING_STOPPED'
VISITING_URL = 'VISITING_URL'
EXCEPTION_OCCURED = 'EXCEPTION_OCCURED'



def catch_crawl_exception(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            r = func(self, *args, **kwargs)
        except Exception as e:
            module_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
            self.crawl_listener(
                module_name, EXCEPTION_OCCURED, 
                {'exception': e, 'traceback': traceback.format_exc()}
            )
            raise
        return r
    return wrapper

