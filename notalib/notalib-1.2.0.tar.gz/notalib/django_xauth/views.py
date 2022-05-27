from .models import Nothing
from .serializers import NothingSerializer

from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer


# Example usage:
#
# router.register(r'auth-check', DirtyHackAuthCheckViewSet)
# ...
# path('api/auth', auth_view),


@csrf_exempt
def auth_view(request):
	username = request.POST.get('username', None)
	password = request.POST.get('password', None)
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return HttpResponse('{"result": "ok"}', status=200)
	else:
		return HttpResponse('{"result": "fail"}', status=403)


@renderer_classes([JSONRenderer])
class DirtyHackAuthCheckViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Nothing.objects.none()
	serializer_class = NothingSerializer
