from pymbse.pymbse.config.pymbse_config import load_pymbse_config
from pymbse.pymbse.model_api.model_api import ModelAPI
from pymbse.pymbse.model_api.model_api_factory import model_type_to_api


class PyMBSE:
    """ A class providing a model query mechanism. The models are embedded into Jupyter notebooks and expose the
    following endpoints:
    - get_html_report()
    - get_ipynb_report()
    - get_figures_of_merit()
    For notebook models
    - get_artefacts()
    - get_artefact(artefact_name)

    For the query mechanism to work, a notebook should provide an input and output functionality.
    - Input:
      - a notebook cell with input parameters is marked with a tag "parameters"
      - the input parameter cell contains only variable assignments, e.g., a = 3. Thus, the input parameter cell should
      not contain comments, iPython magic, import statements, etc.

    - Output
      - a notebook cell with outputs does not require any tag
      - the outputs are returned with a statement `sb.glue('model_results', data=fom_dct, encoder='json')`, where
      fom_dct is a dictionary composed of two keys: `fom` and `artefacts`:
        - the value of the `fom` key  contains a figure of merit key-value dictionary
        - the value of the `artefacts` key contains an artefact key-value dictionary with keys being artefact file
        names and values corresponding to relative file paths w.r.t. the root model directory

    """

    def __init__(self, config_path: str, source_model: str, target_model: str, input_parameters: dict) -> None:
        """

        :param config_path: a path to the model dependency config
        :param source_model: a source model from which a PyMBSE query is made (used to check whether the target model is
        in its the dependency). If the source_model is an empty string, then the target_model is called as a standalone
        model. In this case, there is no check of the dependency.
        :param target_model: name of a model to be executed.
        :param input_parameters: a dictionary with input parameters for the target_model
        """
        self.configuration = load_pymbse_config(config_path)
        self.source_model = source_model
        self.target_model = target_model

        is_source_model_in_models = self.source_model not in self.configuration.models
        if self.source_model != '' and is_source_model_in_models:
            raise KeyError('Source model %s not present in model configuration!' % self.source_model)

        if self.source_model != '' and self.target_model not in self.configuration.models[self.source_model].needs:
            raise KeyError('Target model %s not present in source model dependencies!' % self.target_model)

        self.input_parameters = input_parameters

    def build(self) -> ModelAPI:
        """Method building a ModelAPI instance based on model configuration. It passes pieces of information needed for
        model execution, namely:
        - target model config
        - target model snapshot hash (for caching)
        - input parameters

        :return: a ModelAPI implementation matching the model type
        """
        target_model_config = self.configuration.models[self.target_model]
        ip_with_port = self.configuration.database.get_ip_with_port()
        root_model_metadata_hash = self.configuration.hash_root_model_metadata(root_model=self.target_model,
                                                                               input_parameters=self.input_parameters)
        model_api_class = model_type_to_api[target_model_config.model_type]
        return model_api_class(root_model_config=target_model_config,
                               ip_with_port=ip_with_port,
                               root_model_metadata_hash=root_model_metadata_hash,
                               input_parameters=self.input_parameters)
