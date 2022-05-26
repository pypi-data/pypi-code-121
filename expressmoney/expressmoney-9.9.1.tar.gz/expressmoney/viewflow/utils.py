__all__ = ('fix_flow_signal', 'CustomCreateProcessView')

from django.contrib.auth import get_user_model
from viewflow.flow.views import CreateProcessView


User = get_user_model()


def fix_flow_signal(func):
    def _wrapper_fix_signal(self, **kwargs):
        kwargs.update({'self': self})
        func(**kwargs)

    return _wrapper_fix_signal


class CustomCreateProcessView(CreateProcessView):

    def dispatch(self, request, **kwargs):
        request.user = User.objects.using('default').get(id=request.user.id)
        return super().dispatch(request, **kwargs)
