from django.conf import settings


class FakeRequest:
    user = None
    POST = {'action-publish': True}

    def get_host(self):
        return settings.HOSTNAME

    def get_port(self):
        return settings.PORT
