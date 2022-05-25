from django.test import TestCase

from djangoldp.tests.models import User, Circle, Project
from djangoldp.serializers import LDPSerializer
from djangoldp.related import get_prefetch_fields


class LDPViewSet(TestCase):

    user_serializer_fields = ['@id', 'username', 'first_name', 'last_name', 'email', 'userprofile', 'conversation_set',
                              'circle_set', 'projects']
    user_expected_fields = {'userprofile', 'conversation_set', 'circle_set', 'projects', 'circle_set__owner',
                            'conversation_set__author_user', 'conversation_set__peer_user', 'circle_set__space'}
    project_serializer_fields = ['@id', 'description', 'members']
    project_expected_fields = {'members', 'members__userprofile'}

    def _get_serializer(self, model, depth, fields):
        meta_args = {'model': model, 'depth': depth, 'fields': fields}
        meta_class = type('Meta', (), meta_args)
        return (type(LDPSerializer)('TestSerializer', (LDPSerializer,), {'Meta': meta_class}))()

    def test_get_prefetch_fields_user(self):
        model = User
        depth = 0
        serializer_fields = self.user_serializer_fields
        expected_fields = self.user_expected_fields
        serializer = self._get_serializer(model, depth, serializer_fields)
        result = get_prefetch_fields(model, serializer, depth)
        self.assertEqual(expected_fields, result)

    def test_get_prefetch_fields_circle(self):
        model = Circle
        depth = 0
        serializer_fields = ['@id', 'name', 'description', 'owner', 'members', 'team']
        expected_fields = {'owner', 'members', 'team', 'members__user', 'members__circle', 'team__userprofile', 'space'}
        serializer = self._get_serializer(model, depth, serializer_fields)
        result = get_prefetch_fields(model, serializer, depth)
        self.assertEqual(expected_fields, result)

    def test_get_prefetch_fields_project(self):
        model = Project
        depth = 0
        serializer_fields = self.project_serializer_fields
        expected_fields = self.project_expected_fields
        serializer = self._get_serializer(model, depth, serializer_fields)
        result = get_prefetch_fields(model, serializer, depth)
        self.assertEqual(expected_fields, result)

    # TODO: dynamically generating serializer fields is necessary to retrieve many-to-many fields at depth > 0,
    #  but the _all_ default has issues detecting reverse many-to-many fields
    '''def test_get_prefetch_fields_depth_1(self):
        model = Project
        depth = 2
        serializer_fields = self.project_serializer_fields
        user_expected = set(['team__' + x for x in self.user_expected_fields])
        expected_fields = self.project_expected_fields.union(user_expected)
        serializer = self._get_serializer(model, depth, serializer_fields)
        result = get_prefetch_fields(model, serializer, depth)
        self.assertEqual(expected_fields, result)'''
