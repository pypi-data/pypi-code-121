import abc
import time

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class BaseEvent(ABC):
    def __init__(self, user):
        self.timestamp = self._get_time()
        self.userId = user.id
        self.userProperties = user.properties

    # noinspection PyMethodMayBeStatic
    def _get_time(self):
        return int(round(time.time() * 1000))


class ExposureEvent(BaseEvent):
    def __init__(self, user, experiment_id, experiment_key, variation_id, variation_key):
        super(ExposureEvent, self).__init__(user)
        self.experimentId = experiment_id
        self.experimentKey = experiment_key
        self.variationId = variation_id
        self.variationKey = variation_key


class TrackEvent(BaseEvent):
    def __init__(self, user, event_type, event):
        super(TrackEvent, self).__init__(user)
        self.eventTypeId = event_type.id
        self.eventTypeKey = event_type.key
        self.value = event.value
        self.properties = event.properties
