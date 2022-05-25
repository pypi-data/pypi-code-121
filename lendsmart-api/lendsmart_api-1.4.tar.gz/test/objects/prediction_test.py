from datetime import datetime
from test.base import ClientBaseCase

from lendsmart_api.objects import PredictionWorkflow
from lendsmart_api.objects.base import MappedObject

class PredictionWorkflow(ClientBaseCase):
    """
    Tests methods of the PredictionWorkflow class
    """
    def test_get_prediction_workflow(self):
        """
        Tests that a prediction workflow is loaded correctly by ID
        """
        sub = PredictionWorkflow(self.client)
        self.assertEqual(sub.label, 'Longview Pro 40 pack')
