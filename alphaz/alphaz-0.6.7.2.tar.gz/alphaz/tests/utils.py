from alphaz.models.tests import AlphaTest, test
from alphaz.libs import config_lib

from core import core

LOG = core.get_logger("tests")

class Dashboard(AlphaTest):
    @test()
    def dashboard(self):
        filename = "dashboard.cfg"
        directory = core.config.get("directories/tmp")
        dashboard = core.api.conf.get('dashboard')

        try:
            config_lib.write_config_file(filename, dashboard, directory,upper_keys=True)
            return True
        except Exception as ex:
            LOG.error(ex) 
            return False