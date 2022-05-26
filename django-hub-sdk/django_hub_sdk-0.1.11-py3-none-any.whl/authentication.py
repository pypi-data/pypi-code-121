import hashlib
import random
import string
from urllib.parse import urlencode, quote_plus

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from rest_framework import authentication

from .models import HubUser, HubOauthToken, UserCompany


class LoginUserByCache:
    def get_programmatic_jwt(self):
        url = settings.HUB_BASE_URI + settings.HUB_OAUTH_TOKEN_URI
        response = requests.post(url, headers={
            "Accept": "application/json",
        }, data={
            'grant_type': 'client_credentials',
            'client_id': settings.HUB_PROGRAMMATIC_CLIENT,
            'client_secret': settings.HUB_PROGRAMMATIC_SECRET,
            'scope': '*',
        })
        return response.json()['access_token']

    def update_or_create_company(self, user, company_uuid):
        url = settings.HUB_BASE_URI + settings.HUB_BASE_PREFIX + settings.HUB_PROGRAMMATIC_PREFIX + '/companies'
        url += '/' + company_uuid
        programmatic_token = self.get_programmatic_jwt()

        company_response = requests.get(url, headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + programmatic_token
        })

        hub_company = company_response.json()['result']

        company, updated = UserCompany.objects.update_or_create(
            uuid=hub_company['uuid'],
            defaults={
                'name': hub_company['name'],
            }
        )

        user.company = company
        user.save()

    def get_hub_user(self, key):
        url = settings.HUB_BASE_URI + settings.HUB_BASE_PREFIX + settings.HUB_OAUTH_USERINFO_URI
        query_params = {
            "project": settings.HUB_APP_SLUG
        }
        url += '?' + urlencode(query_params, quote_via=quote_plus)
        response = requests.get(url, headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + key
        })
        return response.json()['result']

    def update_or_create_user(self, hub_user):
        user_model = get_user_model()

        is_superuser = False
        if "is_superuser" in hub_user:
            is_superuser = True

        first_name, last_name = hub_user['name'].split(" ", 1)
        username = hub_user['email'].split('@')[0]

        user, updated = user_model.objects.update_or_create(
            email=hub_user['email'],
            hub_uuid=hub_user['uuid'],
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'is_superuser': is_superuser,
                'username': username,
                'avatar': hub_user['avatar']
            }
        )

        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for i in range(20))
        user.set_password(password)
        user.save()

        self.update_or_create_company(user, hub_user['company'])
        self.update_or_create_permissions(user, hub_user['user_permissions'])

        return user

    def update_or_create_permissions(self, user, hub_permissions):
        for key, value in hub_permissions:
            model, action = key.split(".")
            content_type = ContentType.objects.filter(model=model).first()
            if content_type:
                permission, updated = Permission.objects.update_or_create(
                    codename=action,
                    content_type=content_type,
                    defaults={
                        "name": f"{model} {action}"
                    }
                )
                user.user_permissions.add(permission)
            else:
                print(f"Não existe permissão para {model} {action}")
            user.save()


class HubJWTAuthentication(authentication.TokenAuthentication, LoginUserByCache):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        cache_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        token = HubUser.objects.filter(token__access_token=str(cache_key)).first()
        if token:
            cache.set(
                'access_token_user_id_' + str(cache_key),
                token.user_id
            )
            user_model = get_user_model()
            user = user_model.objects.get(id=token.user_id)
        else:
            hub_user = self.get_hub_user(key)
            user = self.update_or_create_user(hub_user)
            HubUser.objects.create(
                token=HubOauthToken.objects.filter(access_token=str(cache_key)).first(),
                user=user
            )

        return user, key
