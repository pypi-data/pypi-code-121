import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model


class ComputeGradientsKerasTF2:
    def __init__(self, model, model_dir, model_artifact_path, att_layer_names_mapping, embedding_names, hybrid=False):
        """
        Helper class to compute gradients for Keras TF2 models

        :param model: keras model
        :param model_dir: model directory pathlib path
        :param model_artifact_path: str. model artifact file name (if .h5 file format) or
               directory (if saved model format)
        :param att_layer_names_mapping: dict that map attributable layer names to input feature names.
               Values have to be list of feature name(s).
               For example: {'cat_var': ['country', 'gender'], 'num_var': ['price']}.
        :param embedding_names: List. Name(s) the embedding layer(s) of the model.
        :param hybrid: Boolean value for hybrid data type (for example matrices). Default to False.
        """
        self.model = model
        self.model_dir = model_dir
        self.model_artifact_path = model_artifact_path
        self.embedding_names = embedding_names

        if (att_layer_names_mapping is None) or (att_layer_names_mapping == {}):
            raise ValueError("att_layer_names_mapping argument cannot be empty."
                             " Please give the dictionary mapping of attributable layer names.")
        if not isinstance(att_layer_names_mapping, dict):
            raise ValueError("att_layer_names_mapping as to be a dictionary mapping between the attributable "
                             "layer names and the corresponding features names. "
                             "Values have to be list of feature name(s). "
                             "For example: {'cat_var': ['country', 'gender'], 'num_var': ['price']}")
        self.att_layer_names_mapping = att_layer_names_mapping
        if embedding_names is None:
            self.att_sub_models = None
        else:
            self.att_sub_models = self.get_attributable_sub_models()

        self.hybrid = hybrid

    def get_attributable_sub_models(self):
        """
        Construct sub-models for each attributable layer name. This method is used if there are embedding
        layers in the model because it's not possible to attribute directly to the input.

        :return: dictionary with keys the attributable layer names and values the sub models
        """
        return {att_layer: Model(self.model.inputs, outputs=self.model.get_layer(att_layer).output)
                for att_layer in self.att_layer_names_mapping.keys()}

    def transform_to_attributable_input(self, input_data):
        """
        This method is responsible for transforming the input dataframe to the upstream-most representation
        of model inputs that belongs to a continuous vector-space.
        For models with embedding layers (esp. NLP models) the first attributable layer is downstream of that.

        :param input_data: input data (pandas DataFrame when no embedding, otherwise outputs of the _transform_input)
        :return: dictionary with keys the attributable input layer names and values
               the differential input values associated.
        """
        if self.att_sub_models is None:
            if self.hybrid:
                return {att_layer_name: input_data[att_layer_name]
                        for att_layer_name, col in self.att_layer_names_mapping.items()}
            else:
                return {att_layer_name: input_data[col].values
                        for att_layer_name, col in self.att_layer_names_mapping.items()}
        else:
            return {att_layer: att_sub_model.predict(input_data) for att_layer, att_sub_model
                    in self.att_sub_models.items()}

    def define_model_grads(self, batch_input_shape_list):
        """
        Define a differentiable model, cut from the Embedding Layers.
        This will take as input what the transform_to_attributable_input function defined.

        :param batch_input_shape_list: List of tuples corresponding to the output shape of the embedding layer(s)
               of the model. For example if the model has two embeddings, the list should have two tuples.
        :return: Differentiable keras model
        """
        if batch_input_shape_list is None:
            raise ValueError("Please specify the batch_input_shape_list. It corresponds to the output shape"
                             " of the embedding layer(s).")
        if not isinstance(batch_input_shape_list, list):
            batch_input_shape_list = [batch_input_shape_list]

        model = tf.keras.models.load_model(
            str(self.model_dir / self.model_artifact_path)
        )

        for index, name in enumerate(self.embedding_names):
            model.layers.remove(model.get_layer(name))
            model.layers[index]._batch_input_shape = batch_input_shape_list[index]
            model.layers[index]._dtype = 'float32'
            model.layers[index]._name = name

        new_model = tf.keras.models.model_from_json(model.to_json())

        for layer in new_model.layers:
            try:
                layer.set_weights(self.model.get_layer(name=layer.name).get_weights())
            except:
                pass

        return new_model

    @staticmethod
    def gradients_input(x, grad_model):
        """
        Method to compute gradients.

        :param x: attributable input tensor
        :param grad_model: Differentiable keras model. If the model has embedding layer, please use define_model_grads
               to get the grad model. Otherwise, grad_model is simply the original model.
        :return: dictionary of gradients
        """
        with tf.GradientTape() as tape:
            tape.watch(x)
            preds = grad_model(x)

        grads = tape.gradient(preds, x)

        return grads

    def compute_gradients(self, attributable_input, grad_model):
        """
        This method computes gradients of the model output wrt to the differentiable input.
        In the backend, this method receives the output of the transform_to_attributable_input()
        method.

        :param attributable_input: dictionary with keys attributable layer names and values array of
               corresponding values. If there are embeddings, the attributable_input values should be the
               output of the embedding layer.
        :param grad_model: Differentiable keras model. If the model has embedding layer, please use define_model_grads
               to get the grad model. Otherwise, grad_model is simply the original model.
        :return: a list of dictionaries, where each entry of the list is the attribution
                 for an output.
                 In case of single output model, this is a list with a single entry.
                 For the dictionary, the keys are the name of the input layers and the values are the attributions.
        """
        gradients_by_output = []
        attributable_input_tensor = {
            k: tf.identity(v) for k, v in attributable_input.items()
        }
        gradients_dic_tf = self.gradients_input(attributable_input_tensor, grad_model)
        gradients_dic_numpy = dict(
            [key, np.asarray(value)] for key, value in gradients_dic_tf.items()
        )
        gradients_by_output.append(gradients_dic_numpy)
        return gradients_by_output
