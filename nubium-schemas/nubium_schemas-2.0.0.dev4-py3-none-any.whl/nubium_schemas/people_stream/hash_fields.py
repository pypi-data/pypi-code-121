from .schemas import PersonSchema


def _generate_eloqua_person_mask(cls):
    return {
        field.name: field.metadata.get(
            "eloqua_hash", _generate_eloqua_person_mask(field.type) if hasattr(field.type, "metadata") else False
        )
        for field in cls.get_fields()
    }


eloqua_person_mask = _generate_eloqua_person_mask(PersonSchema)
