import pytest

from cosapp.base import System
from cosapp.drivers import EulerExplicit
from cosapp.recorders import DataFrameRecorder


class ThresholdSystem(System):
    def setup(self):
        self.add_inward('x', 0.0)
        self.add_inward('threshold', 0.0)
        self.add_outward_modevar('below', True, init='x < threshold')
        self.add_event('cross', trigger='x == threshold')
    
    def transition(self):
        if self.cross.present:
            self.below = not self.below


def test_ModeVariableIntegration():
    s = ThresholdSystem('s')
    driver = s.add_driver(
        EulerExplicit(dt=0.1, time_interval=(0, 2))
    )
    driver.set_scenario(
        values = {
            'threshold': 0.6,
            'x': 'cos(4 * t)',
        },
    )
    driver.add_recorder(
        DataFrameRecorder(includes=['x', 'below', 'x - threshold']),
        period = 0.1
    )
    s.below = True  # inconsistent with `init` expression
    s.run_drivers()

    data = driver.recorder.export_data()
    data = data.drop(['Section', 'Status', 'Error code'], axis=1)
    # print('\n', data)
    assert not data['below'][0]  # consistent with `init` expression
    
    threshold = s.threshold

    for i, row in data.iterrows():
        x = row['x']
        below = row['below']
        delta = x - threshold
        context = f"row #{i}, x = {x}"
        if delta < -1e-12:
            assert below, context
        elif delta > 1e-12:
            assert not below, context
