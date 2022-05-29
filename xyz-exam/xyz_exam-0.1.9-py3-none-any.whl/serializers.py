# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class PaperSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Paper
        exclude = ()
        read_only_fields = ('user', 'questions_count')


class PaperListSerializer(PaperSerializer):
    class Meta(PaperSerializer.Meta):
        exclude = ('content_object', 'content')
        read_only_fields = ('user', 'questions_count')


class AnswerSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', label='姓名', read_only=True)
    class Meta:
        model = models.Answer
        exclude = ()
        read_only_fields = ('user',)


class AnswerListSerializer(AnswerSerializer):
    class Meta(AnswerSerializer.Meta):
        fields = ['paper', 'user', 'std_score', 'seconds', 'create_time']


class StatSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stat
        exclude = ()


class PerformanceSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    # paper_name = serializers.CharField(source="paper.title", label='试卷', read_only=True)
    # user_name = serializers.CharField(source="user.get_full_name", label='学生', read_only=True)

    class Meta:
        model = models.Performance
        exclude = ()
        read_only_fields = ['user', 'paper_name', 'user_name']


class FaultSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Fault
        exclude = ()


class ExamSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Exam
        exclude = ('target_users',)
        read_only_fields = ('target_user_count',)


class ExamResultSerializer(ExamSerializer):
    paper = PaperSerializer()
    answers = AnswerSerializer(source='paper.answers', many=True)
    class Meta(ExamSerializer.Meta):
        pass


class ExamListSerializer(ExamSerializer):
    paper = None

    class Meta(ExamSerializer.Meta):
        exclude = ('target_users',)
