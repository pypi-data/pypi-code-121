import logging

from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestPermsAssertMixin
from tests.models import Author, User

logger = logging.getLogger(__name__)


class PermTestsTest(TestPermsAssertMixin, TestCase):
    def setUp(self):
        self.client = APIClient(with_cookie=True)

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            username='user',
            email="user@example.com",
            password='test',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            is_superuser=True)
        User.objects.create_user(
            username='admin',
            email="admin@example.com",
            password='test',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            is_superuser=True)

    # API calls ---------------------------------------------------------------

    def list(self):
        Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        Author.objects.create(
            first_name='Philip Kindred',
            last_name='Dick',
            slug='philip-k-dick')
        Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            slug='isaac-asimov')
        return self.client.get('/api/admin/authors')

    def get(self):
        author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        return self.client.get(f'/api/admin/authors/{author.pk}')

    def post(self):
        return self.client.post('/api/admin/authors', dict(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien'))

    def put(self):
        author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        return self.client.put(f'/api/admin/authors/{author.pk}', dict(
            first_name='John Ronald Reuel Updated'))

    def delete(self):
        author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        return self.client.delete(f'/api/admin/authors/{author.pk}')

    # Tests -------------------------------------------------------------------

    USER_TESTS = {
        "user": dict(
            list=200, list__count=3,
            get=200,
            post=200,
            put=200,
            delete=200),
        "admin": dict(
            list=200, list__count=3,
            get=200,
            post=200,
            put=200,
            delete=200)}
