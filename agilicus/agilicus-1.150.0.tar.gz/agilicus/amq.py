import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import json

from .input_helpers import get_org_from_input_or_ctx
from .context import get_cacert, get_api, get_token, is_admin


def on_connect(ctx, mqttc, obj, flags, rc):
    if rc != 0:
        return "failed to connect"
    # grab the token (in case it has expired), and set the password
    token = get_token(ctx)
    mqttc.username_pw_set("agilicus-cli", password=token)


def on_message(ctx, mqttc, obj, msg):
    result = {}
    api_obj = json.loads(msg.payload)
    result[msg.topic] = api_obj
    print(json.dumps(result))


def on_subscribe(mqttc, obj, mid, granted_qos):
    pass


def subscribe(ctx, routing_key=None, org_id=None, **kwargs):
    cert = get_cacert(ctx)
    token = get_token(ctx)
    org_id = get_org_from_input_or_ctx(ctx, org_id)

    url = urlparse(get_api(ctx))

    mqttc = mqtt.Client(transport="websockets")
    headers = {}
    headers["Host"] = url.hostname

    mqttc.ws_set_options(path="/mqtt", headers=headers)
    mqttc.tls_set(ca_certs=cert)

    def on_message_with_ctx(*args, **kwargs):
        return on_message(ctx, *args, **kwargs)

    def on_connect_with_ctx(*args, **kwargs):
        return on_connect(ctx, *args, **kwargs)

    mqttc.on_message = on_message_with_ctx
    mqttc.on_connect = on_connect_with_ctx
    mqttc.on_subscribe = on_subscribe

    mqttc.username_pw_set("agilicus-cli", password=token)
    mqttc.connect(url.hostname, port=443, keepalive=30)

    if routing_key is None:
        if is_admin(ctx):
            routing_key = "org/#"
        else:
            routing_key = f"org/{org_id}/#"

    mqttc.subscribe(routing_key)
    mqttc.loop_forever()
