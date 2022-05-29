from typing import List, Callable
from codefast.logger import Logger


class ResponsibilityChain(object):
    # Run a few processors in order until one of them succeeds.
    def __init__(self, processors: List[Callable] = []) -> None:
        self.processors = processors

    def add_processor(self, processor: Callable) -> None:
        self.processors.append(processor)
        return self

    def __call__(self, *args, **kwargs):
        for processor in self.processors:
            try:
                processor(*args, **kwargs)
                return self
            except Exception as e:
                Logger().error('Processor {} failed. {}'.format(processor, e))
        return self
