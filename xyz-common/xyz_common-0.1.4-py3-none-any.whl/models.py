# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from six import text_type

from xyz_util.modelutils import JSONField


class Setting(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "配置"
        unique_together = ("owner_type", "owner_id", "name")

    owner_type = models.ForeignKey(ContentType, verbose_name='属主类别', null=True, blank=True,
                                   on_delete=models.PROTECT)
    owner_id = models.PositiveIntegerField(verbose_name='属主编号', null=True, blank=True)
    owner = GenericForeignKey('owner_type', 'owner_id')
    name = models.CharField("名称", max_length=64, null=False, blank=False)
    json_data = JSONField("内容", blank=True, null=True)

    def __str__(self):
        owner = self.owner if self.owner_id else self.owner_type
        return "%s.%s" % (owner, self.name)



class Event(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "事件"
        ordering = ('-create_time',)

    owner_type = models.ForeignKey(ContentType, verbose_name='属主类别', null=True, blank=True,
                                   on_delete=models.PROTECT)
    owner_id = models.PositiveIntegerField(verbose_name='属主编号', null=True, blank=True, db_index=True)
    owner = GenericForeignKey('owner_type', 'owner_id')
    name = models.CharField("名称", max_length=64)
    context = JSONField("上下文", blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s.%s@%s" % (self.owner, self.name, self.create_time.isoformat())

    def object_name(self):
        return text_type(self.owner)

    object_name.short_description = "对象名称"


class Trash(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "垃圾"
        unique_together = ("content_type", "object_id")

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    object_name = models.CharField("名称", max_length=256, null=True, blank=True)
    json_data = JSONField("内容", blank=True, null=True)
    create_time = models.DateTimeField("删除时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s.%s" % (self.content_type, self.object_id)

    def recover(self):
        d = self.json_data
        nd = {}
        M = self.content_type.model_class()
        rd = {}
        for f in M._meta.get_fields():
            if f.name not in d:
                continue
            if f.related_model:
                if d[f.name]:
                    if isinstance(d[f.name], list):
                        rd[f.name] = f.related_model.objects.filter(id__in=d[f.name])
                    else:
                        nd[f.name] = f.related_model.objects.get(id=d[f.name])
            else:
                nd[f.name] = d[f.name]
        m = M(**nd)
        m.save()
        for k, v in rd.items():
            setattr(m, k, v)

class VersionHistory(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "版本历史"
        unique_together = ("content_type", "object_id", "version")

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField("对象ID", db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, null=True, blank=True)
    version = models.PositiveIntegerField("版本")
    json_data = JSONField("内容", blank=True, null=True)
    create_time = models.DateTimeField("更新时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s.%s.V%d" % (self.content_type, self.object_id, self.version)

    def recover(self):
        obj = self.content_object
        m = obj._meta
        from django.db.models.fields.related import ForeignKey
        data = self.json_data
        for f in m.fields:
            fn = f.name
            if fn not in data:
                continue
            v = data.get(fn)
            if isinstance(f, ForeignKey):
                fn = "%s_id" % fn
            setattr(obj, fn, v)
        obj.save()

