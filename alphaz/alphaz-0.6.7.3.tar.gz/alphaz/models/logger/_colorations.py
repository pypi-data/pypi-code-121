import re

import colorama
from colorama import Fore, Back, Style
colorama.init()

def colored_term(text,front=None,back=None,bold=False):
    if front is not None and hasattr(Fore,front.upper()):
        text = getattr(Fore,front.upper()) + text
    if back is not None and hasattr(Back,back.upper()):
        text = getattr(Back,back.upper()) + text
    if bold:
        text = Style.BRIGHT

    if front is not None or back is not None or bold:
        text += Style.RESET_ALL
    return text

class ColorFilter:
    def __init__(self,configuration):
        self.configuration = configuration

    def filter(self, record):
        from ...libs import io_lib

        patterned = []

        msg = record.msg

        for pattern, pattern_config in self.configuration.items():
            #pattern = pattern.replace('\\\\','\\').replace(r"\\+",r"\+")
            results = re.findall(pattern, msg)
            for result in results:
                if not result in patterned:
                    msg = msg.replace(result,colored_term(result,
                        front=pattern_config.get('color',None),
                        back=pattern_config.get('background',None),
                        bold=pattern_config.get('bold',None)
                    ))
                    patterned.append(result)

        record.msg = msg
        return record