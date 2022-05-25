# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
APIs for federated learning.
"""
from shrike.pipeline.pipeline_helper import AMLPipelineHelper
from shrike.pipeline.module_helper import module_reference
from shrike._core import experimental
from coolname import generate_slug
from dataclasses import dataclass
from typing import List, Optional, Union
from azure.ml.component import dsl
from azure.ml.component.pipeline import Pipeline
from azure.ml.component.component import Component, Output
import logging
from omegaconf import OmegaConf, open_dict, DictConfig
from pathlib import Path
from typing import Callable, Dict
import collections.abc

log = logging.getLogger(__name__)

EXPERIMENTAL_WARNING_MSG = (
    "Federated APIs are experimental and could change at any time."
)


def dataset_name_to_reference(
    component_instance: Component, dataset_names: list
) -> Dict[str, Output]:
    res = {}
    if not dataset_names:
        return res
    for dataset in dataset_names:
        res[dataset] = component_instance.outputs[dataset]
    return res


@dataclass
class StepOutput:
    """Output object from preprocess/midprocess/postprocess/training step in a federated pipeline."""

    step: Union[Component, Pipeline] = None
    outputs: List[str] = None


class FederatedPipelineBase(AMLPipelineHelper):
    """
    Base class for Federated Learning pipelines.
    """

    def __init__(self, config, module_loader=None):
        super().__init__(config, module_loader=module_loader)

        package_path = Path(__file__).parent / "components"
        fedavg_component = DictConfig(
            module_reference(
                key="fl_fedavg_pytorch",
                name="fl_fedavg_pytorch",
                yaml=str(package_path) + "/fedavg/spec.yaml",
            )
        )
        self.config.modules.manifest.append(fedavg_component)
        self.module_loader.modules_manifest = OmegaConf.merge(
            self.module_loader.modules_manifest, {"fl_fedavg_pytorch": fedavg_component}
        )
        self.cur_fl_iteration: Optional[int] = None
        self.output_prefix = "fl_output_"

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_base_name(self) -> str:
        """The training outputs from each silo will be stored at <base_name>/<silo_name> on the central storage.
        By default, it will return a name of 2 word. User can override this method.

        Returns:
            base_name
        """
        rv = "fl-"
        rv += generate_slug(2)
        return rv

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_iteration_name(self) -> str:
        """Display name for each iteration's subgraph, containing letters, numbers, and underscores only. The default value is "iteration n"."""
        return f"iteration_{self.cur_fl_iteration}"

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_silo_specific_name(self, silo_name) -> str:
        """Display name for a silo's training in iteration n's subgraph, containing letters, numbers, and underscores only. The default value is "silo_<silo_name>__iteration_n"."""
        return f"silo_{silo_name}__iteration_{self.cur_fl_iteration}"

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_subgraph_name(self) -> str:
        """Display name for each subgraph"""
        return "Federated Learning Subgraph"

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def preprocess(self, config: DictConfig, **input) -> StepOutput:
        """
        Optional user-defined preprocess step. The outputs will be distributed to each silo's datastore.

        Returns:
            a component/subgraph instance, and a list of output dataset names to be passed to the downstream pipeline.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def midprocess(self, config: DictConfig, **input) -> StepOutput:
        """
        User-defined midprocess step which reads outputs from `train` in each silo. The outputs will be distributed to each silo's datastore.
        By default, it calls the built-in FedAvg component (un-signed).

        Returns:
            a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline.
        """
        fedavg_component = self.component_load("fl_fedavg_pytorch")
        num_models = len(self.config.federated_config.silos)
        if len(input) != num_models:
            log.error(
                "The input model weights are inconsistent with the number of models."
            )
            raise Exception
        if "agg_weights" in self.config.federated_config.params:
            weights = self.config.federated_config.params.agg_weights
        else:
            weights = ",".join([str(1 / num_models)] * num_models)
        model_name = (
            self.config.federated_config.params.model_name
            if "model_name" in self.config.federated_config.params
            else None
        )
        updated_input = {}
        for k, v in input.items():
            idx = k[k.index("silo") + 4 : k.index("_")]
            updated_input["model_input_dir_" + idx] = v
        fedavg_step = fedavg_component(
            **updated_input,
            num_models=num_models,
            weights=weights,
            model_name=model_name,
        )
        return StepOutput(fedavg_step, ["model_output_dir"])

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def postprocess(self, config: DictConfig, **kwargs) -> StepOutput:
        """
        Optional user-defined postprocess step which reads outputs from the final `midprocess` step and writes to the `noncompliant_datastore`.

        Returns:
            a component/subgraph instance, and a list of output dataset names.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def train(
        self, config: DictConfig, silo: DictConfig, input: Output = None, **kwargs
    ) -> StepOutput:
        """
        User-defined train step happening at each silo. This reads outputs from `preprocess` or `midprocess`, and sends outputs back to the `noncompliant_datastore`.

        Returns:
            a component/subgraph instance, and a list of output dataset names to be passed to the downstream pipeline.
        """
        pass

    def _data_transfer(
        self, input_list: dict, destination_datastore: str, base_name: str
    ) -> dict:
        """Moves data `input_list` to `destination_datastore` with path prefixed by `base_name`."""
        # assume one shared ADF
        dts_name = self.config.federated_config.data_transfer_component
        try:
            data_transfer_component = self.component_load(
                dts_name  # this component is subject to change
            )
            log.info(f"Using {dts_name} as data transfer component.")
        except Exception as e:
            log.error(
                f"Please specify the data transfer component name registered in your workspace in module manifest and `federated_config.data_transfer_component` pipeline yaml."
            )
            raise (e)

        res = {}
        if not input_list:
            return res
        for name, input in input_list.items():
            data_transfer_step = data_transfer_component(source_data=input)
            self.apply_smart_runsettings(data_transfer_step, datatransfer=True)
            data_transfer_step.outputs.destination_data.configure(
                datastore=destination_datastore,
                path_on_datastore=base_name + "/" + name,
            )
            res[name] = data_transfer_step.outputs.destination_data
        return res

    def _process_at_orchestrator(self, prev: StepOutput) -> dict:
        """Processes outputs at the orchestrator."""
        step = prev.step
        if isinstance(step, Pipeline):
            prev_output = step.outputs
        elif isinstance(step, Component):
            prev_output = dataset_name_to_reference(step, prev.outputs)
        else:
            raise Exception(
                f"The output of preprocess/midprocess/postprocess step must be a Pipeline object or a Component object. You are using {type(prev.step)}."
            )
        return prev_output

    def _merge_config(self):
        """Merges and simplifies federated_config."""
        # override priority: default_config < customized shared config < per-silo setting
        # everything in customized shared config have equal priority
        federated_config = self.config.federated_config
        default_config = federated_config.config_group.get("default_config", {})
        for silo_name, silo_config in federated_config.silos.items():
            customized_config = {}
            if "inherit" in silo_config:
                for inherit_config in silo_config["inherit"]:
                    customized_config = OmegaConf.merge(
                        customized_config, federated_config.config_group[inherit_config]
                    )
            log.info(
                f"=== Original config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )
            with open_dict(default_config):
                merge = OmegaConf.merge(default_config, customized_config)
            log.info(f"=== Shared config {merge}")
            with open_dict(self.config.federated_config.silos[silo_name]):
                self.config.federated_config.silos[silo_name] = OmegaConf.merge(
                    merge, silo_config
                )
                self.config.federated_config.silos[silo_name].pop("inherit", None)
            log.info(
                f"=== Merged config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )

    def _check_if_data_transfer_is_activated_and_process(
        self, datastore_name, base_name, **inputs
    ):
        deactivate_data_transfer = self.config.federated_config.deactivate_data_transfer
        if deactivate_data_transfer:
            log.info("Data transfer is disabled; training outputs will remain in silo.")
            return inputs
        else:
            log.info(f"Moving data {inputs.keys()} into {datastore_name}.")
            return self._data_transfer(
                input_list=inputs,
                destination_datastore=datastore_name,
                base_name=base_name,
            )

    def _train_in_silo_once(
        self, silo_name: str, silo: DictConfig, cool_name: str, **prev_output
    ) -> dict:
        """Runs the "training" step once at one silo."""
        prev_output = self._check_if_data_transfer_is_activated_and_process(
            silo.datastore, cool_name, **prev_output
        )
        if len(prev_output) == 1:
            prev_output = {"input": list(prev_output.values())[0]}
        train_step = self.train(self.config, silo=silo, **prev_output)

        step = train_step.step
        if isinstance(step, Pipeline):
            train_output = step.outputs
            for node in step._expand_pipeline_nodes():
                node._node_name = self.create_silo_specific_name(silo_name)
        elif isinstance(step, Component):
            train_output = dataset_name_to_reference(step, train_step.outputs)
            step._node_name = self.create_silo_specific_name(silo_name)

        else:
            raise Exception(
                f"The output of train step must be a Pipeline object or a Component object. You are using {type(step)}"
            )

        silo_output = self._check_if_data_transfer_is_activated_and_process(
            self.config.compute.noncompliant_datastore,
            cool_name + "/" + silo_name,
            **train_output,
        )
        return silo_output

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def build(self, config: DictConfig):
        """Constructs the federated pipeline. User does not need to modify."""

        @dsl.pipeline(display_name=self.create_subgraph_name())
        def _subpipeline_function(**kwargs):
            cool_name = self.create_base_name()
            midprocess_input = {}
            i = 1
            for silo_name, silo in self.config.federated_config.silos.items():
                train_output = self._train_in_silo_once(
                    silo_name,
                    silo,
                    cool_name,
                    **kwargs,
                )
                if len(train_output) == 1:
                    # if there's only one output, forcibly change the name to "<silo_name>_input"
                    midprocess_input[f"silo{i}_input"] = list(train_output.values())[0]
                else:
                    for k, v in train_output.items():
                        midprocess_input[f"silo{i}_" + k] = v
                i += 1

            prev = self.midprocess(self.config, **midprocess_input)
            prev_output = self._process_at_orchestrator(prev) if prev else None
            output = {
                self.output_prefix + name: prev_output[name] for name in prev_output
            }
            return output

        @dsl.pipeline()
        def pipeline_function():
            self._merge_config()
            prev = self.preprocess(self.config)
            prev_output = self._process_at_orchestrator(prev) if prev else None

            for iter in range(self.config.federated_config.max_iterations):
                self.cur_fl_iteration = iter
                if prev_output:
                    prev_output = {
                        output_name.replace(self.output_prefix, ""): prev_output[
                            output_name
                        ]
                        for output_name in prev_output.keys()
                    }
                    subpipeline = _subpipeline_function(**prev_output)
                else:
                    subpipeline = _subpipeline_function()
                subpipeline.node_name = self.create_iteration_name()
                prev_output = subpipeline.outputs

            if len(prev_output) == 1:
                prev_output = {"input": list(prev_output.values())[0]}
            prev = self.postprocess(self.config, **prev_output)
            output = self._process_at_orchestrator(prev) if prev else None
            return output

        return pipeline_function

    def pipeline_instance(self, pipeline_function, config):
        """Creates an instance of the pipeline using arguments. User does not need to modify."""
        pipeline = pipeline_function()
        return pipeline
