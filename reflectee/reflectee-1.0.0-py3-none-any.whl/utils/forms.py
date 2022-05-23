from django.forms import ChoiceField, ModelChoiceField, modelform_factory

__all__ = [
    "get_form",
]


async def get_form(model, instance=None, form_fields=None, form_class=None):

    if not form_fields:
        form_fields = (
            [field.name for field in model._meta.get_fields() if field.editable]
            if model
            else []
        )

    form_kwargs = dict(instance=instance)
    form_class = (
        modelform_factory(model, fields=form_fields)
        if model and not form_class
        else form_class
    )
    form = form_class(**form_kwargs)
    form_data = await serialize_form(form)
    if form.instance:
        form_data.update(id=form.instance.pk)
    return form_data


async def serialize_form(form):
    fields = {}
    for field in form:
        type = str(field.field.__class__.__name__)
        field_data = dict(
            name=field.name,
            label=field.label,
            type=type,
            value=field.value(),
        )
        if isinstance(field.field, ModelChoiceField):
            model_field = (
                field.field.queryset.model
            )  # self.model._meta.get_field(field.name)
            field_data["stream"] = getattr(
                model_field,
                "_last_binding_stream",
                f"{model_field._meta.app_label}.{model_field._meta.object_name}",
            )

        elif isinstance(field.field, ChoiceField):
            field_data["options"] = [
                dict(
                    value=choice[0],
                    label=choice[1],
                )
                for choice in field.field.choices
            ]
            field_data["choices"] = {
                choice[0]: choice[1] for choice in field.field.choices
            }
        fields[field.name] = field_data

    return dict(
        errors=form.errors or None,
        # success=not form.errors if "submit" in request.data else None,
        # object=await self.serialize_retrieve(request, form.instance)
        # if form.instance
        # else None,
        fields=fields,
    )
