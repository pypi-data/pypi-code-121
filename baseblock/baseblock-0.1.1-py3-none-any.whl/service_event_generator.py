#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generate a Service Event for Activity Provenance """


from datetime import datetime


from baseblock import Stopwatch
from baseblock import Enforcer
from baseblock import BaseObject


class ServiceEventGenerator(BaseObject):
    """ Generate a Service Event for Activity Provenance """

    def __init__(self):
        """ Change History

        Created:
            9-Apr-2022
            craig@grafflr.ai
            *   https://github.com/grafflr/graffl-core/issues/278
        """
        BaseObject.__init__(self, __name__)

    def process(self,
                service_name: str,
                event_name: str,
                stopwatch: Stopwatch,
                data: dict) -> dict:
        """ Generate a Service Event

        Reference:
            https://github.com/grafflr/graffl-core/issues/278#issuecomment-1094174053

        Args:
            service_name (str): The name of the Python Service that generated this event.
            event_name (str): The name of this event.
                The service name and event name should be differentiated. 
                It is possible a service may generate multiple events.
            stopwatch (Stopwatch): Represents the time cost for the service
            data (dict): The actual event data
                Beyond that this is a dictionary, the contents of this will not be validated

        Returns:
            dict: _description_
        """

        timestamp = float(datetime.timestamp(datetime.now()))

        if self.isEnabledForDebug:
            Enforcer.is_str(service_name)
            Enforcer.is_str(event_name)
            Enforcer.is_float(timestamp)
            Enforcer.is_dict(data)
            assert len(data)

        return {
            'service': service_name,
            'event': event_name,
            'ts': timestamp,
            'stopwatch': str(stopwatch),
            'data': data,
        }
