##
# @file
# @brief Base class for cloud_eval_client.py
# All of those methods are implemented based on the specific project.
class CloudEvalClientBase:
    """Base class for cloud_eval_client.py, all of those methods needs to be implemented based on
    a specific project. Examples of implementation included in each method.
    """
    UNIMPLEMENTED_ERROR_MESSAGE = "Please override the parent base class methods for using cloud eval"

    def get_request_headers(self, row: dict):
        """! Construct the model service request headers.

            Args:
                row: (dict) - dataset csv record is provided in case it is needed.
            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """

        ##
        # Example:
        # ```
        # return {
        #     "accept": "application/json",
        #     "Content-Type": "application/json",
        #     "x-token": "fake-super-secret-token"
        # }
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)

    def get_request_payload(self, row: dict):
        """! Construct a model service payload from a dataset csv record

            Args:
                row: (dict) - Dataset csv record
            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """
        ##
        # Example:
        # ```
        # data = json.loads(record['data'])
        #
        # service_input = PyScoopsClassificationInputs(html_content=data['text'],
        #                                              source=data['source'],
        #                                              queue_name=data['queue_name'],
        #                                              title=data['title']
        #                                              )
        # model_request = service_input  # [input]
        # payload = model_request.dict()
        # return payload
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)

    def extract_model_predictions_from_response(self, predictions):
        """! Extract the predictions from the service response.

            Args:
                predictions: Prediction result.
            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """
        ##
        # Example:
        # ```
        # if type(predictions) == list:
        #     if len(predictions) > 1:
        #         raise Exception("We do not currently support mini batches")
        #     prediction = predictions[0]
        #     try:
        #         prediction_obj = PyScoopsClassificationOutputs(**prediction)
        #         return prediction_obj.dict()
        #     except:
        #         # default answer
        #         return {}
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)

    def get_endpoint_name(self):
        """! Return model's endpoint name.

            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """
        ##
        # For example, if you invoke the model with `/predict` then you can do:
        # ```
        # return "predict"
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)

    def evaluate_model_results(self, row: dict):
        """! Evaluate results received from the model by comparing them to desired outputs

            Args:
                row: (dict) - Compare prediction results with evaluation.
            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """
        ##
        # Example: (From scoops)
        # ```
        # # Load evaluator
        # service_evaluator = PyScoopsClassificationEvaluator()
        #
        # # Extract specific row prediction
        # row_prediction_dict = json.loads(row['prediction'])
        # row_prediction = int(row_prediction_dict['pred'])
        #
        # # Extract target from row information
        # data_dict = json.loads(row['data'])
        # target = int(data_dict['pred'])
        #
        # # Perform evaluation
        # conf_matrix_dict = service_evaluator.get_confusion_matrix(target, row_prediction)
        #
        # return conf_matrix_dict
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)

    def set_format_output(self, row: dict):
        """! Fit specific information received from the model / evaluation to the desired output format

            Args:
                row: (dict) - Row record, includes prediction and evaluation result
            Raises:
                NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
        """
        ##
        # Example (From scoops):
        # ```
        # # Format the dictionary according to the DSP format
        #
        # # Extract data from original dataset row
        # data_dict = json.loads(row['data'])
        #
        # # DSP expects to get the exactly same data that it sent, just with the 'pred' field different
        # basic_dict = {'html_content': data_dict['text'],
        #               'source': data_dict['source'],
        #               'queue_name': data_dict['queue_name'],
        #               'title': data_dict['title'],
        #               'internal_notes': data_dict['internal_notes']}
        #
        # pred_dict = {'pred': int(json.loads(row['prediction'])['pred'])}
        # target_dict = {'pred': int(data_dict['pred'])}
        # pred_dict_to_dsp = dict(basic_dict, **pred_dict)
        # target_dict_to_dsp = dict(basic_dict, **target_dict)
        #
        # row['target'] = json.dumps(target_dict_to_dsp)
        # row['pred'] = json.dumps(pred_dict_to_dsp)
        # row['prob'] = json.loads(row['prediction'])['prob']
        #
        # confusion_matrix_flattened = flatten(row['evaluation'])
        # row.update(confusion_matrix_flattened)
        #
        # # Remove unnecessary fields
        # remove_key = row.pop('evaluation', None)
        # remove_key = row.pop('prediction', None)
        # remove_key = row.pop('data', None)
        # ```

        raise NotImplementedError(CloudEvalClientBase.UNIMPLEMENTED_ERROR_MESSAGE)
