import pandas as pd
import json
from typing import Dict, List
from dsframework.base.common.functions import flatten

##
# @file
# @brief ZIDS_Tester base class for general_tester.py

class ZIDS_Tester:
    """ZIDS_Tester class base class for general_tester.py, contains methods to format data to Inputs, Outputs and dsp,
        requirements.
    """
    def __init__(self):
        """! ZIDS_Tester initializer.

        Initializes local variables.
        """
        self.truth_dataset_id = -1
        self.model_type_id = -1
        self.data_keys = []
        ## Prediction field name
        self.pred_name = ""
        ## Ground truth fields name - implemented in derived class.
        self.target_name = ""

    def save_meta_data(self, input_req):
        """! Save input request metadata, truth_dataset_id and model_type_id.

        Args:
            input_req: An object of type TestInputRequest
        """

        ## Truth dataset ID
        self.truth_dataset_id = input_req.truth_dataset_id
        ## Model type ID
        self.model_type_id = input_req.model_type_id

    def test_batch(self, test_request):
        """Implemented in derived class generatedClassGeneralTester in file general_tester.py"""
        raise NotImplementedError

    def convert_input_to_dataframe(self, data_rows):
        """! Convert from a list of TestInputRow to a dataframe.
        - Used in general_tester.py test_batch()
        - Also apply Model-Specific conversion.


        Args:
            data_rows: A list of objects, List[TestInputRow]
        Returns:
            Pandas dataframe that contains all the relevant information
        """
        df = pd.DataFrame.from_records((data_row.dict() for data_row in data_rows))
        df = df.apply(self.adapt_to_dsp_format, axis=1)
        return df

    def create_model_request(self, batch_input_rows):
        """Implemented in derived class generatedClassGeneralTester in file general_tester.py"""
        raise NotImplementedError

    def run_model_on_data_rows(self, row_dataframe: pd.DataFrame) -> pd.DataFrame:
        """! Runs model on all data rows. Create a format, the model can work with and runs the pipeline.

        Args:
            row_dataframe: Input dataframe, containing all data rows.
        Returns:
            Extended dataframe which contains the output of the model
        """
        batch_of_pages = row_dataframe.to_dict(orient='records')

        model_request = self.create_model_request(batch_of_pages)

        # Call the model to get predictions
        predicted_records = self.pipeline.execute(model_request)

        if predicted_records:
            df_predicted = self.create_predicted_records_dataframe(predicted_records)
            row_dataframe = row_dataframe.join(df_predicted)
        else:
            # we did not get any records, create empty records
            self.create_empty_predictions(row_dataframe)

        return row_dataframe

    def adapt_to_dsp_format(self, df_row):
        """! Adapt for DSP format compatibility
        'data' is provided as string since the DSP saves it this way.
        Please feel free to modify due to your project needs.


        Args:
            df_row: A single row from the processed data frame
        Returns:
            df_row: The flattened data frame, with all the fields previously compressed in the 'data' field
        """

        ##  Extract keys for later use
        self.data_keys = json.loads(df_row['data']).keys()

        # Restructure as a data frame line
        for k, v in json.loads(df_row['data']).items():
            df_row[k] = v
        return df_row

    def create_predicted_records_dataframe(self, predicted_records):
        """! Create a dataframe formatted as input for evaluation

        Args:
            predicted_records: Results from pipeline
        Returns:
            df_predicted: DataFrame
        """

        df_predicted = pd.DataFrame(predicted_records)
        df_predicted = df_predicted.rename(columns={self.pred_name: 'pred_model'})
        return df_predicted

    @staticmethod
    def create_empty_predictions(row_dataframe):
        """! Create empty predictions in case the model returns an error, and we wish to keep evaluating.
        Not implemented yet.


        Args:
            row_dataframe: Input dataframe, containing all data rows.
        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def format_evaluation_output(self, row_dataframe) -> List[Dict]:
        """! Format the results with the expected DSP data format.

        Args:
            row_dataframe: Results from evaluation
        Returns:
            List[Dict]: In dsp format
        """

        row_dataframe = row_dataframe.rename(columns={'pred': 'target', 'pred_model': 'pred'})

        output = row_dataframe.to_dict(orient='records')
        for rec in output:
            pred_dict = {}
            target_dict = {}
            for row_key in self.data_keys:
                pred_dict[row_key] = rec[row_key]
                target_dict[row_key] = rec[row_key]
            pred_dict['pred'] = rec['pred']
            target_dict['pred'] = rec['target']

            for row_key in self.data_keys:
                del rec[row_key]

            rec['target'] = json.dumps(target_dict)
            rec['pred'] = json.dumps(pred_dict)

        return output

    @staticmethod
    def format_response_row_for_dsp_upload(output, test_request):
        """! Format response rows (including results) to follow DSP requirements.

        Args:
            output: model_evaluation_results
            test_request: Include ids required for response - truth_dataset_id, model_type_id -
        Returns:
            Doesn't return, make changes by reference to input argument 'output'.
        """
        row_extra_data = {
            "truth_dataset_id": test_request.truth_dataset_id,
            "model_type_id": test_request.model_type_id
        }
        for row in output:
            row.update(row_extra_data)
            row['truth_id'] = row.get('id', -1)

            if 'id' in row:
                del row['id']

            confusion_matrix_flattened = flatten(row['confusion_matrix'])
            row.update(confusion_matrix_flattened)

            del row['confusion_matrix']

            if 'id' in row:
                del row['data']

    @staticmethod
    def get_f1_precision_recall(var_name, df):
        """! Calculate from detailed output report the f1, precision and recall scores per attribute.

        This function should be overridden if other form of calculation is needed

        Args:
            var_name: variable name to calculate the scores for.
            df: detailed results dataframe with per attribute confusion matrix as outputted by tester.
        Returns:
            f1, precision and recall scores.

        """
        tp = df[var_name + '_tp']
        fp = df[var_name + '_fp']
        tn = df[var_name + '_tn']
        fn = df[var_name + '_fn']
        recall = 0
        precision = 0
        f1 = 0
        if len(np.where(tp + fp + tn + fn != 1)[0]) > 0:
            print(f'{len(np.where(tp + fp + tn + fn != 1)[0])} examples have errors')
        if (tp.sum() + fn.sum()) != 0:
            recall = tp.sum() / (tp.sum() + fn.sum())
        if (tp.sum() + fp.sum()) != 0:
            precision = tp.sum() / (tp.sum() + fp.sum())
        if (precision + recall) != 0:
            f1 = 2 * ((precision * recall) / (precision + recall))
        return f1, precision, recall