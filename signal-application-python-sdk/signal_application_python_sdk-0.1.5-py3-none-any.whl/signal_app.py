import os
import logging
from signalsdk.shadow_client import OnConfigurationChangeRequested, ShadowClient
from signalsdk.iot_mqtt_connection import IotMqttConnection
from signalsdk.local_mqtt import OnEventReceived, LocalMqtt
from signalsdk.api import get_local_config
from signalsdk.application_config import get_config_for_app
from signalsdk.signal_exception import SignalAppCallBackError, SignalAppConfigEnvError, \
    SignalAppInitError, SignalDeviceDomainNotFoundError, \
    SignalDeploymentNotFoundError

class SignalApp:
    def __init__(self):
        self.iotMqttConnection = None
        self.shadow_client = None
        self.localMqtt = None
        self.appConfig = {}
        self.appSettings = {}
        self.app_id = ""
        self.thing_name = ""
        self.account_id = ""
        self.deviceDeploymentVersion = None
        self.deviceDeploymentId = None
        self.groupDeploymentVersion = None
        self.groupDeploymentId = None
        self.deviceApiDomainName = None
        self.configurationChangedCallback = None
        self.onEventReceivedCallback = None

    def on_config_change_requested(self, delta):
        logging.info(f"signalsdk: configuration change received: "
                     f"{str(delta)}")

        self.deviceApiDomainName = delta.get("deviceApiDomainName") or self.deviceApiDomainName
        logging.info(f"signalsdk::deviceApiDomainName: {self.deviceApiDomainName}")

        if not self.deviceApiDomainName:
            raise SignalDeviceDomainNotFoundError

        self.deviceDeploymentVersion = delta.get("deploymentVersion")
        logging.info(f"signalsdk::device deploymentVersion: {self.deviceDeploymentVersion}")
        # if deployment version is null then it means
        # deployment does not exist at all/is deleted
        if not self.deviceDeploymentVersion:
            self.deviceDeploymentId = None
        else:
            self.deviceDeploymentId = delta.get("deploymentId") or self.deviceDeploymentId
            logging.info(f"signalsdk::device deploymentId: {self.deviceDeploymentId}")

        self.groupDeploymentVersion = delta.get("groupDeploymentVersion")
        logging.info(f"signalsdk::group deploymentVersion: {self.groupDeploymentVersion}")
        # if group deployment version is null then it means
        # group deployment does not exist at all/is deleted
        if not self.groupDeploymentVersion:
            self.groupDeploymentId = None
        else:
            self.groupDeploymentId = delta.get("groupDeploymentId") or self.groupDeploymentId
            logging.info(f"signalsdk::group deploymentId: {self.groupDeploymentId}")

        if not self.deviceDeploymentId and not self.groupDeploymentId:
            raise SignalDeploymentNotFoundError

        self.appSettings = get_config_for_app(self.deviceDeploymentId,
                                              self.groupDeploymentId,
                                              self.account_id,
                                              self.app_id,
                                              self.deviceApiDomainName)

        if "sdkSubTopic" in self.appSettings["settingsForSDK"] and \
            self.appSettings["settingsForSDK"]["sdkSubTopic"] != {}:
            desired_subtopic = self.appSettings["settingsForSDK"]["sdkSubTopic"]
            current_subtopic = self.localMqtt.get_subscribed_topic()
            self.renew_topic_subscription(current_subtopic, desired_subtopic)

        if self.appSettings["settingsForApp"] != {}:
            try:
                self.configurationChangedCallback(self.appSettings["settingsForApp"])
            except Exception as err:
                logging.info(f"signalsdk: configurationChangedCallback "
                             f"function threw an error: {err}")
                raise SignalAppCallBackError from err
        else:
            self.report_configuration_change()

    def initialize(self, onConfiguratioChangedCallback: OnConfigurationChangeRequested,
                   onEventReceivedCallback: OnEventReceived):
        """Signal Application Initialize
        Following objects are created
        localMqtt: it is used to subscribe or publish to local MQTT broker
        served as local event bus
        iotMqttConnection: it is used subscribe or publish device
        shadow configuration topics
        shadow_client: it listens to device shadow change topic and trigger
        local updates and reports

        :param application_type:
        :param onConfiguratioChangedCallback: call back function provided by
        signal application for configuration change
        :param onEventReceivedCallback: call back function provided by signal
        application for events handling
        """
        logging.info("signalsdk::Starting signal app initialize.")
        self.configurationChangedCallback = onConfiguratioChangedCallback
        self.onEventReceivedCallback = onEventReceivedCallback
        self.appConfig = get_local_config()
        self.thing_name = self.appConfig['thingName']
        self.account_id = self.appConfig['accountId']
        self.app_id = os.getenv('APPLICATION_ID')
        self.shadow_client = None
        if not self.app_id:
            raise SignalAppConfigEnvError

        self.localMqtt = LocalMqtt()
        self.localMqtt.set_on_event_received(self.onEventReceivedCallback)
        self.localMqtt.connect()

        self.iotMqttConnection = IotMqttConnection(self.app_id, self.appConfig)
        self.iotMqttConnection.set_on_connection_successful(
            self.start_listening_configuration_updates)
        self.iotMqttConnection.connect()
        return self.iotMqttConnection

    def start_listening_configuration_updates(self):
        logging.info("signalsdk:IoT Connected. Starting to listen configuration updates...")
        if not self.shadow_client:
            self.shadow_client = ShadowClient(self.iotMqttConnection, self.thing_name)
            logging.info("signalsdk:Shadow client created")
        self.shadow_client.set_on_configuration_change_requested(self.on_config_change_requested)
        self.shadow_client.get_application_config()
        self.shadow_client.start_listening_device_shadow()

    def next(self, event):
        """Publish the event
        :param event:
        :return:
        """
        if 'settingsForSDK' not in self.appSettings:
            logging.info(f"signalsdk: settingForSDK not exists: {self.appSettings}"
                         f"event: {event} ")
            return
        logging.info(f"signalsdk: forwarding event to topic: "
                     f"{self.appSettings['settingsForSDK']} "
                     f"event: {event}")

        if not self.shadow_client:
            logging.error("signalsdk: shadow client is not created")
            raise SignalAppInitError
        if 'sdkPubTopic' in self.appSettings['settingsForSDK'] and \
                self.appSettings['settingsForSDK'] != {}:
            logging.info(f"signalsdk next() publishing sdk config: "
                         f"{self.appSettings['settingsForSDK']}")
            self.localMqtt.publish(self.appSettings['settingsForSDK']['sdkPubTopic'], event)
        else:
            logging.info("signalsdk next() called but no publish topic found in sdk config")

    def report_configuration_change(self):
        logging.info("signalsdk: report_configuration_change")
        if not self.shadow_client:
            logging.error("signalsdk: shadow client is not created")
            raise SignalAppInitError
        to_report = {}
        if self.deviceDeploymentId:
            to_report["deploymentId"] = self.deviceDeploymentId
        if self.deviceDeploymentVersion:
            to_report["deploymentVersion"] = self.deviceDeploymentVersion
        if self.groupDeploymentId:
            to_report["groupDeploymentId"] = self.groupDeploymentId
        if self.groupDeploymentVersion:
            to_report["groupDeploymentVersion"] = self.groupDeploymentVersion
        to_report["deviceApiDomainName"] = self.deviceApiDomainName
        logging.info(f"signalsdk: report configuration change with: {to_report}")
        self.shadow_client.update_application_config(to_report)

    def renew_topic_subscription(self, current_topic, desired_topic):
        if current_topic and current_topic != desired_topic:
            self.localMqtt.unsubscribe()
        if desired_topic and current_topic != desired_topic:
            self.localMqtt.subscribe(desired_topic)
