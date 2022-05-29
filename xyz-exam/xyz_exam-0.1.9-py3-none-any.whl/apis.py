# -*- coding:utf-8 -*-
from __future__ import division

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from xyz_util.statutils import do_rest_stat_action, using_stats_db
from xyz_restful.mixins import UserApiMixin, BatchActionMixin
from . import models, serializers, stats, helper
from rest_framework import viewsets, decorators, response, status
from xyz_restful.decorators import register
from xyz_dailylog.mixins import ViewsMixin


@register()
class PaperViewSet(ViewsMixin, UserApiMixin, BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Paper.objects.all()
    serializer_class = serializers.PaperSerializer
    search_fields = ('title',)
    filter_fields = {
        'id': ['in', 'exact'],
        'owner_id': ['exact', 'in'],
        'is_active': ['exact'],
        'title': ['exact'],
        # 'is_break_through': ['exact'],
        'owner_type': ['exact'],
        'tags': ['exact'],
        'content': ['contains'],
        'create_time': ['range']
    }
    ordering_fields = ('is_active', 'title', 'create_time', 'questions_count')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PaperListSerializer
        return super(PaperViewSet, self).get_serializer_class()

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_paper)

    @decorators.action(['GET', 'POST'], detail=True)
    def image_signature(self, request, pk):
        from xyz_qcloud.cos import gen_signature
        return response.Response(gen_signature(allow_prefix='/exam/paper/%s/images/*' % self.get_object().id))

    @decorators.action(['GET'], detail=False)
    def ids(self, request):
        qset = self.filter_queryset(self.get_queryset()).values_list('id', flat=True)
        return response.Response({'ids': list(qset)})

    @decorators.action(['GET'], detail=False, filter_backends=[DjangoFilterBackend])
    @method_decorator(cache_page(60 * 60 * 2))
    def count(self, request):
        c = self.filter_queryset(self.get_queryset()).count()
        return response.Response({'count': c})

    @decorators.action(['GET'], detail=False)
    def collect_questions(self, request):
        from .stores import QuestionStore
        from xyz_util.mongoutils import get_paginated_response, normalize_filter_condition
        st = QuestionStore()
        qd = request.GET
        rand = qd.get('random', False)
        d = normalize_filter_condition(qd, st.field_types, st.fields)
        if rand:
            from xyz_util.mongoutils import drop_id_field
            return response.Response(dict(results=drop_id_field(st.random_find(d, count=int(qd.get('count', 20))))))
        return get_paginated_response(self, st.find(d))

    @decorators.action(['GET'], detail=False)
    def questions_group(self, request):
        from .stores import QuestionStore
        from xyz_util.mongoutils import normalize_filter_condition
        st = QuestionStore()
        qd = request.GET
        group = qd.get('group', 'paperId')
        d = normalize_filter_condition(qd, st.field_types, st.fields)
        return response.Response(st.count_by(group, d, output='dict'))

    @decorators.action(['PATCH'], detail=True)
    def outline_question(self, request, pk):
        from .stores import QuestionStore
        st = QuestionStore()
        rd = request.data
        uid = rd.get('uid')
        qd = {'paperId': int(pk), 'uid': uid }
        print(qd)
        st.update(qd, {'outline': rd.get('outline')})
        return response.Response(rd)


@register()
class AnswerViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer
    filter_fields = ('paper', 'user')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AnswerListSerializer
        return super(AnswerViewSet, self).get_serializer_class()

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_answer)

    @decorators.action(['PATCH'], detail=True, permission_classes=[], filter_backends=[])
    def grade(self, request, pk):
        qs = request.query_params
        exam_id = qs.get('exam')
        error = helper.check_token(request, exam_id)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request)


@register()
class StatViewSet(UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Stat.objects.all()
    serializer_class = serializers.StatSerializer
    filter_fields = ('paper',)


@register()
class PerformanceViewSet(UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = using_stats_db(models.Performance.objects.all())
    serializer_class = serializers.PerformanceSerializer
    filter_fields = {
        'paper': ['exact', 'in'],
        'paper_id': ['exact', 'in'],
        'user': ['exact']
    }
    search_fields = ('paper__title', 'user__first_name')
    ordering_fields = ('score', 'update_time')


@register()
class FaultViewSet(UserApiMixin, BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Fault.objects.all()
    serializer_class = serializers.FaultSerializer
    filter_fields = {
        'paper': ['exact', 'in'],
        'question_id': ['exact'],
        'question_type': ['exact'],
        'corrected': ['exact'],
        'is_active': ['exact'],
        'user': ['exact'],
        'paper__owner_type': ['exact'],
        'paper__owner_id': ['exact'],
        'create_time': ['range']
    }
    ordering_fields = ['times', 'update_time']

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_fault)

    @decorators.action(['patch'], detail=True)
    def redo(self, request, pk):
        fault = self.get_object()
        rl = fault.detail.setdefault('result_list', [])
        right = request.data['right']
        rl.append(right)
        if not right:
            fault.times += 1
        fault.save()
        return response.Response(self.get_serializer(instance=fault).data)

    @decorators.action(['patch'], detail=False)
    def batch_correct(self, request):
        from datetime import datetime
        return self.do_batch_action('corrected', True, extra_params=dict(update_time=datetime.now()))


@register()
class ExamViewSet(BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Exam.objects.all()
    serializer_class = serializers.ExamSerializer
    search_fields = ('name',)
    filter_fields = {
        'name': ['exact', 'in'],
        'is_active': ['exact', 'in'],
        'owner_type': ['exact'],
        'owner_id': ['exact', 'in'],
        'begin_time': ['gte', 'lte'],
        'manual_grade': ['exact']
    }

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['GET', 'POST'], detail=True)
    def user_answer_signature(self, request, pk):
        from xyz_qcloud.cos import gen_signature
        sign = gen_signature(allow_prefix='/exam/exam/%s/answer/%s/*' % (pk, request.user.id))
        return response.Response(sign)

    @decorators.action(['GET'], detail=True, permission_classes=[], filter_backends=[])
    def all_answers(self, request, pk):
        error = helper.check_token(request, pk)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        paper = exam.paper
        answers = paper.answers
        uids = list(answers.values_list('user_id', flat=True))
        from xyz_school.models import Student
        students = Student.objects.filter(user_id__in=uids).values('number', 'name', 'id', 'user')
        return response.Response(dict(
            students=students,
            answers=serializers.AnswerSerializer(answers, many=True).data,
            paper=serializers.PaperSerializer(paper).data,
            exam=serializers.ExamSerializer(exam).data
        ))

    @decorators.action(['GET'], detail=True)
    def get_grade_token(self, request, pk):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner(salt=str(pk))
        from datetime import datetime, timedelta
        import json, base64
        expire_time = datetime.now() + timedelta(days=7)
        d = dict(exam=pk, expire=expire_time.isoformat())
        token = signer.sign(base64.b64encode(json.dumps(d).encode('utf8')).decode())
        return response.Response(dict(token=token))

    @decorators.action(['GET'], detail=True)
    def performance(self, request, pk):
        exam = self.get_object()
        return response.Response(dict(performance=exam.performance()))

    @decorators.action(['GET'], detail=True, permission_classes=[], filter_backends=[])
    def result(self, request, pk):
        error = helper.check_token(request, pk)
        if error:
            return response.Response(error, status=status.HTTP_403_FORBIDDEN)
        exam = self.get_object()
        return response.Response(serializers.ExamResultSerializer(exam).data)
