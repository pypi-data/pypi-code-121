import pydantic.json


# Use this class as a type for complex data from the json, e.g., in the state_propagator function.
class Complex(complex):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern=r"[+-]?\d+\.?\d* *[+-] *\d+\.?\d*j",
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            v = "".join(v.split())

        return complex(v)


assert (
    complex not in pydantic.json.ENCODERS_BY_TYPE
), "Is complex type supported on newer version of pydantic?"
pydantic.json.ENCODERS_BY_TYPE[complex] = str
