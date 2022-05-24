"""signalsdk
signalsdk module provide interface for signal applications to interact with
Teldio Signal platform.

Initialize SDK: Entry point for Signal Application SDK
* Creates a bi-directional communication between device shadow and application

initialize(applicationType: string,
     onConfigurationChangeRequestedCallback: OnConfigurationChangeRequested,
     onEventReceivedCallback: OnEventReceived)

Pass event to the next entity by sending an event to a designated topic
next(event: string)

signal application send report when configuration change is applied
reportConfigurationChange(event: object)

callback method used to handle configuration change when requested from the cloud
* Triggered when a new configuration change requested from the cloud
onConfigurationChangeRequested(newConfig: object)

callback method used to handle the events received from event bus
* Triggered when a new event received from application's subscribed topic
onEventReceived(event: object)

"""
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
print("package initialized.")
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
