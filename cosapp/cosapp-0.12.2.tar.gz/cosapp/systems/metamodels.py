"""
System tuned to support meta-models.
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, Tuple, Type

import numpy
import pandas

from cosapp.ports.port import Port
from cosapp.ports.enum import Scope
from cosapp.systems.system import System
from cosapp.utils.surrogate_models import SurrogateModel, NearestNeighbor
# TODO allow keywords arguments to be passed to the surrogate constructor
from cosapp.utils.helpers import is_numerical, is_number


class MetaSystem(System):
    """Based :py:class:`~cosapp.systems.system.System` to insert meta-system inside CoSApp.

    Parameters
    ----------
    data : str or pandas.DataFrame
    mapping : Dict[str, str], optional
    default_model : Type[SurrogateModel], optional
        Default surrogate model; default NearestNeighbor with RBF interpolator
    name : str, optional
        Name of the `System`; default 'undefined'

    Attributes
    ----------
    models : dict[str, SurrogateModel]
        Dictionary of surrogate model for each output variables
    _trained : bool
        Are the surrogate models trained?
    _default_model : Type[SurrogateModel]
        Default surrogate model to use
    _input_names : list of str
        List of port variable names (`port`.`variable`)

    Examples
    --------

    As for classical :py:class:`~cosapp.systems.system.System`, this class needs to be subclassed to be meaning full.

    >>> class XPort(Port):
    >>>     def setup(self):
    >>>         self.add_variable('x')
    >>>
    >>> class OutPort(Port):
    >>>     def setup(self):
    >>>         self.add_variable('sin')
    >>>         self.add_variable('cos')
    >>>
    >>> class MetaA(MetaSystem):
    >>>     def setup(self):
    >>>         self.add_input(XPort, 'in_')
    >>>         self.add_output(OutPort, 'out', model=NearestNeighbor)

    """

    __slots__ = ('_default_model', '_input_names', '_trained', 'models')

    def __init__(self,
        name: str,
        data: Union[str, pandas.DataFrame],
        mapping: Optional[Dict[str, str]] = None,
        default_model: Type[SurrogateModel] = NearestNeighbor,
        **kwargs):
        """Class constructor"""
        self._trained = False
        self._default_model = default_model
        self.models = dict()
        self._input_names = None

        kwargs['data'] = data
        kwargs['mapping'] = mapping
        super().__init__(name, **kwargs)  # here _initialize will be called then user setup

        self._input_names = self._get_models_inputs()

    def _get_models_inputs(self) -> list:
        # TODO Fred this does not smell good, sequence only allow in System.INWARDS port...
        inputs = list()
        sequences = list()

        for port in self.inputs.values():
            if port.name == MetaSystem.INWARDS:
                ignored = ('training_data', )

                for varname in filter(lambda n: n not in ignored, port):
                    value = port[varname]
                    if not is_numerical(value):
                        continue
                    elif is_number(value):
                        inputs.append(f"{port.name}.{varname}")
                    else:
                        sequences.append(varname)
            else:
                inputs.extend([f"{port.name}.{varname}" for varname in port if is_number(port[varname])])

        self._locked = False
        # TODO Fred We should not change the System interface but work with group of model instead for sequences
        for s in sequences:
            for i, val in enumerate(self.inputs[MetaSystem.INWARDS][s]):
                name = f"{s}_index{i}"
                self.add_inward(name, val)
                inputs.append(f"{MetaSystem.INWARDS}.{name}")
            self.split_sequences_in_training_data(MetaSystem.INWARDS, s)
        self._locked = True

        return inputs

    def _initialize(self,
        data: Union[str, pandas.DataFrame] = None,
        mapping: Dict[str, str] = None,
        **kwargs) -> Dict[str, Any]:
        """Hook method to add `Module` member before calling `setup` method.

        Parameters
        ----------
        data : str or pandas.DataFrame
            The training data or a filepath containing them
        mapping : Dict[str, str]
            Name mapping between training data columns and port variables.
        kwargs : Dict[str, Any]
            Other keywords arguments to pass to `setup` method

        Returns
        -------
        Dict[str, Any]
            ``System.__init__`` optional keywords arguments not consumed by this method.
        """

        def read_data(data):
            data_path = Path(data)
            if not data_path.is_file():
                raise FileNotFoundError(f"File {data_path.name} does not exist.")

            def read_json(path: Path) -> pandas.DataFrame:
                with path.open() as file:
                    tmp_dict = json.load(file)
                if set(tmp_dict.keys()) == {'schema', 'data'}:
                    # File is in table format
                    data, schema = tmp_dict['data'], tmp_dict['schema']
                    return pandas.DataFrame(data).set_index(schema['primaryKey'])
                else:
                    return pandas.DataFrame(tmp_dict)

            readers = {
                '.csv': pandas.read_csv,
                '.xlsx': pandas.read_excel,
                '.json': read_json,
            }

            def read_unknown_sep(path: Path) -> pandas.DataFrame:
                return pandas.read_csv(path, sep=None, engine='python')

            data = readers.get(data_path.suffix, read_unknown_sep)(data_path)
            return data

        if isinstance(data, str):
            data = read_data(data)
        elif not isinstance(data, pandas.DataFrame):
            raise TypeError(
                f"data must be a str or a pandas.DataFrame: got {type(data).__name__}."
            )

        if mapping is not None:
            data = data.rename(columns=mapping)  # Rename columns

        self.add_inward('training_data', data, desc="Training data")
        return kwargs

    def _train(self) -> None:
        """Train the model using the provided training data."""

        for model_name, model in self.models.items():
            if model_name not in self.training_data.columns:
                raise AttributeError(
                    f"Name {model_name!r} not found in training data of MetaModel {self.name!r}"
                )
            model.train(
                self.training_data.loc[:, self._input_names].values,
                self.training_data.loc[:, model_name].values.reshape((-1, 1))
            )
        self._trained = True

    def add_output(self,
        port_class: "Type[Port]",
        name: str,
        variables: Optional[Dict[str, Any]] = None,
        model: Optional[Union[Type[SurrogateModel], Dict[str, SurrogateModel]]] = None,
    ) -> Port:
        """Add an output `Port` to the `System`.

        This function cannot be called outside `System.setup`.

        Parameters
        ----------
        port_class: type
            Class of the `Port` to create
        name : str
            `Port` name
        variables : Dict[str, Any], optional
            Dictionary of initial values (default: None)
        model : Type[Surrogate] or Dict[str, SurrogateModel], optional
            Surrogate default model type or mapping of surrogate model with output names; default
            `NearestNeighbor`.

        Returns
        -------
        Port
            The created port

        Examples
        --------

        >>> class MyPort(Port):
        >>>     def setup(self):
        >>>         self.add_variable('x')
        >>>         self.add_variable('y')
        >>>
        >>> class MySystem(System):
        >>>     def setup(self):
        >>>         self.add_output(MyPort, 'output_x')
        >>>         self.add_output(MyPort, 'output_y', model=NearestNeighbor)
        >>>         self.add_output(MyPort, 'output_z', model={'x': NearestNeighbor,
        >>>                                                    'y': FloatKrigingSurrogate})
        """
        if not (isinstance(model, (dict, type(None))) or issubclass(model, SurrogateModel)):
            raise TypeError(
                f"Model should be a subclass of SurrogateModel or a dictionary; got {type(model)}."
            )
        port = super().add_output(port_class, name, variables)

        if model is None:
            model = {'default': self._default_model}
        elif isinstance(model, type):
            if issubclass(model, SurrogateModel):
                model = {'default': model}

        for variable in port:
            model_name = f"{name}.{variable}"
            surrogate_model = model.get(variable, model['default']())
            self.models[model_name] = surrogate_model

        return port

    def add_outward(self,
        definition: Union[str, Dict[str, Any]],
        value: Any = 1,
        unit: str = '',
        dtype: Optional[type] = None,
        valid_range: Optional[Tuple[Any, Any]] = None,
        invalid_comment: str = '',
        limits: Optional[Tuple[Any, Any]] = None,
        out_of_limits_comment: str = '',
        desc: str = "",
        scope: Scope = Scope.PUBLIC,
        model: Optional[Union[Type[SurrogateModel], Dict[str, SurrogateModel]]] = None,
    ) -> None:

        if not (isinstance(model, (dict, type(None))) or issubclass(model, SurrogateModel)):
            raise TypeError(
                f"Model should be a subclass of SurrogateModel or a dictionary; got {type(model)}."
            )

        super().add_outward(
            definition,
            value=value,
            unit=unit,
            dtype=dtype,
            valid_range=valid_range,
            invalid_comment=invalid_comment,
            limits=limits,
            out_of_limits_comment=out_of_limits_comment,
            desc=desc,
            scope=scope,
        )

        if model is None:
            model = {'default': self._default_model}
        elif isinstance(model, type):
            if issubclass(model, SurrogateModel):
                model = {'default': model}

        def add_model(variable: str):
            model_name = f"{MetaSystem.OUTWARDS}.{variable}"
            surrogate_model = model.get(variable, model['default']())
            self.models[model_name] = surrogate_model

        if isinstance(definition, str):
            var_name = definition
            if is_numerical(self.outputs[MetaSystem.OUTWARDS][var_name]):
                if is_number(self.outputs[MetaSystem.OUTWARDS][var_name]):
                    add_model(var_name)
                elif is_numerical(self.outputs[MetaSystem.OUTWARDS][var_name]):
                    for i, varname in enumerate(self.outputs[MetaSystem.OUTWARDS][var_name]):
                        self.add_outward(
                            f"{var_name}_index{i}",
                            value=varname,
                            desc=desc,
                            scope=scope,
                        )
                    self.split_sequences_in_training_data(MetaSystem.OUTWARDS, var_name)
        elif isinstance(definition, dict):
            for varname in definition:
                if is_number(self.outputs[MetaSystem.OUTWARDS][varname]):
                    add_model(varname)

    def split_sequences_in_training_data(self, port_name, var_name):
        name = f"{port_name}.{var_name}"
        training_data = self.inputs[MetaSystem.INWARDS]['training_data']
        if name in training_data.columns:
            temp = pandas.DataFrame(
                training_data[name].tolist(),
                index = training_data.index,
                columns = [f"{name}_index{i}" for i, _ in enumerate(self[name])]
            )
            self.inputs[MetaSystem.INWARDS]['training_data'] = pandas.concat([training_data, temp], axis=1)
        else:
            raise AttributeError(f"Name {name!r} not found in training data of MetaModel {self.name!r}")

    def compute(self) -> None:
        """Contains the customized `System` calculation."""
        if not self._trained:
            self._train()

        self.split_in_sequences()
        # build input vector
        input_vector = numpy.array([self[name] for name in self._input_names])

        for model_name, model in self.models.items():
            self[model_name] = float(model.predict(input_vector))

        self.rebuild_out_sequences()

    def split_in_sequences(self):
        for variable in self.inputs[MetaSystem.INWARDS]:
            var_name = f"{MetaSystem.INWARDS}.{variable}"
            if is_numerical(self[var_name]) and not is_number(self[var_name]):
                for i, val in enumerate(self[var_name]):
                    self[f"{var_name}_index{i}"] = val

    def rebuild_out_sequences(self):
        for name, port in self.outputs.items():
            for variable in port:
                var_name = f"{name}.{variable}"
                if is_numerical(self[var_name]) and not is_number(self[var_name]):
                    for i in range(len(self[var_name])):
                        self[var_name][i] = self[f"{var_name}_index{i}"]

    def update(self):
        self._trained = False  # Force model training
