import logging
from typing import Callable
from awscrt.mqtt import QoS
from awsiot import iotshadow
from signalsdk.iot_mqtt_connection import IotMqttConnection

OnConfigurationChangeRequested=Callable[[object], None]

class ShadowClient:
    """IoT device shadow client
    it is responsible of communication with device shadow on configuration changes

    """
    def __init__(self, iot_mqtt_connection: IotMqttConnection, thingName):
        self.shadow_client = iotshadow.IotShadowClient(iot_mqtt_connection.get_connection())
        self.configuration_changed_callback = None
        self.shadowName = 'applications-shadow'
        self.thingName = thingName

    def set_on_configuration_change_requested(self, callback: OnConfigurationChangeRequested):
        self.configuration_changed_callback = callback

    def on_named_shadow_delta_updated(self, response: iotshadow.ShadowDeltaUpdatedEvent):
        logging.info(f"signalsdk::{__name__}:on_named_shadow_delta_updated. "
                     f"Triggering callback. Response: {response.state} "
                     f"Type:{type(response.state)}")
        self.configuration_changed_callback(response.state)

    def on_named_shadow_updated(self, response: iotshadow.ShadowUpdatedEvent):
        logging.info(f"signalsdk::{__name__}:on_named_shadow_updated. {response}")

    def on_update_named_shadow_accepted(self, response: iotshadow.UpdateShadowResponse):
        logging.info(f"signalsdk::{__name__}:on_update_named_shadow_accepted. "
                     f"Current config: {response}")

    def on_update_named_shadow_rejected(self, response: iotshadow.ErrorResponse):
        logging.info(f"{__name__}:on_update_named_shadow_rejected. "
                     f"Current config: {response}")

    def on_get_named_shadow_accepted(self, response: iotshadow.GetShadowResponse):
        logging.info(f"signalsdk::{__name__}:on_get_named_shadow_accepted. "
                     f"Triggering callback. Response: {response.state} "
                     f"Type:{type(response.state)}")
        delta = response.state.desired
        self.configuration_changed_callback(delta)

    def on_get_named_shadow_rejected(self, response: iotshadow.ErrorResponse):
        logging.warning(f"signalsdk::{__name__}:on_get_named_shadow_rejected. "
                     f"Response: {response}")

    def on_publish_update_named_shadow(self, future):
        # type: (Future) -> None
        try:
            future.result()
            logging.info("signalsdk::Update named shadow published.")
        except Exception as e:
            logging.error(f"signalsdk::Failed to publish update named shadow request. Error: {e}")

    def start_listening_device_shadow(self):
        logging.info(f"signalsdk::{__name__}:start_listening_device_shadow. "
                     f"thing_name:{self.thingName} shadow_name:{self.shadowName}")
        delta_updated_subscribed_future, _ = \
            self.shadow_client.subscribe_to_named_shadow_delta_updated_events(
            request=iotshadow.NamedShadowDeltaUpdatedSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_named_shadow_delta_updated
            )
        delta_updated_subscribed_future.result()

        shadow_updated_subscribed_future, _ = \
            self.shadow_client.subscribe_to_named_shadow_updated_events(
            request=iotshadow.NamedShadowUpdatedSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_named_shadow_updated
        )
        shadow_updated_subscribed_future.result()

        update_accepted_subscribed_future, _ = \
            self.shadow_client.subscribe_to_update_named_shadow_accepted(
            request=iotshadow.UpdateNamedShadowSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_update_named_shadow_accepted
        )
        update_accepted_subscribed_future.result()

        update_rejected_subscribed_future, _ = \
            self.shadow_client.subscribe_to_update_named_shadow_rejected(
            request=iotshadow.UpdateNamedShadowSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_update_named_shadow_rejected
        )
        update_rejected_subscribed_future.result()

    def get_application_config(self):
        logging.info(f"signalsdk::{__name__}:get_application_config. "
                     f"thing_name:{self.thingName} shadow_name:{self.shadowName}")
        get_accepted_subscribed_future, _ = \
            self.shadow_client.subscribe_to_get_named_shadow_accepted(
            request=iotshadow.GetNamedShadowSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_get_named_shadow_accepted
            )
        get_accepted_subscribed_future.result()
        logging.info("signalsdk::subscribed to get_named_shadow_accepted")

        get_rejected_subscribed_future, _ = \
            self.shadow_client.subscribe_to_get_named_shadow_rejected(
            request=iotshadow.GetNamedShadowSubscriptionRequest(
                thing_name=self.thingName, shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE,
            callback=self.on_get_named_shadow_rejected
        )
        get_rejected_subscribed_future.result()
        logging.info("signalsdk::subscribed to get_named_shadow_rejected")

        publish_get_future = self.shadow_client.publish_get_named_shadow(
            request=iotshadow.GetNamedShadowRequest(thing_name=self.thingName,
                                                    shadow_name=self.shadowName),
            qos=QoS.AT_LEAST_ONCE
        )
        publish_get_future.result()
        logging.info("signalsdk::published get_named_shadow")

    def update_application_config(self, config):
        logging.info(f"signalsdk::{__name__}:update_application_config. "
                     f"thing_name:{self.thingName} shadow_name:{self.shadowName}")
        publish_update_future = self.shadow_client.publish_update_named_shadow(
            request=iotshadow.UpdateNamedShadowRequest(
                thing_name=self.thingName,
                shadow_name=self.shadowName,
                state=iotshadow.ShadowState(reported=config)),
            qos=QoS.AT_LEAST_ONCE
            )
        publish_update_future.add_done_callback(self.on_publish_update_named_shadow)
