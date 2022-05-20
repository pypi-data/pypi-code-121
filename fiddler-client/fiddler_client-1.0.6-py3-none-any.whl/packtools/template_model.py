import pandas as pd


class TemplateKerasTF2Model:
    def __init__(self, model_dir, model_artifact_path, att_layer_names_mapping, output_col,
                 embedding_names=None, batch_input_shape_list=None, hybrid=False):
        """
        Template for Keras TF2 models for package.py creation. Each method can be overwrite if needed.

        :param model_dir: model directory pathlib path
        :param model_artifact_path: str. model artifact file name (if .h5 file format) or
               directory (if saved model format)
        :param att_layer_names_mapping: dict that map attributable layer names to input feature names.
               Values have to be list of feature name(s).
               For example: {'cat_var': ['country', 'gender'], 'num_var': ['price']}.
        :param output_col: List. Name(s) the output(s) of the model. This will need to match the output(s)
               defined in model info.
        :param embedding_names: List. Name(s) the embedding layer(s) of the model.
        :param batch_input_shape_list: List of tuples corresponding to the output shape of the embedding layer(s)
               of the model. For example if the model has two embeddings, the list should have two tuples.
        :param hybrid: Boolean value for hybrid data type (for example matrices). Default to False.
        """
        import tensorflow as tf
        from .keras_ig_helpers import ComputeGradientsKerasTF2

        self.output_col = output_col
        self.embedding_names = embedding_names
        self.hybrid = hybrid

        self.model = tf.keras.models.load_model(str(model_dir / model_artifact_path))

        self.grads_instance = ComputeGradientsKerasTF2(self.model, model_dir, model_artifact_path,
                                                       att_layer_names_mapping, embedding_names,
                                                       hybrid=self.hybrid)
        if (embedding_names is None) or (embedding_names == []):
            self.grad_model = self.model
        else:
            self.grad_model = self.grads_instance.define_model_grads(batch_input_shape_list)

    def transform_to_attributable_input(self, input_df):
        """
        This method is called by the platform and is responsible for transforming the input dataframe
        to the upstream-most representation of model inputs that belongs to a continuous vector-space.
        For models with embedding layers (esp. NLP models) the first attributable layer is downstream of that.

        :param input_df: pandas DataFrame
        :return: dictionary with keys attributable layer names and values array of corresponding values.
                 If there are embeddings, the attributable_input values should be the output of the embedding layer.
        """
        if (self.embedding_names is not None) or self.hybrid:
            input_df = self._transform_input(input_df)
        return self.grads_instance.transform_to_attributable_input(input_df)

    def get_ig_baseline(self, input_df):
        """
        This method is used to generate the baseline against which to compare the input.
        It accepts a pandas DataFrame object containing rows of raw feature vectors that
        need to be explained (in case e.g. the baseline must be sized according to the explain point).
        Must return a pandas DataFrame that can be consumed by the predict method described earlier.

        :param input_df: pandas DataFrame
        :return: pandas DataFrame
        """
        raise NotImplementedError('Please implement generate_baseline in package.py')

    def _transform_input(self, input_df):
        """
        Helper function that accepts a pandas DataFrame object containing rows of raw feature vectors.
        The output of this method can be any Python object. This function can also
        be used to deserialize complex data types stored in dataset columns (e.g. arrays, or images
        stored in a field in UTF-8 format).

        :param input_df: pandas DataFrame
        :return: transformed input data
        """
        raise NotImplementedError('Please implement _transform_input in package.py')

    def predict(self, input_df):
        """
        Basic predict wrapper.

        :param input_df: a pandas DataFrame of input features
        :return: a pandas DataFrame of predictions.
        """
        transformed_input = self._transform_input(input_df)
        pred = self.model.predict(transformed_input)
        return pd.DataFrame(pred, columns=self.output_col)

    def compute_gradients(self, attributable_input):
        """
        This method computes gradients of the model output wrt to the differentiable input.
        If there are embeddings, the attributable_input should be the output of the embedding
        layer. In the backend, this method receives the output of the transform_to_attributable_input()
        method.

        :param attributable_input: dictionary with keys the attributable input layer names and values
               the differential input values associated.
        :return: a list of dictionaries, where each entry of the list is the attribution
                 for an output.
                 In case of single output model, this is a list with a single entry.
                 For the dictionary, the keys are the name of the input layers and the values are the attributions.
        """
        gradients_by_output = self.grads_instance.compute_gradients(attributable_input, self.grad_model)
        return gradients_by_output

    def project_attributions(self, input_df, attributions):
        """
        This method is used to map the attributions that were computed back to the input data.
        If you have a text input, you can use IGTextAttributionsTF2Keras.get_project_attribution().
        If you have tabular inputs, you can use IGTabularAttributions.get_project_attribution().
        If you have hybrid inputs, please contact Fiddler for help.

        :param input_df: pandas DataFrame of input features
        :param attributions: a list of dictionaries, where each entry of the list is the IG attribution for an output.
        :return: dictionary of final attributions for Fiddler to process. Keys are model outputs and values
                 are constructed from GEM (Generalized Explanation Markup) objects.
        """
        raise NotImplementedError('Please implement project_attributions in package.py. '
                                  'If you have a text input, you can use '
                                  'IGTextAttributionsTF2Keras.get_project_attribution(). '
                                  'If you have tabular inputs, you can use '
                                  'IGTabularAttributions.get_project_attribution(). '
                                  'If you have hybrid inputs, please contact Fiddler for help.')


class TemplateTreeShap:
    def __init__(self, model, output_cols, baseline_pred_dic, transformed_names_mapping=None):
        self.model = model
        self.output_cols = output_cols
        self.baseline_pred_dic = baseline_pred_dic
        self.transformed_names_mapping = transformed_names_mapping
        self.tree_shap_explanations = 'Tree Shap'

    def predict(self, input_df):
        """
        Basic predict wrapper.

        :param input_df: a pandas DataFrame of input features
        :return: a pandas DataFrame of predictions.
        """
        NotImplementedError('Please implement predict in package.py')

    def transform_input(self, input_df):
        """
        Basic wrapper to pre-process data.

        :param input_df: a pandas DataFrame of input features
        :return: a pandas DataFrame of predictions.
        """
        return input_df

    def explain_custom(self, explanation_name, input_df):
        """
        Wrapper to define the custom explanation method, in this example Tree SHAP.

        :param explanation_name: parameter used in Fiddler BE code to get explanation for a given explanation method.
               This allows users to define multiple custom explanations methods.
        :param input_df: a pandas DataFrame of input features
        :return: explanations_by_output and extras_by_output: two dictionaries with keys the output columns and values
                 the corresponding explanations and extra information necessary
        """
        from .project_attributions_helpers import TreeShapAttributions

        if explanation_name == self.tree_shap_explanations:
            predictions = self.predict(input_df).iloc[0].to_dict()
            transformed_df = self.transform_input(input_df)
            tree_shap_init = TreeShapAttributions(input_df, transformed_df, self.output_cols, self.model)
            if (self.transformed_names_mapping is not None) and (not isinstance(self.transformed_names_mapping, dict)):
                try:
                    self.transformed_names_mapping = self.transformed_names_mapping.get_mapping_feature_names(transformed_df.columns)
                except AttributeError:
                    raise ValueError('transformed_names_mapping is not a mapping dictionary')
            explanations_by_output, extras_by_output = tree_shap_init.get_project_attribution(predictions,
                                                                                              self.baseline_pred_dic,
                                                                                              self.transformed_names_mapping)
            return explanations_by_output, extras_by_output
        else:
            raise NotImplementedError(f'Please implement {explanation_name} in package.py with explain_custom method')
