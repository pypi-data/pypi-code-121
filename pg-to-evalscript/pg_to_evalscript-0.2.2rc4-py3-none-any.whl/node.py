import os
import uuid
import textwrap
import json
import pkgutil
from collections import defaultdict

from pg_to_evalscript.process_graph_utils import iterate, copy_dictionary


class ProcessDefinitionMissing(Exception):
    error_code = "ProcessDefinitionMissing"

    def __init__(self, process_id):
        super().__init__(f"Process '{process_id}' doesn't have a definition file.")


def pprint_dict(dictionary):
    return "\n".join("{}\t{}".format(k, v) for k, v in dictionary.items())


class Node:
    def __init__(
        self,
        node_id,
        process_id,
        arguments,
        child_nodes,
        dependencies,
        dependents,
        level,
        process_definitions_directory="javascript_processes",
        user_defined_processes={},
    ):
        self.user_defined_processes = user_defined_processes
        self.set_appropriate_class(process_id)
        self.variable_wrapper_string = uuid.uuid4().hex
        self.node_id = node_id
        self.level = level
        self.process_definitions_directory = process_definitions_directory
        self.node_varname_prefix = "node_"

        if self.is_process_defined(process_id):
            self.process_id = process_id
        else:
            raise ProcessDefinitionMissing(process_id)

        self.dependencies = dependencies
        self.dependents = dependents
        self._original_arguments = arguments
        self.arguments = self.prepare_arguments(arguments)
        self.process_function_name = f"{self.process_id}_{uuid.uuid4().hex}"

        if child_nodes is None:
            self.child_nodes = []
        else:
            self.child_nodes = child_nodes

    def __str__(self):
        delimiter = "-" * 80
        arguments = textwrap.indent(json.dumps(self._original_arguments, indent=4), "\t")
        return f"{delimiter}\nNode {self.node_id} ({self.process_id})\n\n\tArguments:\n{arguments}\n{delimiter}"

    def __repr__(self):
        return f"Node {self.node_id} ({self.process_id})\n"

    def set_appropriate_class(self, process_id):
        if process_id in self.user_defined_processes:
            self.__class__ = UserDefinedProcessNode
        else:
            class_types_for_process = {
                "reduce_dimension": ReduceDimensionNode,
                "add_dimension": AddDimensionNode,
                "load_collection": LoadCollectionNode,
                "save_result": SaveResultNode,
                "merge_cubes": MergeCubesNode,
                "if": IfNode,
                "apply": ApplyNode,
                "count": CountNode,
                "array_apply": ArrayApplyNode,
                "array_filter": ArrayFilterNode,
                "aggregate_temporal_period": AggregateTemporalPeriodNode,
                "apply_dimension": ApplyDimensionNode,
                "aggregate_temporal": AggregateTemporalNode,
            }
            if class_types_for_process.get(process_id):
                self.__class__ = class_types_for_process[process_id]

    def is_process_defined(self, process_id):
        try:
            return (
                pkgutil.get_data("pg_to_evalscript", f"{self.process_definitions_directory}/{process_id}.js")
                is not None
            )
        except:
            return False

    def indent_by_level(self, string):
        return textwrap.indent(string, "\t" * self.level)

    def get_process_function_name(self):
        return self.process_id

    def prepare_arguments(self, arguments):
        json_string = json.dumps(self.replace_arguments_source(copy_dictionary(arguments)))
        return json_string.replace(f'"{self.variable_wrapper_string}', "").replace(
            f'{self.variable_wrapper_string}"', ""
        )

    def replace_arguments_source(self, arguments):
        for k, v in iterate(arguments):
            if isinstance(v, dict) and len(v) == 1 and "process_graph" in v:
                continue
            elif isinstance(v, dict) and len(v) == 1 and "from_node" in v:
                arguments[k] = (
                    self.variable_wrapper_string
                    + self.node_varname_prefix
                    + v["from_node"]
                    + self.variable_wrapper_string
                )
            elif isinstance(v, dict) and len(v) == 1 and "from_parameter" in v:
                arguments[k] = (
                    self.variable_wrapper_string + f'arguments.{v["from_parameter"]}' + self.variable_wrapper_string
                )
            elif isinstance(v, dict) or isinstance(v, list):
                self.replace_arguments_source(v)
        return arguments

    def load_process_code(self):
        return pkgutil.get_data(
            "pg_to_evalscript", f"{self.process_definitions_directory}/{self.process_id}.js"
        ).decode("utf-8")

    def write_process(self):
        process_definition = self.load_process_code()
        return self.indent_by_level(process_definition)

    def write_call(self):
        return self.indent_by_level(
            f"let {self.node_varname_prefix}{self.node_id} = {self.process_function_name}({self.arguments})"
        )

    def write_function(self):
        newline = "\n"
        tab = "\t"
        return self.indent_by_level(
            f"""
function {self.process_function_name}(arguments) {{
{self.write_process()}
    return {self.get_process_function_name()}(arguments)
}}
"""
        )

    def get_dimensions_change(self, dimensions_of_inputs):
        return dimensions_of_inputs[0]


class ReduceDimensionNode(Node):
    def is_process_defined(self, process_id):
        return True

    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function reduce_dimension(arguments) {{
    function reducer(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    arguments['reducer'] = reducer;
    return reduce_dimension(arguments);  
}}
"""

    def get_dimensions_change(self, dimensions_of_inputs):
        def remove_dimension(name, dims):
            return list(filter(lambda x: x["name"] != name, dims))

        return remove_dimension(self._original_arguments["dimension"], dimensions_of_inputs[0])


class LoadCollectionNode(Node):
    def is_process_defined(self, process_id):
        return True


class SaveResultNode(Node):
    def is_process_defined(self, process_id):
        return True


class AddDimensionNode(Node):
    def get_dimensions_change(self, dimensions_of_inputs):
        return [*dimensions_of_inputs[0], {"name": self._original_arguments["name"], "size": 1}]


class MergeCubesNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        overlap_resolver_code = (
            f"""
function overlap_resolver(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
}}
"""
            if len(self.child_nodes) > 0
            else "const overlap_resolver=undefined;"
        )
        return f"""
function merge_cubes(arguments) {{
    {overlap_resolver_code}
    {self.load_process_code()}
    return merge_cubes({{...arguments, overlap_resolver: overlap_resolver }});
}}
"""

    def get_dimensions_change(self, dimensions_of_inputs):
        """
        merge_cubes process expects datacubes to have different labels in a single dimension.
        We can't know which dimension is it and what the new size will be.
        We can arbitrarily choose one and set its size to the sum, as it might get removed/reduced by later nodes
        So we set new sizes to the sums for *all* dimensions
        """
        dim_size_sums = defaultdict(int)

        for dimensions_of_input in dimensions_of_inputs:
            for dim in dimensions_of_input:
                if dim["size"] is not None:
                    dim_size_sums[dim["name"]] += dim["size"]
                else:
                    dim_size_sums[dim["name"]] = None

        output_dimensions = []
        for dim in dim_size_sums:
            output_dimensions.append({"name": dim, "size": dim_size_sums[dim]})

        return output_dimensions


class IfNode(Node):
    def get_process_function_name(self):
        return "_if"


class ApplyNode(Node):
    def write_process(self):
        newline = "\n"
        return f"""
function apply(arguments) {{  

   function process(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    arguments['process'] = process;
    return apply(arguments);

}}
"""


class ApplyDimensionNode(Node):
    def write_process(self):
        newline = "\n"
        return f"""
function apply_dimension(arguments) {{
   function process(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    return apply_dimension({{...arguments, process}})
}}
"""


class CountNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function count(arguments) {{
    function condition(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {(self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id) if len(self.child_nodes) > 0 else None};
    }}

    {pkgutil.get_data("pg_to_evalscript", f"{self.process_definitions_directory}/is_valid.js").decode("utf-8")}

    {self.load_process_code()}
    return count(arguments);
}}
"""


class ArrayApplyNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function array_apply(arguments) {{
    function process(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    const {{ data, context }} = arguments;
    return array_apply({{ data: data, context: context, process: process }})
}}
"""


class ArrayFilterNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function array_filter(arguments) {{
    function condition(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    return array_filter(arguments);
}}
"""


class AggregateTemporalPeriodNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function aggregate_temporal_period(arguments) {{
    function reducer(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    arguments['reducer'] = reducer;
    return aggregate_temporal_period(arguments)
}}
"""


class AggregateTemporalNode(Node):
    def write_process(self):
        newline = "\n"
        tab = "\t"
        return f"""
function aggregate_temporal(arguments) {{
    function reducer(arguments) {{
    {newline.join(node.write_function() for node in self.child_nodes)}
    {newline.join(node.write_call() for node in self.child_nodes)}
        return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
    }}

    {self.load_process_code()}
    return aggregate_temporal({{...arguments, reducer: reducer}});
}}
"""


class UserDefinedProcessNode(Node):
    def is_process_defined(self, process_id):
        return True

    def write_process(self):
        newline = "\n"
        return f"""
function {self.process_id}(arguments) {{  
{newline.join(node.write_function() for node in self.child_nodes)}
{newline.join(node.write_call() for node in self.child_nodes)}
    return {self.child_nodes[-1].node_varname_prefix + self.child_nodes[-1].node_id};
}}
"""
