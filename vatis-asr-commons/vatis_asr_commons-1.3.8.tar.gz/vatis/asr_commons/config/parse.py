from typing import Any, Dict, List, Optional

from vatis.asr_commons.config.headers import *

from vatis.asr_commons.config.logging import get_logger
from vatis.asr_commons.live.headers import *

logger = get_logger(__name__)


def parse_post_processing_options(headers) -> Dict[str, Any]:
    post_processing_config: Dict[str, Any] = {}

    if DISABLE_DISFLUENCIES_HEADER in headers:
        post_processing_config['disable_disfluencies'] = str(headers.get(DISABLE_DISFLUENCIES_HEADER)).lower() == 'true'

    if ENABLE_PUNCTUATION_AND_CAPITALIZATION_HEADER in headers:
        post_processing_config['enable_punctuation_capitalization'] = str(headers.get(ENABLE_PUNCTUATION_AND_CAPITALIZATION_HEADER)).lower() == 'true'

    if ENABLE_ENTITIES_RECOGNITION_HEADER in headers:
        post_processing_config['enable_entities_recognition'] = str(headers.get(ENABLE_ENTITIES_RECOGNITION_HEADER)).lower() == 'true'

    if ENABLE_NUMERALS_CONVERSION_HEADER in headers:
        post_processing_config['enable_numerals_conversion'] = str(headers.get(ENABLE_NUMERALS_CONVERSION_HEADER)).lower() == 'true'

    return post_processing_config


def parse_speakers_diarization_and_channels_transcription_options(headers) -> Dict[str, Any]:
    options: Dict[str, Any] = {}

    if SPEAKERS_DIARIZATION_HEADER in headers:
        options['speakers_diarization'] = str(headers.get(SPEAKERS_DIARIZATION_HEADER)).lower() == 'true'

    if SPEAKERS_NUMBER_HEADER in headers:
        options['speakers_number'] = int(headers.get(SPEAKERS_NUMBER_HEADER))

    return options


def parse_audio_attributes(headers) -> Dict[str, Any]:
    audio_attributes: Dict[str, Any] = {}

    if SAMPLE_RATE_HEADER in headers:
        audio_attributes['sample_rate'] = int(headers.get(SAMPLE_RATE_HEADER))

    if BIT_RATE_HEADER in headers:
        audio_attributes['bit_rate'] = int(headers.get(BIT_RATE_HEADER))

    if BIT_DEPTH_HEADER in headers:
        audio_attributes['bit_depth'] = int(headers.get(BIT_DEPTH_HEADER))

    if AUDIO_FORMAT_HEADER in headers:
        audio_attributes['audio_format'] = str(headers.get(AUDIO_FORMAT_HEADER))

    if SENDING_HEADERS_HEADER in headers:
        audio_attributes['sending_headers'] = str(headers.get(SENDING_HEADERS_HEADER)).lower() == 'true'

    if CHANNELS_HEADER in headers:
        audio_attributes['channels'] = int(headers.get(CHANNELS_HEADER))

    return audio_attributes


def parse_live_stream_config(headers) -> Dict[str, Any]:
    stream_config: Dict[str, Any] = {}

    if FRAME_LEN_HEADER in headers:
        stream_config['frame_len'] = float(headers[FRAME_LEN_HEADER])

    if FRAME_OVERLAP_HEADER in headers:
        stream_config['frame_overlap'] = float(headers[FRAME_OVERLAP_HEADER])

    if BUFFER_OFFSET_HEADER in headers:
        stream_config['buffer_offset'] = float(headers[BUFFER_OFFSET_HEADER])

    return stream_config


def parse_hotwords_config(headers) -> Dict[str, Any]:
    hotwords_config: Dict[str, Any] = {}

    if HOTWORDS_KEY in headers:
        hotwords = headers.get(HOTWORDS_KEY)
        parsed_hotwords: Optional[List[str]] = None

        if isinstance(hotwords, list):
            parsed_hotwords = hotwords
        elif isinstance(hotwords, str):
            parsed_hotwords = list(hotwords.split(','))
        elif hotwords is not None:
            logger.warning(f'Couldn\'t parse hotwords: {hotwords}')

        hotwords_config['hotwords'] = parsed_hotwords

    if HOTWORDS_WEIGHT_KEY in headers:
        hotwords_config['hotwords_weight'] = float(headers.get(HOTWORDS_WEIGHT_KEY))

    return hotwords_config
