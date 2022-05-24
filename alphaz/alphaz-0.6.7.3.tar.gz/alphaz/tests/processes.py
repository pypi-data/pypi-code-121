import time

from alphaz.models.tests import AlphaTest, test
from alphaz.models import process
from core import core

LOG = core.get_logger('tests')

@process()
def test_process():
    while True:
        time.sleep(10)
        pass

class AlphaProcesses(AlphaTest):

    def __init__(self):
        super().__init__()

    @test(save=False)
    def connexion(self):
        return self.connected
