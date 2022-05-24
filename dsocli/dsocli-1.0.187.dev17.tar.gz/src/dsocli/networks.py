from .logger import Logger
from .constants import *
from .exceptions import *
from .network_utils import *

class NetworkService():
    def layout_subnet_plan(self, subnet_plan, filters=None, summary=True):
        Logger.info(f"Laying out subnet plan '{subnet_plan['name']}'...")
        return layout_subnet_plan(subnet_plan, filters, summary)


Networks = NetworkService()