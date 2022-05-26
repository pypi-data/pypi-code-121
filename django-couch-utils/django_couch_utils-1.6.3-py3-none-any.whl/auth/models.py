
from datetime import datetime

from django.conf import settings

if getattr(settings, 'COUCHDB_WRAPPER', None) == 'couchdbcurl':
    from couchdbcurl.client import Document
elif getattr(settings, 'COUCHDB_WRAPPER', None) == 'couchdbrq':
    from couchdbrq.client import Document
else:
    raise Exception("Couchdb wrapper undefined wrong, please check settings.COUCHDB_WRAPPER")

from django_couch.auth.utils import make_password, check_password
from django.utils.crypto import salted_hmac

class User(Document):

    @property
    def pk(self):
        return self.id

    ## def is_active(self):
    ##     """Fake function. Always returns True"""
    ##     return True

    def is_authenticated(self):
        """Links to self.is_superuser"""
        return '_id' in self

    def get_and_delete_messages(self):
        return None

    def has_perm(self, perm):
        """Permissions system
Django-couch-utils tries to be compliant with basic django permissions system.
So, you must fill user documents with field `permission' which is list of application permission like "module1.permission1".

Example:
{
    username: "...",
    password: "...",
    permissions: ["users.user_edit", "users.user_delete", "files.edit"]
...
}

"""


        return self.is_superuser or perm in self.get_all_permissions()

    def has_perms(self, perm_list):
        """See has_perms() docs"""

        if self.is_superuser:
            return True

        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True


    def has_module_perms(self, module):
        """See has_perms() docs"""

        if self.is_superuser:
            return True

        modules = set([perm.split('.')[0] for perm in self.get_all_permissions()])
        return module in modules

    def get_all_permissions(self):

        if not hasattr(self, '_permissions'):
            # cache permissions

            perms = self.get('permissions', [])[:]  # copy perms
            if self.get('groups'):
                rows = self._db.view('_all_docs', keys=self.groups, include_docs=True).rows
                for row in rows:
                    perms.extend(row.doc.permissions)

            self._permissions = set(perms)


        return self._permissions



    def save(self, *args, **kwargs):
        """Save user object and update ``last_login`` field"""

        if hasattr(self, 'backend'):
            backend = self.backend
            del(self.backend)
        else:
            backend = None

        if hasattr(self, 'last_login') and type(self.last_login) == datetime:
            from django.conf import settings
            self.last_login = self.last_login.isoformat()

        if 'update_fields' in kwargs:
            del(kwargs['update_fields'])

        Document.save(self, *args, **kwargs)

        if backend:
            self.backend = backend

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


    @property
    def _meta(self):
        class DjangoFaker():

            @property
            def pk(self):
                return self

            def value_to_string(self, user):
                return user.id


        return DjangoFaker()


    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()
