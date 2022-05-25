from typing import List, Any
from dsframework.base.common.component import ZIDS_Component

##
# @file
# @brief Predictor class, this is where the model goes.

class generatedClass(ZIDS_Component):
    """! generatedClass class (Predictor) implements ZIDS_Component base class.

    The second step of the pipeline and its main goal is to feed a dataset to a model.

    All the action happens in this step, model sits in this class.
    """

    def __init__(self, artifacts=None) -> None:
        """generatedClass class (Postprocessor) initializer

        Args:
            artifacts: Shared artifacts instance.
        """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(artifacts)

    def execute(self, predictables: List[Any], **kwargs) -> List[Any]:
        """! generatedClass.execute (Predictor), Feed dataset to the model in this method, implement here.


        Args:
            predictables:List[Any]: List of predictable objects received from Preprocess.
            **kwargs: Dictionary with additional variables, if necessary.
        Returns:
            List[ZIDS_Predictable]: List of predictable objects.
        """

        ##
        # Implementation example:
        # @code{.py}
        #     def execute(self, predictables: List[Any], **kwargs) -> List[Any]:
        #         features = [list(vars(p.features).values()) for p in predictables]
        #
        #         results = self.artifacts.rf_model.predict_proba(features)
        #
        #         idx = 0
        #         for p in predictables:
        #             p.prob = results[idx][-1]
        #             idx += 1
        #         return predictables
        # @endcode

        ##
        # another example:
        # @code
        #     def execute(self, predictables: List[Any], **kwargs) -> List[Any]:
        #         df = pd.DataFrame([predictables.dict()])
        #         df = self.text_data_preparation(df)
        #         data = self.encode_batch(df['text'].tolist())
        #
        #         bert_output = self.artifacts.model(data)
        #
        #         probas = list(tf.nn.softmax(bert_output.logits).numpy())
        #         return probas
        # @endcode

        return predictables
