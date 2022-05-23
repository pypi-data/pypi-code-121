ADSL_SERVICES = ['ADSL', 'ADSL+100min', 'ADSL+1000min']
FIBRE_SERVICES = ['Fibra']
MOBILE_SERVICES = ['Mobil']
NO_COVERAGE_VALUES = ['NoServei', 'NoFibra', 'fibraIndirecta', 'NoFibraVdf']


class Service():

    def __init__(self, otrs_response):
        self.response = otrs_response
        self._technology = self._field('TecDelServei')

    def _field(self, field_name):
        return self.response.dynamic_field_get(field_name).value

    def _is_adsl(self):
        return self._technology in ADSL_SERVICES

    def _is_fibre(self):
        return self._technology in FIBRE_SERVICES

    def _has_adsl_coverage(self):
        return self._is_adsl() and (
            not self._field('coberturaADSL') or self._field('coberturaADSL') not in NO_COVERAGE_VALUES)

    def _has_fibre_coverage(self):
        return self._is_fibre() and (
            self._fibre_MM_coverage() or self._fibre_Vdf_coverage() or self._fibre_Orange_coverage()
        )

    def _fibre_MM_coverage(self):
        return not self._field('coberturaFibraMM') or self._field('coberturaFibraMM') not in NO_COVERAGE_VALUES

    def _fibre_Vdf_coverage(self):
        return not self._field('coberturaFibraVdf') or self._field('coberturaFibraVdf') not in NO_COVERAGE_VALUES

    def _fibre_Orange_coverage(self):
        return not self._field('coberturaFibraOrange') or self._field('coberturaFibraOrange') not in NO_COVERAGE_VALUES

    def has_coverage(self):
        return self.is_mobile() or self._has_adsl_coverage() or self._has_fibre_coverage()

    def is_mobile(self):
        return self._technology in MOBILE_SERVICES
