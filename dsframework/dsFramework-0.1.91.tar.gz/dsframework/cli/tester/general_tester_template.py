import sys
from typing import List

import pandas as pd
import os
import json
from random import randint

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs

from tester.test_schema.test_input import TestInputRequest, TestInputRow
from tester.test_schema.test_output import TestOutputResponse
from dsframework.base.tester.tester_logic import ZIDS_Tester
from dsframework.base.common.functions import flatten, split_dataframe, get_date_time
from tester.evaluator import generatedProjectNameEvaluator


##
# @file
# @brief generatedClass implementation of ZIDS_Tester base class.

class generatedClass(ZIDS_Tester):
    """Main purpose of this class is to support the 'local testing' feature in dsp, it allows to run the model
    on a selected dataset from dsp. It implements ZIDS_Tester.
    """
    def __init__(self):
        ZIDS_Tester.__init__(self)
        ## Not used
        self.ready = False
        ## Instance of the pipeline
        self.pipeline = generatedProjectNamePipeline()
        ## Instance of the Evaluator class
        self.evaluator = generatedProjectNameEvaluator()
        ## Fill this according to the field received from the model, and remove this comment
        self.pred_name = ""
        ## Fill this according to the field received from DSP, and remove this comment
        self.target_name = ""

    def test_batch(self, test_request: TestInputRequest) -> TestOutputResponse:
        """! This is the main function of the tester (Local testing feature in dsp), most of the functions
        are implemented in the base class (ZIDS_Tester), but wherever needed, a NotImplementedError will be raised.
        Feel free to mingle with the other functions as well. This is a humble suggestion.


        Args:
            test_request: A request for testing a batch, as received from the DSP (Data Science Portal)

        Returns:
            model_evaluation_results: A request formatted to fit to the DSP needs
        """

        # parse request rows as TestRow
        data_rows: List[TestInputRow] = test_request.rows

        if data_rows:
            # Convert the input to a dataframe input
            df_data_rows = self.convert_input_to_dataframe(data_rows)

            # Run the model on the data rows - implement create_model_request
            df_model_predictions = self.run_model_on_data_rows(df_data_rows)

            # Evaluate the results based on ground truth and predictions
            model_evaluation_results = self.evaluator.evaluate_model_predictions(df_model_predictions)

            # Format the evaluated output by changing the naming convention to fit with DSP
            model_evaluation_results = self.format_evaluation_output(model_evaluation_results)

        else:
            output = []
        # format response rows
        self.format_response_row_for_dsp_upload(model_evaluation_results, test_request)

        return model_evaluation_results

    def create_model_request(self, batch_input_rows) -> generatedProjectNameInputs:
        """! Structure the data as a proper request, and create a dictionary in order to enable serialization.

        Args:
            batch_input_rows: A batch of input information, intended to be structured into a model request
        Returns:
            model_request: The data, structured in a format that the model can work with
        """

        ##
        # This is an example code from the scoops project, please fit with your specific project fields:
        # @code{.py}
        # request_scoops = [ScoopCandidate(html_content=rec['text'],
        #                   source=rec['source'],
        #                   queue_name=rec['queue_name'],
        #                   title=rec['title']) for rec in batch_input_rows]
        # model_request = ScoopsClassificationRequest(pages=request_scoops)
        # @endcode

        raise NotImplementedError
        model_request = generatedProjectNameInputs()
        return model_request

    @staticmethod
    def create_mock_response(input_request: TestInputRequest) -> List[TestOutputResponse]:
        """! This function creates a mock output for the DSP to display.
        When starting a new project, this function can be used to test connection with the DSP.
        It of course has to be modified in order to reflect the correct API fields


        Args:
            input_request: Request as received from the DSP
        Returns:
            List[TestOutputResponse]: A list of responses, to be sent back to the DSP
        """
        input_request = input_request.dict()
        # print('DSP Request: ', input_request)

        response = []
        rows = input_request['rows']
        truth_dataset_id = input_request['truth_dataset_id']
        model_type_id = input_request['model_type_id']
        for row in rows:
            data = json.loads(row['data'])
            id = row['id']
            raw_id = row['raw_id'] or -1
            segments = data['segments'] if 'segments' in data else data
            pred = data['segments'] if 'segments' in data else data
            text = ''
            # Please feel free to adjust the mock response. This response fits the sigparser project
            if 'signature' in data:
                 text = data['signature']
            elif 'email' in data:
                 text = data['email']
            elif 'text' in data:
                text = data['text']
            elif 'name' in data:
                text = data['name']

            # Generate different confusion matrix values per row
            cm_list = [0, 0, 0, 0]
            cm_index = randint(0, 3)
            cm_list[cm_index] = 1

            response.append(
                TestOutputResponse(
                    **{
                        'truth_id': id,
                        'truth_dataset_id': truth_dataset_id,
                        'model_type_id': model_type_id,
                        'raw_id': raw_id,
                        'pred': json.dumps(pred),
                        'target': json.dumps(segments),
                        'text': text,
                        'name_first_fn': cm_list[0],
                        'name_first_fp': cm_list[1],
                        'name_first_pred': "Marty",
                        'name_first_prob': -1,
                        'name_first_target': "Marty",
                        'name_first_tn': cm_list[2],
                        'name_first_tp': cm_list[3],
                    }
                )
            )
        # call tester here

        return response

    def test_from_file(self, csv_file_path, batch_size):
        """! Run an evaluation from a csv file input.

        Args:
            csv_file_path: csv file containing both ground truth and raw input for the model.
            batch_size: Size of batch to use in order to feed the model with controllable chunks of data
        """
        ## Define prediction column name
        predictions_col_name = self.pred_name
        ## Define ground truth column name
        ground_truth_col_name = self.target_name

        # Define csv output
        time_str = get_date_time(False, True)
        csv_output_name = "model_eval_results_" + time_str + ".csv"
        csv_output_path = os.path.join(os.getcwd(), csv_output_name)
        first_chunk = True

        # Load CSV. predictions and ground truth columns are converted from string to list/dict
        df = pd.read_csv(csv_file_path,
                         converters={predictions_col_name: json.loads,
                                     ground_truth_col_name: json.loads})

        # Chunk according to batch size
        batches = split_dataframe(df, int(batch_size))

        # iterate over batches and send the data for evaluation
        for batch in batches:

            # Reset index of batch in order to align evaluation
            batch.reset_index(inplace=True)

            # Feed the model chunk by chunk
            output_rows = self.run_model_on_data_rows(batch)

            # Evaluate the results based on ground truth and predictions
            df_model_evaluation_results = self.evaluator.evaluate_model_predictions(output_rows)

            # Flatten confusion matrix and sort the dataframe
            conf_mat_dict = df_model_evaluation_results['confusion_matrix'].to_dict()
            confusion_matrix_flattened = flatten(conf_mat_dict)
            conf_pd = pd.DataFrame(confusion_matrix_flattened, index=[0])
            df_model_evaluation_results = df_model_evaluation_results.join(conf_pd)
            df_model_evaluation_results = df_model_evaluation_results.drop('confusion_matrix', 1)

            # Write output to csv, append the chunks
            if first_chunk:
                df_model_evaluation_results.to_csv(csv_output_path, mode='a')
                first_chunk = False
            else:
                df_model_evaluation_results.to_csv(csv_output_path, mode='a', header=False)


# This will call the tester with a given csv file
if __name__ == '__main__':

    tester = generatedClass()
    args = sys.argv[1:]
    tester.test_from_file(args[0], args[1])
    print("Done evaluating, please find the results at: model_eval_results.csv")
