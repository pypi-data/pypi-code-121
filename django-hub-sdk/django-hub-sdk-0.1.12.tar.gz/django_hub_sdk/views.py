import hashlib
import random
import string
from urllib.parse import urlencode, quote_plus

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import views, response, status

from .authentication import HubJWTAuthentication
from .models import HubOauthToken, HubUser


# Create your views here.
class LoginView(views.APIView):
    def get(self, request):
        characters = string.ascii_letters + string.digits
        state = ''.join(random.choice(characters) for i in range(40))

        cache.set("state-" + state, state)
        cache.set(state, request.get_full_path())

        payload = {
            'client_id': settings.HUB_OAUTH_CLIENT_ID,
            'redirect_uri': settings.HUB_OAUTH_REDIRECT,
            'response_type': 'code',
            'scope': settings.HUB_OAUTH_SCOPES,
            'state': state,
            'url': request.query_params.get('url', '/')
        }

        redirect_uri = settings.HUB_BASE_FRONT_URI + settings.HUB_OAUTH_AUTHORIZE_URI
        redirect_uri += '?' + urlencode(payload, quote_via=quote_plus)

        return response.Response(data={
            "login_url": redirect_uri
        })


class CallbackView(views.APIView):
    def get(self, request):
        params = request.query_params

        code = params.get('code', '')
        state = params.get('state', '')
        url = params.get('url', '')

        cache_state = cache.get("state-" + state, '')

        if len(cache_state) > 0 and state != cache_state:
            return response.Response({
                'message': _('State is not valid')
            }, status.HTTP_404_NOT_FOUND)

        token_uri = settings.HUB_BASE_URI + settings.HUB_OAUTH_TOKEN_URI
        response_token = requests.post(token_uri, data={
            'grant_type': 'authorization_code',
            'client_id': settings.HUB_OAUTH_CLIENT_ID,
            'client_secret': settings.HUB_OAUTH_CLIENT_SECRET,
            'redirect_uri': settings.HUB_OAUTH_REDIRECT,
            'code': code,
        }, headers={
            "Accept": "application/json"
        })

        json_cache = response_token.json()
        json_cache['expires_in_dt'] = timezone.now() + timezone.timedelta(seconds=json_cache['expires_in'])

        HubOauthToken.objects.create(
            access_token=hashlib.md5(json_cache['access_token'].encode('utf-8')).hexdigest(),
            refresh_token=json_cache['refresh_token'],
            expires_in=json_cache['expires_in'],
            expires_in_dt=json_cache['expires_in_dt']
        )

        json_cache['redirect'] = url

        return response.Response(json_cache)


class UserMeView(views.APIView):
    authentication_classes = [HubJWTAuthentication]

    def get(self, request):
        url = settings.HUB_BASE_URI + settings.HUB_BASE_PREFIX + settings.HUB_OAUTH_USERINFO_URI
        query_params = {
            "project": settings.HUB_APP_SLUG
        }
        url += '?' + urlencode(query_params, quote_via=quote_plus)
        hub_response = requests.get(url, headers={
            "Accept": "application/json",
            "Authorization": request.headers.get('Authorization')
        })
        return response.Response(data=hub_response.json())


class LogoutView(views.APIView):
    authentication_classes = [HubJWTAuthentication]

    def get(self, request):
        logout_url = settings.HUB_BASE_FRONT_URI + '/auth/logout'

        hub_users = HubUser.objects.filter(user_id=request.user.id)
        hub_user_ids = hub_users.select_related('token').values_list('token_id', flat=True)
        HubOauthToken.objects.filter(id__in=hub_user_ids).delete()
        hub_users.delete()

        return response.Response(data={
            "logout_url": logout_url
        })


class RefreshTokenView(views.APIView):
    authentication_classes = [HubJWTAuthentication]

    def get(self, request):
        bearer_token = request.headers.get('Authorization')
        bearer_token_hash = hashlib.md5(bearer_token.encode('utf-8')).hexdigest()
        bearer_token_cache = HubOauthToken.objects.filter(access_token=bearer_token_hash).first()

        if bearer_token_cache is None:
            return response.Response(data={
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Bearer Token is Required"
            }, status=status.HTTP_401_UNAUTHORIZED)

        if bearer_token_cache.is_expired():
            refresh_uri = settings.HUB_BASE_URI + settings.HUB_OAUTH_TOKEN_URI
            refresh_response = requests.post(refresh_uri, data={
                'grant_type': 'refresh_token',
                'refresh_token': bearer_token_cache.refresh_token,
                'client_id': settings.HUB_OAUTH_CLIENT_ID,
                'client_secret': settings.HUB_OAUTH_CLIENT_SECRET,
                'scope': settings.HUB_OAUTH_SCOPES,
            })
            json_cache = refresh_response.json()
            json_cache['expires_in_dt'] = timezone.now() + timezone.timedelta(seconds=json_cache['expires_in'])
            HubOauthToken.objects.create(
                access_token=hashlib.md5(json_cache['access_token'].encode('utf-8')).hexdigest(),
                refresh_token=json_cache['refresh_token'],
                expires_in=json_cache['expires_in'],
                expires_in_dt=json_cache['expires_in_dt']
            )
            return response.Response(data={
                'access_token': json_cache['access_token']
            })

        return response.Response(data={
            'access_token': bearer_token_cache.access_token
        })
