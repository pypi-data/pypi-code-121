
from dsframework.base.tester.evaluator_logic import ZIDS_Evaluator


class generatedClass(ZIDS_Evaluator):
    def __init__(self):
        """generatedClass initializer."""

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__()

    def get_confusion_matrix(self, true_label, prediction):
        """
        Model evaluation function, to be implemented per project in evaluator.py file
        """
        raise NotImplementedError
