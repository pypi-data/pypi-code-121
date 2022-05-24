from datetime import datetime
from typing import Iterable, Optional

from django.conf import settings

import requests

from dnoticias_services.communications.base import BaseMailRequest
from dnoticias_services.utils.request import get_headers


"""
SETTINGS:

CREATE_NOTIFICATION_API_URL
UPDATE_NOTIFICATION_API_URL
GET_NOTIFICATION_API_URL
DELETE_NOTIFICATION_API_URL
GET_NOTIFICATION_LIST_API_URL
CREATE_TOPIC_API_URL
UPDATE_TOPIC_API_URL
DELETE_TOPIC_API_URL
GET_TOPICS_SELECT2_API_URL
GET_TOPIC_LIST_API_URL
GET_TOPIC_API_URL
"""


class Notifications(BaseMailRequest):
    @classmethod
    def create_notification(
        cls,
        site_domain: str,
        object_id: str,
        content_type_id: str,
        title: str,
        body: str,
        icon_url: str,
        image_url: str,
        redirect_url_web: str,
        redirect_url_app: str,
        to_send: Optional[bool] = False,
        scheduled_for: Optional[datetime] = None, 
        topics: Optional[Iterable[str]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.CREATE_NOTIFICATION_API_URL,
            headers=get_headers(_api_key),
            json={
                "site_domain": site_domain,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "title": title,
                "body": body,
                "icon_url": icon_url,
                "image_url": image_url,
                "redirect_url_web": redirect_url_web,
                "redirect_url_app": redirect_url_app,
                "topics": topics,
                "to_send": to_send,
                "scheduled_for": scheduled_for
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def update_notification(
        cls,
        id: int,
        site_domain: str,
        object_id: str,
        content_type_id: str,
        title: str,
        body: str,
        icon_url: str,
        image_url: str,
        redirect_url_web: str,
        redirect_url_app: str,
        to_send: Optional[bool] = False,
        scheduled_for: Optional[datetime] = None, 
        topics: Optional[Iterable[str]] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.UPDATE_NOTIFICATION_API_URL.format(notification_id=id),
            headers=get_headers(_api_key),
            json={
                "site_domain": site_domain,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "title": title,
                "body": body,
                "icon_url": icon_url,
                "image_url": image_url,
                "redirect_url_web": redirect_url_web,
                "redirect_url_app": redirect_url_app,
                "topics": topics,
                "to_send": to_send,
                "scheduled_for": scheduled_for
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_notification(
        cls,
        notification_id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.get(
            settings.GET_NOTIFICATION_API_URL.format(notification_id=notification_id),
            headers=get_headers(_api_key),
            json={
                "notification_id": notification_id,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def delete_notification(
        cls,
        object_id: int,
        content_type_id: int,
        site_domain: str,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.delete(
            settings.DELETE_NOTIFICATION_API_URL,
            headers=get_headers(_api_key),
            json={
                "object_id": object_id,
                "content_type_id": content_type_id,
                "site_domain": site_domain,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_notification_list(
        cls,
        site_domain: str,
        user_requester_email: str,
        post_data: dict,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.GET_NOTIFICATION_LIST_API_URL,
            headers=get_headers(_api_key),
            json={
                "site_domain": site_domain,
                "user_requester_email": user_requester_email,
                "post_data": post_data
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def create_topic(
        cls,
        name: str,
        slug: str,
        site_domain: str,
        active: bool,
        object_id: Optional[int] = None,
        content_type_id: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.CREATE_TOPIC_API_URL,
            headers=get_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "site_domain": site_domain,
                "active": active,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def update_topic(
        cls,
        id: int,
        name: str,
        slug: str,
        site_domain: str,
        active: bool,
        object_id: Optional[int] = None,
        content_type_id: Optional[int] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.UPDATE_TOPIC_API_URL.format(topic_id=id),
            headers=get_headers(_api_key),
            json={
                "name": name,
                "slug": slug,
                "object_id": object_id,
                "content_type_id": content_type_id,
                "site_domain": site_domain,
                "active": active,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def delete_topic(
        cls,
        object_id: int,
        content_type_id: int,
        site_domain: str,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.delete(
            settings.DELETE_TOPIC_API_URL,
            headers=get_headers(_api_key),
            json={
                "object_id": object_id,
                "content_type_id": content_type_id,
                "site_domain": site_domain,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topics_select2(
        cls,
        site_domain: str,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.get(
            settings.GET_TOPICS_SELECT2_API_URL,
            headers=get_headers(_api_key),
            params={
                "site_domain": site_domain,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topic_list(
        cls,
        site_domain: str,
        user_requester_email: str,
        post_data: dict,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.post(
            settings.GET_TOPIC_LIST_API_URL,
            headers=get_headers(_api_key),
            json={
                "site_domain": site_domain,
                "user_requester_email": user_requester_email,
                "post_data": post_data
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response

    @classmethod
    def get_topic(
        cls,
        topic_id: int,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        _api_key = api_key or cls.API_KEY
        _timeout = timeout or cls.TIMEOUT

        response = requests.get(
            settings.GET_TOPIC_API_URL.format(topic_id=topic_id),
            headers=get_headers(_api_key),
            json={
                "topic_id": topic_id,
            },
            timeout=_timeout
        )
        response.raise_for_status()
        return response
