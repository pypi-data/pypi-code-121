# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from hl7v2json import parser
from tests.samples import message1, message2


class TestParserValidate(TestCase):
    def setUp(self):
        pass

    def test_parse_hl7_message(self):
        h = parser.parse_hl7_message(message1)
        assert h is not None
        assert len(h) == 7

    def test_update_description(self):
        h = parser.parse_hl7_message(message1)
        new_message = parser.update_description(0, h)
        assert hasattr(new_message, 'desc')

    def test_validate_message(self):
        h = parser.parse_hl7_message(message1)
        assert parser.validate_segments(h)

    def test_hl7_message_to_dict(self):
        h = parser.parse_hl7_message(message1)
        new_message = parser.update_description(0, h)
        data = parser.hl7_message_to_dict(new_message)
        assert data is not None
        # print(json.dumps(data, indent=4))
        assert data['info']['messageType'] == 'ADT_A01'
        assert data['info']['messageDescription'] == 'Admit/Visit Notification'

        assert 'messageHeader' in data['segments']

        msh_fields = data['segments']['messageHeader']
        assert 'fieldSeparator' in msh_fields
        assert msh_fields['fieldSeparator'] == '|'

        assert 'messageType' in msh_fields
        assert msh_fields['messageType']['messageCode'] == 'ADT'

        h = parser.parse_hl7_message(message2)
        new_message = parser.update_description(0, h)
        data = parser.hl7_message_to_dict(new_message)
        # print(json.dumps(data, indent=4))
        assert data is not None

    def test_parser(self):
        data = parser.parse(message1)
        assert data is not None
