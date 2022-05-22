import os
import sys
import time
from typing import Optional, Union, Dict, List, Any
from quickstats import semistaticmethod
from quickstats.components import AbstractObject
from quickstats.concurrent.logging import standard_log
from quickstats.utils.common_utils import execute_multi_tasks, is_valid_file

class AbstractRunner(AbstractObject):
    
    @property
    def config(self):
        return self._config
    
    def __init__(self, parallel:int=-1, timed:bool=True,
                 save_log:bool=True, cache:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)

        self._config = {
            'cache': cache,
            'parallel': parallel,
            'save_log': save_log,            
            'timed': timed
        }

    def _prerun_batch(self):
        pass

    @semistaticmethod
    def _prerun_instance(self, **kwargs):
        pass
    
    @semistaticmethod
    def _run_instance(self, **kwargs):
        raise NotImplementedError
    
    @semistaticmethod
    def _cached_return(self, outname:str):
        raise NotImplementedError
        
    def run_instance(self, kwargs:Dict[str, Any]):
        self._prerun_instance(**kwargs)
        
        outname = kwargs.get("outname", None)
        
        if outname and (self.config['cache'] and os.path.exists(outname) and is_valid_file(outname)):
            self.stdout.info(f"INFO: Cached output from {outname}")
            return self._cached_return(outname)
        
        log_path = kwargs.get("log_path", None)
        if (outname and self.config['save_log']) and (not log_path):
            log_path = os.path.splitext(outname)[0] + ".log"
        
        if self.config['save_log']:
            with standard_log(log_path) as logger:
                return self._run_instance(**kwargs)
        else:
            return self._run_instance(**kwargs)
        
    def run_batch(self, argument_list, auxiliary_args:Optional[Dict]=None):
        parallel = self.config['parallel']
        t0 = time.time()
        self._prerun_batch()
        raw_result = execute_multi_tasks(self.run_instance, argument_list, parallel=parallel)
        results = self.postprocess(raw_result, auxiliary_args)
        t1 = time.time()
        dt = t1 - t0        
        if self.config['timed']:
            self.stdout.info('INFO: All jobs have finished. Total time taken: {:.3f} s'.format(dt))
        return results
    
    def postprocess(self, raw_result, auxiliary_args:Optional[Dict]=None):
        return raw_result