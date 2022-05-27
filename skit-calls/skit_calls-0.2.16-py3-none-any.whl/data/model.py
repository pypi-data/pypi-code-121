import json
import os
from collections import namedtuple
from datetime import datetime
from typing import Any, Dict, List, Tuple
from urllib.parse import unquote, urljoin

import attr

from skit_calls import constants as const

MaybeString = str | None
MaybeFloat = float | None
Thing = Dict[str, Any]
Things = List[Thing] | None

IntentName = MaybeString
IntentScore = MaybeFloat
Slots = Things
Entities = Things
Utterances = Things


def prediction2intent(prediction: Thing) -> Tuple[IntentName, IntentScore, Slots]:
    intents = prediction.get(const.INTENTS, [])
    if not intents:
        return None, None, []
    intent, *_ = intents
    return intent[const.NAME], intent[const.SCORE], intent[const.SLOTS]


def slots2entities(slots: Slots) -> Entities:
    return [entity for slot in slots for entity in slot.get(const.VALUES, [])]


def jsonify_utterances(json_string: MaybeString) -> Thing | None:
    if not json_string:
        return None
    utterances = json.loads(json_string)
    if isinstance(utterances, list) and utterances:
        if all(isinstance(utterance, list) for utterance in utterances):
            return utterances
        if all(isinstance(utterance, dict) for utterance in utterances):
            return [utterances]
    return None


def jsonify_maybestr(json_string: MaybeString) -> Thing | None:
    if not json_string:
        return None
    if isinstance(json_string, dict):
        return json_string
    return json.loads(json_string)


def float_maybestr(string: MaybeString) -> MaybeFloat:
    if not string:
        return None
    return float(string)


def print_floats(val: MaybeFloat) -> str:
    return f"{val:.2f}" if val else "None"


def print_utterance(utterances: Utterances) -> str:
    if not utterances:
        return "None"
    return utterances[0][0][const.TRANSCRIPT]


def get_call_url(
    base: MaybeString, path: MaybeString, extension: MaybeString = None
) -> MaybeString:
    if not path:
        return None
    return urljoin(os.path.join(base, ""), unquote(path).lstrip("/")) + extension


def get_url(base: MaybeString, path: MaybeString) -> MaybeString:
    return urljoin(os.path.join(base, ""), unquote(path).lstrip("/"))


@attr.s(slots=True, weakref_slot=False)
class Turn:
    call_id: str = attr.ib(kw_only=True, repr=True, converter=str)
    call_uuid: str = attr.ib(kw_only=True, repr=False)
    conversation_id: int = attr.ib(kw_only=True, repr=True, converter=int)
    conversation_uuid: str = attr.ib(kw_only=True, repr=False)
    audio_url: str = attr.ib(kw_only=True, repr=False)
    reftime: str = attr.ib(kw_only=True, converter=datetime.isoformat, repr=False)
    state: str = attr.ib(kw_only=True, repr=False)

    utterances: Utterances = attr.ib(
        kw_only=True, factory=list, converter=jsonify_utterances, repr=print_utterance
    )
    context: Thing | None = attr.ib(
        kw_only=True, factory=dict, converter=jsonify_maybestr, repr=False
    )
    intents_info: Things = attr.ib(
        kw_only=True, factory=list, converter=jsonify_maybestr, repr=False
    )

    prediction: Thing = attr.ib(
        kw_only=True, factory=dict, converter=jsonify_maybestr, repr=False
    )

    intent: IntentName = attr.ib(kw_only=True, default=None)
    intent_score: IntentScore = attr.ib(kw_only=True, default=None, repr=print_floats)
    slots: Slots = attr.ib(kw_only=True, factory=list, repr=False)
    entities: Entities = attr.ib(kw_only=True, factory=list, repr=False)

    call_url: MaybeString = attr.ib(kw_only=True, repr=False, default=None)
    language: MaybeString = attr.ib(kw_only=True, default=None)
    asr_provider: MaybeString = attr.ib(kw_only=True, default=None, repr=False)
    virtual_number: MaybeString = attr.ib(kw_only=True, default=None, repr=False)
    flow_version: MaybeString = attr.ib(kw_only=True, default=None, repr=False)

    asr_latency: MaybeFloat = attr.ib(
        kw_only=True, default=None, converter=float_maybestr, repr=False
    )
    slu_latency: MaybeFloat = attr.ib(
        kw_only=True, default=None, converter=float_maybestr, repr=False
    )
    call_duration: MaybeFloat = attr.ib(
        kw_only=True, default=None, converter=float_maybestr, repr=False
    )

    @classmethod
    def from_record(cls, record: namedtuple):
        intent_name, intent_score, slots = prediction2intent(record.prediction)
        entities = slots2entities(slots)
        call_url = record.call_url or get_call_url(
            os.environ[const.CDN_RECORDINGS_BASE_PATH],
            record.call_url_id,
            const.WAV_FILE,
        )
        audio_url = get_url(record.turn_audio_base_path, record.turn_audio_path)
        return cls(
            call_id=record.call_id,
            call_uuid=record.call_uuid,
            conversation_id=record.conversation_id,
            conversation_uuid=record.conversation_uuid,
            audio_url=audio_url,
            call_url=call_url,
            reftime=record.reftime,
            state=record.state,
            prediction=record.prediction,
            utterances=record.utterances,
            context=record.context,
            intents_info=record.intents_info,
            intent=intent_name,
            intent_score=intent_score,
            slots=slots,
            entities=entities,
            language=record.language,
            asr_latency=record.asr_latency,
            slu_latency=record.slu_latency,
            asr_provider=record.asr_provider,
            virtual_number=record.virtual_number,
            flow_version=record.flow_version,
            call_duration=record.call_duration,
        )

    def serialize(self, _, __, value):
        return (
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, (dict, list))
            else value
        )

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self, value_serializer=self.serialize)
