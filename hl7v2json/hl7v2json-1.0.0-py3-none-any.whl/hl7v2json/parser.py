# -*- coding: utf-8 -*-
import importlib.resources
from datetime import datetime, timezone, timedelta
import json
import textwrap

import hl7

fields = segments = messages = None

with importlib.resources.open_text("hl7v2json.data.bamboo", "fields.json") as f:
    fields = json.load(f)

with importlib.resources.open_text("hl7v2json.data.bamboo", "messages.json") as f:
    messages = json.load(f)

with importlib.resources.open_text("hl7v2json.data.bamboo", "segments.json") as f:
    segments = json.load(f)


def parse(message):
    sequence = parse_hl7_message(message)
    if not validate_segments(sequence):
        raise Exception('The message is invalid')

    sequence_with_description = update_description(0, sequence)
    data = hl7_message_to_dict(sequence_with_description)
    return data


def parse_hl7_message(message):
    """Parse the raw hl7 message to list of segments"""

    message = textwrap.dedent(message)
    h = hl7.parse(message)
    return h


def validate_segments(message):
    """Check if a parsed message containing legal segments"""

    if not isinstance(message, hl7.containers.Message):
        raise Exception('The message should be an instance of hl7.Message')

    message_type = '{}_{}'.format(message[0][9][0][0], message[0][9][0][1])
    possible_segments = messages[str(message_type)]['segments']['segments']
    for segment in possible_segments:
        if 'children' in segment:
            possible_segments.extend(segment['children'])
    allow_segments = [
        segment['name'] for segment in possible_segments
    ]
    actual_segments = [str(segment[0]) for segment in message]
    return set(actual_segments) < set(allow_segments)


def update_description(idx, sequence, **kwargs):
    """Update description for each sequence"""

    if isinstance(sequence, hl7.Message):
        message_type = '{}_{}'.format(
            sequence[0][9][0][0], sequence[0][9][0][1])
        sequence.desc = messages[message_type]['desc']
        sequence.name = messages[message_type]['name']
    elif isinstance(sequence, hl7.Segment):
        segment_type = str(sequence[0])
        sequence.desc = segments[segment_type]['desc']
    elif isinstance(sequence, hl7.Field):
        if idx == 0:
            return
        segment_type = str(kwargs['parent'][0])
        sequence.desc = segments[segment_type]['fields'][idx - 1]['desc']
        sequence.datatype = segments[segment_type]['fields'][idx - 1]['datatype']
    elif isinstance(sequence, hl7.Repetition):
        field = kwargs['parent']
        sequence.desc = field.desc
        sequence.datatype = field.datatype
    elif isinstance(sequence, hl7.Component):
        field = kwargs['parent']
        if fields[field.datatype]['subfields']:
            description = fields[field.datatype]['subfields'][idx]['desc']
            datatype = fields[field.datatype]['subfields'][idx]['datatype']
        else:
            description = fields[field.datatype]['desc']
            datatype = field.datatype
        sequence.desc = description
        sequence.datatype = datatype

    if type(sequence) in [hl7.Message, hl7.Segment, hl7.Field, hl7.Repetition]:
        for idx, sub_sequence in enumerate(sequence):
            update_description(idx, sub_sequence, parent=sequence)

    return sequence


def hl7_message_to_dict(message):
    message_dict = {
        'info': _get_message_info(message),
        'segments': _get_segments_data(message)
    }
    return message_dict


def _get_message_info(message):
    return {
        'messageType': message.name,
        'messageDescription': message.desc,
    }


def _get_segments_data(message):
    segments_data = {}
    for segment in message:
        fields = _get_fields_data(segment)
        desc_key = segment.desc.split()[0].lower() + ''.join(x.capitalize() for x in segment.desc.split()[1:])
        if desc_key in segments_data:
            # Handle multiple ZPP segments
            if desc_key == "customCareInformation":
                for key in fields:
                    if key != 'description':
                        segments_data[desc_key][key] += f" {fields[key]}"
            # Handle muliple other segments
            else:
                if 'repeat' in segments_data[desc_key]:
                    segments_data[desc_key]['repeat'].append(fields)
                else:
                    segments_data[desc_key]['repeat'] = [fields]
        else:
            segments_data[desc_key] = fields
    return segments_data


def _get_fields_data(segment):
    fields_data = {}
    for idx, field in enumerate(segment):
        if idx == 0:
            continue

        if not str(field):
            continue

        description = field.desc.split()[0].lower() + ''.join(x.capitalize() for x in field.desc.split()[1:])
        data = str(field)            
        if description in ["recordedDate/time", "admitDate/time", "date/timeOfMessage", "eventOccurred"]:
            data = datetime.strptime(data, "%Y%m%d%H%M%S").replace(tzinfo=timezone(-timedelta(hours=5))).isoformat()
        elif description in ["date/timeOfBirth"]:
            data = datetime.strptime(data, "%Y%m%d").date().isoformat()
        fields_data[description] = data
        repetitions = _get_repetitions_data(field)
        if repetitions:
            fields_data[description] = repetitions
    return fields_data


def _get_repetitions_data(field):
    repetitions_data = {}
    if not isinstance(field[0], hl7.Repetition):
        return repetitions_data

    # Move components to top level within field
    # Set descriptions to camelCase
    for repetition in field:
        components = _get_components_data(repetition)
    for component in components:
        desc_key = component['description'].split()[0].lower() + ''.join(x.capitalize() for x in component['description'].split()[1:])
        repetitions_data[desc_key] = component['data']
    return repetitions_data


def _get_components_data(repetition):
    components_data = []
    if not isinstance(repetition[0], hl7.Component):
        return components_data

    for idx, component in enumerate(repetition):
        if not str(component):
            continue

        component_dict = {
            'description': component.desc,
            'data': str(component)
        }
        components_data.append(component_dict)
    return components_data
