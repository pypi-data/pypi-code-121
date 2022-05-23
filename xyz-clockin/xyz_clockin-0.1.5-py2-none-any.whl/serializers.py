# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models

class ProjectSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ()
        read_only_fields = ('creator', 'create_time')

class GroupSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', label=models.Project._meta.verbose_name, read_only=True)
    class Meta:
        model = models.Group
        exclude = ()
        read_only_fields = ('create_time',)

class SessionSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', label=models.Group._meta.verbose_name, read_only=True)
    project_id = serializers.IntegerField(source='group.project_id', label=models.Project._meta.verbose_name, read_only=True)
    class Meta:
        model = models.Session
        exclude = ()

class MemberShipSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', label=models.Group._meta.verbose_name, read_only=True)
    class Meta:
        model = models.MemberShip
        exclude = ()


class PointSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', label=models.Group._meta.verbose_name, read_only=True)
    session_name = serializers.CharField(source='session.name', label=models.Session._meta.verbose_name, read_only=True)
    class Meta:
        model = models.Point
        exclude = ()
