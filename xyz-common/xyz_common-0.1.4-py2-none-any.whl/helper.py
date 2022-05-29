# -*- coding:utf-8 -*- 
__author__ = 'denishuang'

from . import models
from django.contrib.contenttypes.models import ContentType


def extends_config(src_configs, dest_configs):
    return [dest_configs.filter(name=config.name).first() or config for config in src_configs]


def get_model_settings(model, name, owner_id=None):
    s, created = models.Setting.objects.get_or_create(
        owner_type=ContentType.objects.get_for_model(model),
        owner_id=owner_id,
        name=name,
        defaults=dict(
            json_data={}
        )
    )
    return s.json_data

def set_model_settings(model, name, value, owner_id=None):
    s, created = models.Setting.objects.update_or_create(
        owner_type=ContentType.objects.get_for_model(model),
        owner_id=owner_id,
        name=name,
        defaults=dict(
            json_data=value
        )
    )
    return s.json_data
