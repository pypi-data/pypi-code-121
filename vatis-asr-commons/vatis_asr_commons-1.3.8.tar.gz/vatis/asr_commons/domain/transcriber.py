import numpy as np

from typing import List, Tuple, Optional, Type, ClassVar


class DataPacket:
    def __init__(self, headers=None):
        self.headers = {} if headers is None else headers.copy()

    def get_header(self, name, default=None, dtype: Type = str):
        if name not in self.headers:
            return default

        if default is not None:
            dtype = type(default)

        if dtype == bool:
            return str(self.headers.get(name)) == 'True'
        else:
            return dtype(self.headers.get(name))

    def set_header(self, name, value):
        self.headers[name] = value

    def __str__(self):
        return f'"headers": {str(self.headers)}'

    def __repr__(self):
        return self.__str__()


class StringPacket(DataPacket):
    def __init__(self, data: str, headers=None):
        super().__init__(headers)
        self.data = data

    def __str__(self):
        return f'{{"data": {self.data}, {super().__str__()}}}'


class ByteDataPacket(DataPacket):
    def __init__(self, data: bytes, headers=None):
        super().__init__(headers)
        self.data = data

    def __str__(self):
        return f'{{"data": {hash(self.data)}, {super().__str__()}}}'


class TranscriptionPacket(DataPacket):
    def __init__(self, transcript: str, headers=None):
        super().__init__(headers)
        self.transcript = transcript

    def __str__(self):
        return f'{{"transcript": {hash(self.transcript)}, {super().__str__()}}}'


class Word:
    class Entity:
        PERSON: ClassVar[str] = 'PERSON'
        GPE: ClassVar[str] = 'GPE'
        LOC: ClassVar[str] = 'LOC'
        ORG: ClassVar[str] = 'ORG'
        LANGUAGE: ClassVar[str] = 'LANGUAGE'
        NAT_REL_POL: ClassVar[str] = 'NAT_REL_POL'
        DATETIME: ClassVar[str] = 'DATETIME'
        PERIOD: ClassVar[str] = 'PERIOD'
        QUANTITY: ClassVar[str] = 'QUANTITY'
        MONEY: ClassVar[str] = 'MONEY'
        NUMERIC: ClassVar[str] = 'NUMERIC'
        ORDINAL: ClassVar[str] = 'ORDINAL'
        FACILITY: ClassVar[str] = 'FACILITY'
        WORK_OF_ART: ClassVar[str] = 'WORK_OF_ART'
        EVENT: ClassVar[str] = 'EVENT'

    def __init__(self, word: str, start_time_millis: float, end_time_millis: float, speaker: Optional[int] = None,
                 confidence: float = 0, entity: Optional[str] = None, entity_group_id: Optional[int] = None):
        self.word: str = word
        self.start_time: float = start_time_millis
        self.end_time: float = end_time_millis
        self.speaker: int = speaker
        self.confidence: float = confidence
        self.entity: Optional[str] = entity
        self.entity_group_id: Optional[int] = entity_group_id

    def __str__(self):
        return f'''
        {{
            "word": "{self.word}",
            "start_time": {self.start_time},
            "end_time": {self.end_time},
            "speaker": "{self.speaker}",
            "confidence": {self.confidence},
            "entity": "{self.entity}",
            "entity_group_id": {self.entity_group_id}
        }}
        '''

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return Word(
            word=self.word,
            start_time_millis=self.start_time,
            end_time_millis=self.end_time,
            speaker=self.speaker,
            confidence=self.confidence,
            entity=self.entity,
            entity_group_id=self.entity_group_id
        )


class TimestampedTranscriptionPacket(TranscriptionPacket):
    """
    Packet that contains the transcript with the timestamps associated to each word.

    Params:
     - words: list of transcribed words
     - headers: headers of the packet
    """

    def __init__(self, words: List[Word], headers=None, transcript=None):
        transcript = transcript if transcript is not None else ' '.join([word.word for word in words])
        super().__init__(transcript, headers)

        self.words = words

    def __str__(self):
        return f'{{"words": {str(self.words)}, {super().__str__()}}}'


class NdArrayDataPacket(DataPacket):
    def __init__(self, data: np.ndarray, headers=None):
        super().__init__(headers)
        self.data: np.ndarray = data

    def __str__(self):
        return f'{{"data": {hash(self.data.tobytes())}, {super().__str__()}}}'


class LogitsDataPacket(NdArrayDataPacket):
    def __init__(self, data: np.ndarray, timestep_duration: float, headers=None):
        super().__init__(data, headers)
        self.timestep_duration = timestep_duration

    def __str__(self):
        return f'{{"timestep_duration": {self.timestep_duration}, {super().__str__()}}}'


class SpacedLogitsDataPacket(LogitsDataPacket):
    def __init__(self, data: np.ndarray, timestep_duration: float, spaces: List[Tuple[int, int]], headers=None):
        super().__init__(data, timestep_duration, headers)
        self.spaces = spaces

    def __str__(self):
        return f'{{"spaces": {str(self.spaces)}, {super().__str__()}}}'


class ProcessedTranscriptionPacket(TimestampedTranscriptionPacket):
    def __init__(self, processed_words: List[Word], raw_transcription_packet: TimestampedTranscriptionPacket):
        super().__init__(words=raw_transcription_packet.words,
                         headers=raw_transcription_packet.headers,
                         transcript=' '.join([word.word for word in processed_words]))
        self.processed_words = processed_words
