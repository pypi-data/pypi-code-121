# Default Python Libraries
from typing import Dict, List

# AristaFlow REST Libraries
from af_runtime_service import DataContext, ParameterValue, SimpleSessionContext


class ActivityContext(object):
    _ssc: SimpleSessionContext
    _input_parameters: Dict[str, ParameterValue]
    _output_parameters: Dict[str, ParameterValue]
    _token: str

    def __init__(self):
        self._input_parameters = {}
        self._output_parameters = {}

    @property
    def ssc(self):
        return self._ssc

    @ssc.setter
    def ssc(self, ssc: SimpleSessionContext):
        self._ssc = ssc
        self._map_parameters()

    @property
    def session_id(self) -> str:
        # session_id field does not exist in "IncompleteSSC" used by get_ssc
        return self._ssc.session_id if hasattr(self._ssc, 'session_id') else None

    def _map_parameters(self):
        """
        Builds the internal parameter value maps
        """
        dc: DataContext = self._ssc.data_context
        if dc.values is not None:
            for pv in dc.values:
                self._input_parameters[pv.name] = pv
        if dc.output_values is not None:
            for pv in dc.output_values:
                self._output_parameters[pv.name] = pv

    @property
    def input_parameters(self) -> List[ParameterValue]:
        """
        Returns the input parameter values for the data context, never returns None
        """
        return self._ssc.data_context.values or []

    @property
    def output_parameters(self) -> List[ParameterValue]:
        """
        Returns the output parameter values for the data context, never returns None
        """
        return self._ssc.data_context.output_values or []

    def get_input(self) -> Dict:
        """
        Returns all input parameters as dictionary
        """
        values = {}
        pv: ParameterValue
        for pv in self._ssc.data_context.values:
            values[pv.name] = pv.value
        return values

    def set_output(self, values: Dict):
        """
        Set the output parameters to the given values
        """
        for k in self.output_parameters:
            if k.name in values:
                self._output_parameters[k.name].value = values[k.name]

    @property
    def token(self) -> str:
        """ Returns the security token used to start / resume the activity """
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token
