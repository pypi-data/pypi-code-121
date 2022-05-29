# -*- coding:utf-8 -*-
from __future__ import print_function
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, pre_save
from .models import Trash, VersionHistory, Event
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType
from . import signals
from django.contrib.auth.signals import user_logged_in
import json, logging
from xyz_util.datautils import JSONEncoder
from six import text_type

log = logging.getLogger('django')


@receiver(pre_delete, sender=None)
def save_object_to_trash(sender, **kwargs):
    if sender == Trash:
        return
    instance = kwargs['instance']
    if not hasattr(instance, "id"):
        return
    ctype = ContentType.objects.get_for_model(instance)
    id = instance.id
    name = text_type(instance)
    Trash.objects.update_or_create(
        content_type=ctype,
        object_id=id,
        defaults=dict(
            object_name=name,
            json_data=model_to_dict(instance)
        )
    )


@receiver(signals.to_save_version, sender=None)
def save_object_to_version_history(sender, **kwargs):
    if sender == VersionHistory:
        return
    instance = kwargs['instance']
    exclude_fields = kwargs.get("exclude_fields", [])
    if not hasattr(instance, "id") or instance.id is None:
        return
    ctype = ContentType.objects.get_for_model(instance)
    id = instance.id
    name = text_type(instance)
    data = model_to_dict(instance, exclude=exclude_fields)
    vo = VersionHistory.objects.filter(content_type=ctype, object_id=id).order_by("-version").first()
    func = lambda a: json.dumps(a, cls=JSONEncoder)
    cfs = []
    if vo:
        s1 = func(vo.json_data)
        s2 = func(data)
        if s1 == s2:
            return
        d1 = json.loads(s1)
        d2 = json.loads(s2)
        for k in d2.keys():
            if d2[k] != d1[k]:
                cfs.append(k)
        version = vo.version + 1
    else:
        version = 1

    history = VersionHistory.objects.create(
        content_type=ctype,
        object_id=id,
        version=version,
        object_name=name,
        json_data=data
    )
    if cfs:
        # print(cfs)
        signals.new_version_posted.send_robust(sender, instance=instance, history=history, changed_fields=cfs)


@receiver(signals.to_add_event)
def to_add_event(sender, **kwargs):
    try:
        instance = kwargs.pop('instance')
        Event.objects.create(owner=instance, name=kwargs['name'], context=kwargs.get('context'))
    except:
        import traceback
        log.error('common to_add_event error:%s', traceback.format_exc())


@receiver(user_logged_in)
def add_user_login_event(sender, **kwargs):
    user = kwargs['user']
    request = kwargs['request']
    m = request.META
    ip = m.get('HTTP_X_FORWARDED_FOR') or m.get('REMOTE_ADDR')
    name = 'login'
    login_type = getattr(user, 'login_type', None)
    if login_type:
        name = name + '.' + login_type
    backend = text_type(user.backend) if hasattr(user, 'backend') else None
    signals.to_add_event.send_robust(user._meta.model, instance=user, name=name, context={'backend': backend, 'ip': ip})
