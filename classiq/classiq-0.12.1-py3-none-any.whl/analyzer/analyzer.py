"""Analyzer module, implementing facilities for analyzing circuits using Classiq platform."""
import webbrowser
from urllib.parse import urljoin

from classiq.interface.analyzer import analysis_params, result as analysis_result
from classiq.interface.generator import result as generator_result
from classiq.interface.server import routes

from classiq._internals import client
from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import Asyncify
from classiq._internals.type_validation import validate_type
from classiq.exceptions import ClassiqAnalyzerError


class Analyzer(metaclass=Asyncify):
    """Analyzer is the wrapper object for all analysis capabilities."""

    def __init__(self, circuit: generator_result.GeneratedCircuit):
        """Init self.

        Args:
            circuit (): The circuit to be analyzed.
        """
        if circuit.qasm is None:
            raise ValueError("Analysis requires a circuit with valid QASM code")

        self._params = analysis_params.AnalysisParams(qasm=circuit.qasm)
        self.input = circuit

    async def analyze_async(self) -> analysis_result.Analysis:
        """Runs the circuit analysis.

        Returns:
            The analysis result.
        """
        result = await ApiWrapper.call_analysis_task(params=self._params)

        if result.status != analysis_result.AnalysisStatus.SUCCESS:
            raise ClassiqAnalyzerError(f"Analysis failed: {result.details}")
        details = validate_type(
            obj=result.details,
            expected_type=analysis_result.Analysis,
            operation="Analysis",
            exception_type=ClassiqAnalyzerError,
        )

        dashboard_path = routes.ANALYZER_DASHBOARD
        self._open_route(path=dashboard_path)
        return details

    async def analyzer_app_async(self) -> None:
        """Opens the analyzer app with synthesis interactive results.

        Returns:
            None.
        """
        analyzer_input = self.input.analyzer_data
        result = await ApiWrapper.call_analyzer_app(analyzer_data=analyzer_input)
        webbrowser.open_new_tab(urljoin(routes.ANALYZER_FE_APP, str(result.id)))

    @staticmethod
    def _open_route(path: str) -> None:
        backend_uri = client.client().get_backend_uri()
        webbrowser.open_new_tab(f"{backend_uri}{path}")
