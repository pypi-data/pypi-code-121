from odoo.addons.base_rest.http import HttpRestRequest
import json
from odoo.http import Root
import odoo
from odoo.addons.base_rest.core import _rest_services_databases
import logging


_logger = logging.getLogger(__name__)

try:
    import pyquerystring
except (ImportError, IOError) as err:
    _logger.debug(err)


class HttpRestRequest(HttpRestRequest):
    """Http request that always return json, usefull for rest api"""

    def __init__(self, httprequest):
        super(HttpRestRequest, self).__init__(httprequest)
        if self.httprequest.mimetype != "application/json":
            data = self.httprequest.data.decode(self.httprequest.charset)
            data_dec = pyquerystring.parse(data)
            if 'body' in data_dec:
                self.params = json.loads(data_dec['body'])


ori_get_request = Root.get_request


def get_request(self, httprequest):
    db = httprequest.session.db
    if db:
        # on the very first request processed by a worker,
        # registry is not loaded yet
        # so we enforce its loading here to make sure that
        # _rest_services_databases is not empty
        odoo.registry(db)
        service_registry = _rest_services_databases.get(db)
        if service_registry:
            for root_path in service_registry:
                if httprequest.path.startswith(root_path):
                    return HttpRestRequest(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request
