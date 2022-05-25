class ForecastingAlgorithm:

    def __init__(self, tsc, j_algorithm):
        self._tsc = tsc
        self._j_algorithm = j_algorithm

    def reset_model(self):
        self._j_algorithm.resetModel()

    def forecast_ahead(self, steps_ahead, exogenous_variables=None):
        if exogenous_variables is None:
            return self._j_algorithm.forecastAhead(steps_ahead)
        else:
            java_array_ex = self._tsc.packages.time_series.forecasting.algorithms.arimax.PythonConnector \
                .createArrayFromList(self._tsc.java_bridge.convert_to_java_list(exogenous_variables))
            return self._j_algorithm.forecastAhead(steps_ahead, java_array_ex)

    def is_initialized(self):
        return self._j_algorithm.isInitialized()

    def update_model(self, y, exogenous_variables=None):
        java_array_y = self._tsc.packages.time_series.forecasting.algorithms.arimax.PythonConnector \
            .createArrayFromList(self._tsc.java_bridge.convert_to_java_list(y))

        if exogenous_variables is None:
            self._j_algorithm.updateModel(java_array_y)
        else:
            java_list_ex = []
            for i in range(len(exogenous_variables)):
                java_list_ex.append(self._tsc.java_bridge.convert_to_java_list(exogenous_variables[i]))

            java_list_ex_all = self._tsc.java_bridge.convert_to_java_list(java_list_ex)

            java_array_ex = self._tsc.packages.time_series.forecasting.algorithms.arimax.PythonConnector\
                .create2dArrayFromList(java_list_ex_all)

            self._j_algorithm.updateModel(java_array_y, java_array_ex)

    def __getstate__(self):
        j_algorithm_str = self._tsc.packages.time_series.forecasting.algorithms.arimax.PythonConnector.serializeAlgorithm(self._j_algorithm)
        return {'j_algorithm': str(j_algorithm_str)}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        tsc = get_or_create()
        self._tsc = tsc
        self._j_algorithm = self._tsc.packages.time_series.forecasting.algorithms.arimax.PythonConnector.deserializeAlgorithm(d['j_algorithm'])
