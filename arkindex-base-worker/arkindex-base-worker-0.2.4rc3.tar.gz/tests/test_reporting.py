# -*- coding: utf-8 -*-
import json
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

import pytest
from apistar.exceptions import ErrorResponse

from arkindex_worker.reporting import Reporter


def test_init():
    version_id = str(uuid.uuid4())
    reporter = Reporter(name="Worker", slug="worker-slug", version=version_id)
    assert "started" in reporter.report_data
    del reporter.report_data["started"]
    assert reporter.report_data == {
        "name": "Worker",
        "slug": "worker-slug",
        "version": version_id,
        "elements": {},
    }


def test_process():
    reporter = Reporter("worker")
    reporter.process("myelement")
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    assert "started" in element_data
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 0,
        "classifications": {},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_element():
    reporter = Reporter("worker")
    reporter.add_element("myelement", type="text_line")
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {"text_line": 1},
        "transcriptions": 0,
        "classifications": {},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_element_count():
    """
    Report multiple elements with the same parent and type
    """
    reporter = Reporter("worker")
    reporter.add_element("myelement", type="text_line", type_count=42)
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {"text_line": 42},
        "transcriptions": 0,
        "classifications": {},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_classification():
    reporter = Reporter("worker")
    reporter.add_classification("myelement", "three")
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 0,
        "classifications": {"three": 1},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_classifications():
    reporter = Reporter("worker")
    with pytest.raises(AssertionError):
        reporter.add_classifications("myelement", {"not": "a list"})

    reporter.add_classifications(
        "myelement", [{"class_name": "three"}, {"class_name": "two"}]
    )
    reporter.add_classifications(
        "myelement",
        [
            {"class_name": "three"},
            {"class_name": "two", "high_confidence": True},
            {"class_name": "three", "confidence": 0.42},
        ],
    )

    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 0,
        "classifications": {"three": 3, "two": 2},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_transcription():
    reporter = Reporter("worker")
    reporter.add_transcription("myelement")
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 1,
        "classifications": {},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_transcription_count():
    """
    Report multiple transcriptions with the same element and type
    """
    reporter = Reporter("worker")
    reporter.add_transcription("myelement", 1337)
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 1337,
        "classifications": {},
        "entities": [],
        "metadata": [],
        "errors": [],
    }


def test_add_entity():
    reporter = Reporter("worker")
    reporter.add_entity(
        "myelement", "12341234-1234-1234-1234-123412341234", "person", "Bob Bob"
    )
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 0,
        "classifications": {},
        "entities": [
            {
                "id": "12341234-1234-1234-1234-123412341234",
                "type": "person",
                "name": "Bob Bob",
            }
        ],
        "metadata": [],
        "errors": [],
    }


def test_add_metadata():
    reporter = Reporter("worker")
    reporter.add_metadata(
        "myelement", "12341234-1234-1234-1234-123412341234", "location", "Teklia"
    )
    assert "myelement" in reporter.report_data["elements"]
    element_data = reporter.report_data["elements"]["myelement"]
    del element_data["started"]
    assert element_data == {
        "elements": {},
        "transcriptions": 0,
        "classifications": {},
        "entities": [],
        "metadata": [
            {
                "id": "12341234-1234-1234-1234-123412341234",
                "type": "location",
                "name": "Teklia",
            }
        ],
        "errors": [],
    }


def test_error():
    reporter = Reporter("worker")
    reporter.error("myelement", ZeroDivisionError("What have you done"))
    reporter.error(
        "myelement",
        ErrorResponse(
            title="I'm a teapot",
            status_code=418,
            content='{"coffee": "Can\'t touch this"}',
        ),
    )
    assert reporter.report_data["elements"]["myelement"]["errors"] == [
        {"class": "ZeroDivisionError", "message": "What have you done"},
        {
            "class": "ErrorResponse",
            "message": "I'm a teapot",
            "status_code": 418,
            "content": '{"coffee": "Can\'t touch this"}',
        },
    ]


def test_reporter_save(mocker):
    datetime_mock = mocker.MagicMock()
    datetime_mock.utcnow.return_value = datetime(2000, 1, 1)
    mocker.patch("arkindex_worker.reporting.datetime", datetime_mock)
    version_id = str(uuid.uuid4())
    reporter = Reporter(name="Worker", slug="worker-slug", version=version_id)
    reporter.add_element("myelement", type="text_line", type_count=4)
    with NamedTemporaryFile() as f:
        reporter.save(f.name)
        exported_data = json.load(f)
    assert exported_data == {
        "name": "Worker",
        "slug": "worker-slug",
        "started": "2000-01-01T00:00:00",
        "version": version_id,
        "elements": {
            "myelement": {
                "classifications": {},
                "elements": {"text_line": 4},
                "entities": [],
                "errors": [],
                "metadata": [],
                "started": "2000-01-01T00:00:00",
                "transcriptions": 0,
            }
        },
    }
