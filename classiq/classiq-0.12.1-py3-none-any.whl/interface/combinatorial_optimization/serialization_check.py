import io

from pyomo.core import ConcreteModel

from classiq.interface.combinatorial_optimization import model_parser, model_serializer


def pprint_string(model: ConcreteModel) -> str:
    f = io.StringIO()
    model.pprint(ostream=f)
    return f.getvalue()


def serialize_and_parse(model: ConcreteModel) -> ConcreteModel:
    serialization_dict = model_serializer.to_json(model, return_dict=True)
    model_copy, _ = model_parser.from_json(obj_dict=serialization_dict)

    model_string = pprint_string(model)
    model_copy_string = pprint_string(model_copy)

    assert model_string == model_copy_string, model_copy_string
    return model_copy
