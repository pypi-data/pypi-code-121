import abc
import time

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class UserEvent(ABC):
    def __init__(self, user):
        self.timestamp = self._get_time()
        self.userId = user.id
        self.userProperties = user.properties

    # noinspection PyMethodMayBeStatic
    def _get_time(self):
        return int(round(time.time() * 1000))


class ExposureEvent(UserEvent):
    def __init__(self, user, experiment, evaluation):
        super(ExposureEvent, self).__init__(user)
        self.experimentId = experiment.id
        self.experimentKey = experiment.key
        self.experimentType = experiment.type
        self.variationId = evaluation.variation_id
        self.variationKey = evaluation.variation_key
        self.decisionReason = evaluation.reason


class TrackEvent(UserEvent):
    def __init__(self, user, event_type, event):
        super(TrackEvent, self).__init__(user)
        self.eventTypeId = event_type.id
        self.eventTypeKey = event_type.key
        self.value = event.value
        self.properties = event.properties
