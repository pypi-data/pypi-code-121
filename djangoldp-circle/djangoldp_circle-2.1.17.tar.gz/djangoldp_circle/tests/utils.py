import uuid
from djangoldp_account.models import LDPUser


def get_random_user(is_superuser=False):
    return LDPUser.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                  last_name='Test', username=str(uuid.uuid4()), is_superuser=is_superuser)
