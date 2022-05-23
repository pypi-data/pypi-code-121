from importlib import import_module

from django.conf import settings
from django.utils.timezone import now


class EmptyCalss:
    pass


def import_class_from_string(serializer_class_name):
    mixin_path = settings.SERIALIZERS_MIXIN.get(serializer_class_name)
    if not mixin_path:
        return EmptyCalss
    module_path, class_name = mixin_path.rsplit(".", 1)
    module = import_module(module_path)
    Mixin = getattr(module, class_name)
    return Mixin


def product_media_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return f"product_media/{instance.product.id}_{instance.order_value}_{int(now().timestamp())}.{ext}"
