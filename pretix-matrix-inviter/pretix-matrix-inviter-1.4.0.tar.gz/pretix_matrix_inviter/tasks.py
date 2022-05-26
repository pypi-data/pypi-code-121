import logging
import requests
from celery.exceptions import MaxRetriesExceededError
from pretix.base.models import Order, OrderPosition
from pretix.base.services.tasks import ProfiledEventTask
from pretix.celery_app import app
from urllib.parse import quote as url_quote

from .helpers import matrix_room_id

logger = logging.getLogger(__name__)


@app.task(
    base=ProfiledEventTask,
    bind=True,
    max_retries=10,
    retry_backoff=True,
    retry_backoff_max=3600,
)
def matrix_inviter_invite(
    self, event: int, order: int, order_position: int, invitation_reason: str
):
    order_position = OrderPosition.objects.get(pk=order_position)

    user_matrix_id = order_position.meta_info_data.get("question_form_data", {}).get(
        "matrix_inviter_matrix_id"
    )

    if not user_matrix_id:
        return

    order = Order.objects.get(pk=order)
    server = event.settings.matrix_inviter_matrix_server
    token = event.settings.matrix_inviter_authorization_token
    room_id = matrix_room_id(server, event.settings.matrix_inviter_matrix_room)
    payload = {"user_id": user_matrix_id}
    if invitation_reason:
        payload["reason"] = invitation_reason

    try:
        r = requests.post(
            "https://{}/_matrix/client/v3/rooms/{}/invite".format(
                url_quote(server),
                url_quote(room_id),
            ),
            headers={
                "Authorization": "Bearer {}".format(token),
            },
            json=payload,
        )
        r.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as e:
        if r.status_code in (400, 403):
            order.log_action(
                "pretix_matrix_inviter.error",
                data={
                    "matrix_id": user_matrix_id,
                    "matrix_room": room_id,
                    "error": "HTTP Code {} ({})".format(
                        r.status_code, r.json()["error"]
                    ),
                },
            )
        else:
            try:
                if r.status_code == 429:
                    backoff = r.json()["retry_after_ms"] / 1000
                    self.retry(countdown=backoff)
                else:
                    self.retry()
            except MaxRetriesExceededError:
                order.log_action(
                    "pretix_matrix_inviter.error",
                    data={
                        "matrix_id": user_matrix_id,
                        "matrix_room": room_id,
                        "error": "HTTP Code {}".format(r.status_code),
                    },
                )
                raise e
    else:
        order.log_action(
            "pretix_matrix_inviter.invite_sent",
            data={
                "matrix_id": user_matrix_id,
                "matrix_room": room_id,
            },
        )


@app.task(
    base=ProfiledEventTask,
    bind=True,
    max_retries=10,
    retry_backoff=True,
    retry_backoff_max=3600,
)
def matrix_inviter_kick(self, event: int, order: int, order_position: int):
    order_position = OrderPosition.objects.get(pk=order_position)

    user_matrix_id = order_position.meta_info_data.get("question_form_data", {}).get(
        "matrix_inviter_matrix_id"
    )

    if not user_matrix_id:
        return

    order = Order.objects.get(pk=order)
    server = event.settings.matrix_inviter_matrix_server
    token = event.settings.matrix_inviter_authorization_token
    room_id = matrix_room_id(server, event.settings.matrix_inviter_matrix_room)
    payload = {"user_id": user_matrix_id}

    try:
        r = requests.post(
            "https://{}/_matrix/client/v3/rooms/{}/kick".format(
                url_quote(server),
                url_quote(room_id),
            ),
            headers={
                "Authorization": "Bearer {}".format(token),
            },
            json=payload,
        )
        r.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as e:
        if r.status_code in (403):
            order.log_action(
                "pretix_matrix_inviter.remove_error",
                data={
                    "matrix_id": user_matrix_id,
                    "matrix_room": room_id,
                    "error": "HTTP Code {} ({})".format(
                        r.status_code, r.json()["error"]
                    ),
                },
            )
        else:
            try:
                if r.status_code == 429:
                    backoff = r.json()["retry_after_ms"] / 1000
                    self.retry(countdown=backoff)
                else:
                    self.retry()
            except MaxRetriesExceededError:
                order.log_action(
                    "pretix_matrix_inviter.remove_error",
                    data={
                        "matrix_id": user_matrix_id,
                        "matrix_room": room_id,
                        "error": "HTTP Code {}".format(r.status_code),
                    },
                )
                raise e
    else:
        order.log_action(
            "pretix_matrix_inviter.invite_rescinded",
            data={
                "matrix_id": user_matrix_id,
                "matrix_room": room_id,
            },
        )
