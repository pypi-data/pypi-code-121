import botocore.client
import botocore.docs.docstring


def parse(hub, client: "botocore.client.BaseClient", service: str, operation: str):
    function = getattr(client, operation)
    doc: botocore.docs.docstring.ClientMethodDocstring = function.__doc__
    docstring = hub.tool.format.html.parse(doc._gen_kwargs["method_description"])
    parameters = {}
    try:
        # TODO what does botocore expect?
        params = doc._gen_kwargs["operation_model"].input_shape.members
        required_params = doc._gen_kwargs[
            "operation_model"
        ].input_shape.required_members
        for p, data in params.items():
            parameters[p] = hub.pop_create.aws.param.parse(
                param=data, required=p in required_params
            )
    except AttributeError as e:
        hub.log.error(f"Error reading parameters for {service}.{operation}: {e}")
        parameters = {}
    try:
        return_type = hub.pop_create.aws.plugin.type(
            doc._gen_kwargs["operation_model"].output_shape.type_name
        )
    except AttributeError:
        return_type = None

    return_fields = {}
    if return_type == "structure" or return_type == "Dict":
        try:
            return_fields = next(
                iter(doc._gen_kwargs["operation_model"].output_shape.members.items())
            )[1].members
        except AttributeError:
            return_fields = {}

    ret = {
        "doc": "\n".join(hub.tool.format.wrap.wrap(docstring, width=112)),
        "params": parameters,
        "return_type": return_type,
        "hardcoded": {
            "service": service,
            "operation": operation,
            "return_fields": return_fields,
        },
    }

    return ret
