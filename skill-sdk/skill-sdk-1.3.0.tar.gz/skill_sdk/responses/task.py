#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Client tasks (delayed or scheduled)"""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Text, Union

import isodate
from skill_sdk.utils.util import CamelModel


class ReferenceType(Text, Enum):
    """
    Reference event for the execution

        SPEECH_END - end of vocalization of the current response.
        THIS_RESPONSE - immediately after reception of the current response by the touchpoint
        MEDIA_CONTENT_END - end of output of a media content attached to the current response, e.g. an audio stream

    """

    SPEECH_END = "SPEECH_END"
    THIS_RESPONSE = "THIS_RESPONSE"
    MEDIA_CONTENT_END = "MEDIA_CONTENT_END"


class ExecuteAfter(CamelModel):
    """Command is executed after speech end with optional offset"""

    reference: ReferenceType = ReferenceType.SPEECH_END

    # Positive offset relative to reference given as duration
    offset: Optional[Text] = None


class ExecutionTime(CamelModel):
    """
    Exported as timestamp in ISO-8601 format, e.g. 2020-11-25T12:00:00Z
    """

    # Relative execution time
    execute_after: Optional[ExecuteAfter] = None

    # Absolute execution time
    execute_at: Optional[Text] = None

    @staticmethod
    def at(time: datetime.datetime) -> "ExecutionTime":
        return ExecutionTime(execute_at=time.isoformat())

    @staticmethod
    def after(
        event: ReferenceType = ReferenceType.SPEECH_END,
        offset: datetime.timedelta = datetime.timedelta(0),
    ) -> "ExecutionTime":
        return ExecutionTime(
            execute_after=ExecuteAfter(
                reference=event, offset=isodate.duration_isoformat(offset)
            )
        )


class InvokeData(CamelModel):
    """Intent invoke data: name, skill and parameters"""

    # Intent name
    intent: Text

    # Skill Id
    skill_id: Optional[Text] = None

    # Parameters (will be converted to intent invoke attributes)
    parameters: Dict[Text, List[Text]] = {}


class DelayedClientTask(CamelModel):
    """
    Delayed (postponed or scheduled) task, that client executes upon receiving this response
    Standard use case is to invoke an intent after speech end

    """

    # Invoke data
    invoke_data: InvokeData

    # Invoke execution time (default - right after speech end)
    execution_time: ExecutionTime

    @staticmethod
    def invoke(
        intent: Text, skill_id: Text = None, **kwargs: Union[Text, List[Text]]
    ) -> "DelayedClientTask":
        """
        Create a task to invoke intent

            Execute "WEATHER__INTENT" in 10 seconds after speech end:
            >>>         response = Response("Weather forecast for Bonn in 10 seconds.").with_task(
            >>>             ClientTask.invoke("WEATHER__INTENT", location=["Bonn"])
            >>>                 .after(offset=datetime.timedelta(seconds=10))
            >>>         )


        :param intent:      Intent name to invoke
        :param skill_id:    Optional skill Id
        :param kwargs:      Parameters: wey/values map converted into attributes for skill invocation
        :return:
        """
        parameters: Dict[Text, List[Text]] = {
            k: [v] if isinstance(v, Text) else v for k, v in kwargs.items()
        }
        invoke_data = InvokeData(
            intent=intent, skill_id=skill_id, parameters=parameters
        )
        execution_time = ExecutionTime.after(ReferenceType.SPEECH_END)

        return DelayedClientTask(invoke_data=invoke_data, execution_time=execution_time)

    def at(self, time: datetime.datetime) -> "DelayedClientTask":
        """
        Schedule the task execution to particular time point

            Excetute the task in 10 seconds:
            >>> task.at(datetime.datetime.now() + datetime.timedelta(seconds=10))

        :param time:    Time point to execute the task
        :return:
        """
        return self.copy(update=dict(execution_time=ExecutionTime.at(time)))

    def after(
        self,
        event: ReferenceType = ReferenceType.SPEECH_END,
        offset: datetime.timedelta = datetime.timedelta(0),
    ) -> "DelayedClientTask":
        """
        Delay the task execution AND/OR change the reference point type

            Schedule the task to execute BEFORE speech starts:
            >>> task.after(ReferenceType.THIS_RESPONSE)

            To delay task execution by 10 seconds after speech ends:
            >>> task.after(ReferenceType.SPEECH_END, datetime.timedelta(seconds=10))

        :param event:   even reference type (SPEECH_END - after speech ends, THIS_RESPONSE - before speech starts)
        :param offset:  offset timedelta
        :return:
        """
        return self.copy(
            update=dict(execution_time=ExecutionTime.after(event=event, offset=offset))
        )


ClientTask = DelayedClientTask
