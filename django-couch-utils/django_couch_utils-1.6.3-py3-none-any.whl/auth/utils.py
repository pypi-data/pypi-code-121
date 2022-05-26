
import hashlib
import random

def check_password(password, hash):
    raise NotImplemented("This code is not implemented for this django version")

def make_password(password):
    raise NotImplemented("This code is not implemented for this django version")
    

try:
    # for django 1.4
    from django.contrib.auth.hashers import check_password, make_password
except ImportError:
    # for django 1.3

    try:
        from django.contrib.auth.models import check_password
    except ImportError:
        pass
    
    
    def make_password(password, salt=None):
        """Pre-django 1.4 hashing scheme"""

        if not salt:
            salt = hashlib.sha1(str(random.random()) + str(random.random())).hexdigest()[:5]
            
        hsh = hashlib.sha1(salt + password.encode('utf-8')).hexdigest()
        return 'sha1$%s$%s' % (salt, hsh)
