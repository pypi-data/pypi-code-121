#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Client commands"""

from enum import Enum
from typing import Dict, Optional, Text

#
# Note: client kits are Python:
#   we use original field names,
#   not camelCased aliases
from skill_sdk.utils.util import BaseModel


class KitType(Text, Enum):
    """
    Client kits available for cloud skills

    """

    AUDIO_PLAYER = "audio_player"
    CALENDAR = "calendar"
    SYSTEM = "system"
    TIMER = "timer"


class Kit(BaseModel):
    """
    Client kit

    """

    kit_name: KitType
    action: Text
    parameters: Optional[Dict]


class Command(BaseModel):
    """
    Generic client command

    """

    use_kit: Kit

    def __init__(self, kit_name, action, **kwargs):
        super().__init__(
            use_kit=Kit(kit_name=kit_name, action=action, parameters=kwargs or None)
        )


class AudioPlayer(Command):
    """
    Kit for handling audio player/radio functions

    """

    class Action(Text, Enum):
        """Available action commands"""

        PLAY_STREAM = "play_stream"
        PLAY_STREAM_BEFORE_TEXT = "play_stream_before_text"
        STOP = "stop"
        PAUSE = "pause"
        RESUME = "resume"

    class ContentType(Text, Enum):
        """Defined channel/content types"""

        RADIO = "radio"
        VOICEMAIL = "voicemail"

    def __init__(self, action, **kwargs):
        super().__init__(KitType.AUDIO_PLAYER, action, **kwargs)

    @staticmethod
    def play_stream(url: Text) -> "AudioPlayer":
        """
        Start playing a generic internet stream, specified by "url" parameter

        :param url:
        :return:
        """
        return AudioPlayer(AudioPlayer.Action.PLAY_STREAM, url=url)

    @staticmethod
    def play_stream_before_text(url: Text) -> "AudioPlayer":
        """
        Start playing a stream, before pronouncing the response

        :param url:
        :return:
        """
        return AudioPlayer(AudioPlayer.Action.PLAY_STREAM_BEFORE_TEXT, url=url)

    @staticmethod
    def stop(content_type: ContentType = None, text: Text = None) -> "AudioPlayer":
        """
        Stop currently playing media (voicemail, radio, content tts),
            optionally say text BEFORE stopping

        :param content_type:
        :param text:
        :return:
        """
        content_type = content_type or AudioPlayer.ContentType.RADIO
        text = text or ""

        return AudioPlayer(
            AudioPlayer.Action.STOP,
            content_type=content_type,
            notify=dict(not_playing=text),
        )

    @staticmethod
    def pause(content_type: ContentType = None, text: Text = None) -> "AudioPlayer":
        """
        Pause playback, optionally say text AFTER playback paused

        :param content_type:
        :param text:
        :return:
        """
        content_type = content_type or AudioPlayer.ContentType.RADIO
        text = text or ""

        return AudioPlayer(
            AudioPlayer.Action.PAUSE,
            content_type=content_type,
            notify=dict(not_playing=text),
        )

    @staticmethod
    def resume(content_type: ContentType = None) -> "AudioPlayer":
        """
        Resume paused media, say response text before resuming

        :param content_type:
        :return:
        """
        content_type = content_type or AudioPlayer.ContentType.RADIO

        return AudioPlayer(AudioPlayer.Action.RESUME, content_type=content_type)


class Calendar(Command):
    """
    Calendar kit: snooze calendar alarm, cancel snooze

    """

    class Action(Text, Enum):
        """Available action commands"""

        SNOOZE_START = "snooze_start"
        SNOOZE_CANCEL = "snooze_cancel"

    def __init__(self, action, **kwargs):
        super().__init__(KitType.CALENDAR, action, **kwargs)

    @staticmethod
    def snooze_start(snooze_seconds: int = None) -> "Calendar":
        """
        Snooze calendar alarm by optional number of seconds

        :param snooze_seconds:
        :return:
        """
        return Calendar(Calendar.Action.SNOOZE_START, snooze_seconds=snooze_seconds)

    @staticmethod
    def snooze_cancel() -> "Calendar":
        """
        Cancel current snooze

        :return:
        """
        return Calendar(Calendar.Action.SNOOZE_CANCEL)


class System(Command):
    """
    System functions kit

    """

    class Action(Text, Enum):
        """Available action commands"""

        STOP = "stop"
        PAUSE = "pause"
        RESUME = "resume"
        NEXT = "next"
        PREVIOUS = "previous"
        SAY_AGAIN = "say_again"
        VOLUME_UP = "volume_up"
        VOLUME_DOWN = "volume_down"
        VOLUME_TO = "volume_to"

    class SkillType(Text, Enum):
        """Defined channel/skill types"""

        TIMER = "Timer"
        CONVERSATION = "Conversation"
        MEDIA = "Media"

    def __init__(self, action, **kwargs):
        super().__init__(KitType.SYSTEM, action, **kwargs)

    @staticmethod
    def stop(skill_type: SkillType = None) -> "System":
        """
        Send a `Stop` event: stops a foreground activity on the device.
        If there was another activity in background, it will gain focus.

        :param skill_type:  Stop a skill-related activity, or everything, if no skill specified
        :return:
        """
        return System(System.Action.STOP, skill=skill_type)

    @staticmethod
    def pause() -> "System":
        """
        Pause currently active content (if supported)

        :return:
        """
        return System(System.Action.PAUSE)

    @staticmethod
    def resume() -> "System":
        """
        Resume media (if paused)

        :return:
        """
        return System(System.Action.RESUME)

    @staticmethod
    def next() -> "System":
        """
        Switch to next item in content channel

        :return:
        """
        return System(System.Action.NEXT)

    @staticmethod
    def previous() -> "System":
        """
        Switch to previous item in content channel

        :return:
        """
        return System(System.Action.PREVIOUS)

    @staticmethod
    def say_again() -> "System":
        """
        Repeat last uttered sentence (from the dialog channel)

        :return:
        """
        return System(System.Action.SAY_AGAIN)

    @staticmethod
    def volume_up() -> "System":
        """
        Increase the volume one notch

        :return:
        """
        return System(System.Action.VOLUME_UP)

    @staticmethod
    def volume_down() -> "System":
        """
        Decrease the volume one notch

        :return:
        """
        return System(System.Action.VOLUME_DOWN)

    @staticmethod
    def volume_to(value: int = 0) -> "System":
        """
        Set the volume to an absolute value (0-10)

        :return:
        """
        if value not in range(10):
            raise ValueError("Value %s in not in expected range (0 - 10)", repr(value))

        return System(System.Action.VOLUME_TO, value=value)


class Timer(Command):
    """
    Timer kit: start/stop Timer/Reminder/Alarm animation

        After animation started, it keeps running for max. 10 min if no user interaction happens

    """

    class Action(Text, Enum):
        """Available action commands"""

        SET_TIMER = "set_timer"
        CANCEL_TIMER = "cancel_timer"

    def __init__(self, action, **kwargs):
        super().__init__(KitType.TIMER, action, **kwargs)

    @staticmethod
    def set_timer():
        """
        Fire up a "timer" animation

        :return:
        """
        return Timer(Timer.Action.SET_TIMER)

    @staticmethod
    def cancel_timer():
        """
        Cancel currently running "timer"

        :return:
        """
        return Timer(Timer.Action.CANCEL_TIMER)
