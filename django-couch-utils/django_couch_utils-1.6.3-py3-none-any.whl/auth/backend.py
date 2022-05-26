
import django_couch
from django.conf import settings
from django_couch.auth.utils import check_password
from django_couch.auth.models import User


if getattr(settings, 'COUCHDB_WRAPPER', None) == 'couchdbcurl':
    from couchdbcurl.client import ResourceNotFound
elif getattr(settings, 'COUCHDB_WRAPPER', None) == 'couchdbrq':
    from couchdbrq.client import ResourceNotFound
else:
    raise Exception("Couchdb wrapper undefined wrong, please check settings.COUCHDB_WRAPPER")


class CouchBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = True

    def __init__(self):
        print 'aa'
        self.db = django_couch.db(settings.COUCHDB_AUTH_DB)

    def get_user(self, user_id):
        print 'get_user', user_id
        try:
            user = self.db[user_id]
            if len(self.db.view(settings.COUCHDB_AUTH_VIEW, key=user.username, limit=1).rows):
                return User(user, _db = self.db)
            else:
                return None
        except ResourceNotFound:
            return None


    def authenticate(self, username, password):
        print 'auth user', username
        rows = self.db.view(settings.COUCHDB_AUTH_VIEW, key = username.lower(), include_docs = True, limit = 1).rows

        if len(rows) and check_password(password, rows[0].value):
            return User(rows[0].doc, _db = self.db)
        pass
