from typing import Dict, Union, List, Optional

import ROOT

from quickstats import semistaticmethod

class RooMsgService:

    @staticmethod
    def remove_topics(input_arguments:bool=True, numeric_integration:bool=True, object_handling:bool=True):
        if input_arguments:
            ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.InputArguments)
        if numeric_integration:
            ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.NumIntegration)
        if object_handling:
            ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.ObjectHandling)