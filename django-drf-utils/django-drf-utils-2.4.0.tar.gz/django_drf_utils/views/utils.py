from typing import Collection, Type

from rest_framework import response, serializers, status
from rest_framework.permissions import BasePermission
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.decorators import action
from rest_framework.response import Response


class DetailedResponse(response.Response):
    def __init__(self, detail, status_code):
        super().__init__({"detail": detail}, status_code)


def get_model(serializer):
    return serializer.Meta.model


def get_fields(model):
    return model._meta.fields  # pylint: disable=protected-access


class UniqueSchema(AutoSchema):
    def get_responses(self, path, method):
        return {
            status.HTTP_200_OK: {"description": "is unique"},
            status.HTTP_409_CONFLICT: {"description": "is NOT unique"},
        }

    def get_component_name(self, serializer):
        return f"Unique{super().get_component_name(serializer)}"

    def get_components(self, path, method):
        serializer = self.get_serializer(path, method)
        if not isinstance(serializer, serializers.Serializer):
            return {}
        content = self.map_serializer(serializer)
        properties = {
            field.name: content["properties"][field.name]
            for field in get_fields(get_model(serializer))
            if field.unique
        }
        return {
            self.get_component_name(serializer): {
                "type": content["type"],
                "properties": properties,
            }
        }


# TODO DRF contribution
def unique_check(permission_classes: Collection[Type[BasePermission]]):
    def decorator(cls):
        @action(
            detail=False,
            permission_classes=permission_classes,
            methods=["post"],
            schema=UniqueSchema(),
        )
        def unique(self, request, pk=None):  # pylint: disable=unused-argument
            model = get_model(self.get_serializer_class())
            for field in get_fields(model):
                if (
                    field.unique
                    and field.name in request.data
                    and model.objects.filter(
                        **{field.name: request.data[field.name]}
                    ).exists()
                ):
                    return DetailedResponse(
                        f"{field.name} is not unique!",
                        status_code=status.HTTP_409_CONFLICT,
                    )

            return Response(status=status.HTTP_200_OK)

        cls.unique = unique
        return cls

    return decorator
