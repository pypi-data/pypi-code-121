def get_data_dict(instance):
    """
    Get data dictionary from model instance.
    """
    data = {}
    for field in instance._meta.fields:
        if field.name not in ["id", "created_at", "updated_at"]:
            data[field.name] = getattr(instance, field.name)
    return data
