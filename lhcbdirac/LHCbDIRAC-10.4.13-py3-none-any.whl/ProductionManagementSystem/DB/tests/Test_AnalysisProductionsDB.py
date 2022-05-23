###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from datetime import datetime, timedelta

import pytest

from LHCbDIRAC.ProductionManagementSystem.DB.AnalysisProductionsDB import AnalysisProductionsDB


@pytest.fixture
def apdb():
    db = AnalysisProductionsDB(url="sqlite+pysqlite:///:memory:")
    yield db


REQUEST_1 = {
    "request_id": 1234,
    "name": "MySample",
    "version": "v1r2p3",
    "wg": "MyWG",
    "analysis": "MyAnalysis",
    "extra_info": {
        "transformations": [],
        "merge_request": "https://gitlab.cern.ch/lhcb-datapkg/AnalysisProductions/-/merge_requests/0",
        "jira_task": "https://its.cern.ch/jira/browse/WGP-0",
    },
    "validity_start": datetime.now() - timedelta(days=1),
    "owners": [{"username": "johndoe"}],
    "auto_tags": [
        {"name": "config", "value": "MC"},
        {"name": "polarity", "value": "MagDown"},
        {"name": "eventtype", "value": "23133002"},
        {"name": "datatype", "value": "2012"},
    ],
}

REQUEST_2 = {
    "request_id": 987,
    "name": "AnotherSample",
    "version": "v1r2p4",
    "wg": "AnotherWG",
    "analysis": "AnotherAnalysis",
    "extra_info": {
        "transformations": [],
        "merge_request": "https://gitlab.cern.ch/lhcb-datapkg/AnalysisProductions/-/merge_requests/0",
        "jira_task": "https://its.cern.ch/jira/browse/WGP-0",
    },
    "validity_start": datetime.now() - timedelta(days=1),
    "owners": [{"username": "janedoe"}],
    "auto_tags": [
        {"name": "config", "value": "LHCb"},
        {"name": "polarity", "value": "MagUp"},
        {"name": "datatype", "value": "2018"},
    ],
}

REQUEST_3 = {
    "request_id": 988,
    "name": "AnotherSample",
    "version": "v1r2p3",
    "wg": "MyWG",
    "analysis": "MyAnalysis",
    "extra_info": {
        "transformations": [],
        "merge_request": "https://gitlab.cern.ch/lhcb-datapkg/AnalysisProductions/-/merge_requests/0",
        "jira_task": "https://its.cern.ch/jira/browse/WGP-0",
    },
    "validity_start": datetime.now() - timedelta(days=1),
    "owners": [{"username": "janedoe"}],
    "auto_tags": [
        {"name": "config", "value": "LHCb"},
        {"name": "polarity", "value": "MagUp"},
        {"name": "datatype", "value": "2018"},
    ],
}

TRANSFORMS_1a = {
    "id": 45,
    "status": "Archived",
    "steps": [
        {
            "stepID": 50,
            "application": "DaVinci/v45r6",
            "extras": ["AnalysisProductions.v0r0p2510752", "ProdConf"],
            "options": ["$SOMETHING/a.py"],
        }
    ],
    "used": False,
}

TRANSFORMS_1b = {
    "id": 47,
    "status": "Archived",
    "steps": [
        {
            "stepID": 51,
            "application": "Noether/v1r4",
            "extras": ["AppConfig.v3r398", "ProdConf"],
            "options": ["$SOMETHING/b.py"],
        }
    ],
    "used": True,
}


def _compareRequest(orig, new):
    assert new["sample_id"] is not None
    assert orig["request_id"] == new["request_id"]
    assert new["state"] is not None

    assert orig["wg"].lower() == new["wg"]
    assert orig["analysis"].lower() == new["analysis"]
    assert orig["version"].lower() == new["version"]
    assert orig["name"].lower() == new["name"]
    assert orig["extra_info"]["jira_task"] == new["jira_task"]
    assert orig["extra_info"]["merge_request"] == new["merge_request"]

    assert {x["username"].lower() for x in orig["owners"]} == set(new["owners"])
    assert orig["extra_info"]["transformations"] == new["transformations"]

    assert orig["validity_start"] == new["validity_start"]
    assert new["validity_end"] is None
    assert new["last_state_update"] is not None


def test_empty(apdb):
    assert apdb.listAnalyses() == {}
    assert apdb.listAnalyses(at_time=None) == {}
    assert apdb.listAnalyses(at_time=datetime.now()) == {}

    assert apdb.getKnownAutoTags() == set()

    assert apdb.getProductions() == []
    assert apdb.getProductions(wg="MyWG", analysis="MyAnalysis") == []
    assert apdb.getProductions(at_time=None) == []
    assert apdb.getProductions(at_time=datetime.now()) == []

    assert apdb.getArchivedRequests() == []
    assert apdb.getArchivedRequests(state="waiting") == []
    assert apdb.getArchivedRequests(state="ready") == []


def test_registerNew(apdb):
    newRequests = apdb.registerRequests([REQUEST_1])
    assert len(newRequests) == 1

    newRequest = newRequests[0]
    assert newRequest["sample_id"] == 1
    assert newRequest["state"] == "waiting"
    _compareRequest(REQUEST_1, newRequest)

    assert apdb.listAnalyses() == {"mywg": ["myanalysis"]}

    assert apdb.getProductions() == [newRequest]
    assert apdb.getProductions(wg="mywg", analysis="myanalysis") == [newRequest]
    assert apdb.getProductions(wg="MYWG", analysis="MYANALYSIS") == [newRequest]
    assert apdb.getProductions(name="mysample") == [newRequest]
    assert apdb.getProductions(name="MySample") == [newRequest]
    assert apdb.getProductions(name="anothersample") == []
    assert apdb.getProductions(state="waiting") == [newRequest]
    assert apdb.getProductions(state="active") == []
    assert apdb.getProductions(version="v1r2p3") == [newRequest]
    assert apdb.getProductions(version="v1r2p4") == []

    assert apdb.getKnownAutoTags() == {"config", "polarity", "eventtype", "datatype"}
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {
            "config": "mc",
            "polarity": "magdown",
            "eventtype": "23133002",
            "datatype": "2012",
        }
    }


def test_duplicate(apdb):
    apdb.registerRequests([REQUEST_1])
    with pytest.raises(ValueError, match=f"Already registered.*{REQUEST_1['request_id']}.*"):
        apdb.registerRequests([REQUEST_1])


def test_archival(apdb):
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])

    assert apdb.getArchivedRequests() == []
    assert apdb.getArchivedRequests(state="waiting") == []
    assert apdb.getArchivedRequests(state="ready") == []

    apdb.archiveSamples([1])

    archivedRequests = apdb.getArchivedRequests()
    assert len(archivedRequests) == 1
    assert archivedRequests[0]["request_id"] == 1234
    archivedRequests = apdb.getArchivedRequests(state="waiting")
    assert len(archivedRequests) == 1
    assert archivedRequests[0]["request_id"] == 1234
    assert apdb.getArchivedRequests(state="ready") == []

    with pytest.raises(ValueError, match=r".*have already been archived.*"):
        apdb.archiveSamples([2, 1, 3])
    archivedRequests = apdb.getArchivedRequests()
    assert len(archivedRequests) == 1
    assert archivedRequests[0]["request_id"] == 1234

    with pytest.raises(ValueError, match=r"Unknown sample IDs passed.*"):
        apdb.archiveSamples([2, 12, 3])
    archivedRequests = apdb.getArchivedRequests()
    assert len(archivedRequests) == 1
    assert archivedRequests[0]["request_id"] == 1234

    apdb.archiveSamples([2, 3])
    archivedRequests = apdb.getArchivedRequests()
    assert len(archivedRequests) == 3


def test_registerTransformations(apdb):
    apdb.registerRequests([REQUEST_1])

    with pytest.raises(ValueError):
        apdb.registerTransformations({})

    apdb.registerTransformations({1234: [TRANSFORMS_1a]})
    assert apdb.getProductions()[0]["transformations"] == [TRANSFORMS_1a]

    with pytest.raises(ValueError, match=r".*already known.*"):
        apdb.registerTransformations({1234: [TRANSFORMS_1a, TRANSFORMS_1b]})
    assert apdb.getProductions()[0]["transformations"] == [TRANSFORMS_1a]

    apdb.registerTransformations({1234: [TRANSFORMS_1b]})
    assert apdb.getProductions()[0]["transformations"] == [TRANSFORMS_1a, TRANSFORMS_1b]

    apdb.deregisterTransformations({1234: [TRANSFORMS_1a["id"]]})
    assert apdb.getProductions()[0]["transformations"] == [TRANSFORMS_1b]


def test_registerTransformationsError(apdb):
    """Ensure that nothing is changed if an invalid request ID is passed."""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    with pytest.raises(ValueError, match=r"Did not find requests for IDs: \[99999\]"):
        apdb.registerTransformations({987: [TRANSFORMS_1a], 99999: [TRANSFORMS_1a], 988: [TRANSFORMS_1a]})
    for prod in apdb.getProductions():
        assert prod["transformations"] == [], prod


def test_deregisterTransformationsError(apdb):
    """Ensure that nothing is changed if an invalid request ID is passed."""
    apdb.registerRequests([REQUEST_2, REQUEST_3])
    apdb.registerTransformations({987: [TRANSFORMS_1a], 988: [TRANSFORMS_1a]})
    with pytest.raises(ValueError, match=r"Did not find requests for IDs: \[99999\]"):
        apdb.deregisterTransformations(
            {987: [TRANSFORMS_1a["id"]], 99999: [TRANSFORMS_1a["id"]], 988: [TRANSFORMS_1a["id"]]}
        )
    for prod in apdb.getProductions():
        assert prod["transformations"] == [TRANSFORMS_1a], prod


def test_deregisterTransformationsError2(apdb):
    """Ensure that nothing is changed if an invalid request ID is passed."""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    apdb.registerTransformations({1234: [TRANSFORMS_1a], 987: [TRANSFORMS_1a], 988: [TRANSFORMS_1a]})
    with pytest.raises(ValueError, match=r"Transformation 47 is not known"):
        apdb.deregisterTransformations(
            {1234: [TRANSFORMS_1a["id"]], 987: [TRANSFORMS_1a["id"], 47], 988: [TRANSFORMS_1a["id"]]}
        )
    for prod in apdb.getProductions():
        assert prod["transformations"] == [TRANSFORMS_1a], prod

    apdb.deregisterTransformations(
        {1234: [TRANSFORMS_1a["id"]], 987: [TRANSFORMS_1a["id"]], 988: [TRANSFORMS_1a["id"]]}
    )
    for prod in apdb.getProductions():
        assert prod["transformations"] == [], prod


def test_setState(apdb):
    apdb.registerRequests([REQUEST_1])
    prod1 = apdb.getProductions()[0]
    assert prod1["state"] == "waiting"
    assert "progress" not in prod1

    apdb.setState({1234: {"state": "active", "progress": 0.5}})

    prod2 = apdb.getProductions()[0]
    assert prod1["last_state_update"] <= prod2["last_state_update"]
    assert prod2["state"] == "active"
    assert prod2["progress"] == 0.5

    apdb.setState({1234: {"state": "ready", "progress": None}})

    prod3 = apdb.getProductions()[0]
    assert prod2["last_state_update"] <= prod3["last_state_update"]
    assert prod3["state"] == "ready"
    assert "progress" not in prod3


def test_setStateMultiple(apdb):
    apdb.registerRequests([REQUEST_1, REQUEST_3])
    apdb.setState(
        {
            1234: {"state": "active", "progress": 0.5},
            988: {"state": "active", "progress": 0.4},
        }
    )
    prod1, prod2 = apdb.getProductions()
    assert prod1["request_id"] == 1234
    assert prod1["state"] == "active"
    assert prod1["progress"] == 0.5
    assert prod2["request_id"] == 988
    assert prod2["state"] == "active"
    assert prod2["progress"] == 0.4
    with pytest.raises(ValueError, match=r"Failed to update Request.*"):
        apdb.setState(
            {
                1234: {"state": "active", "progress": 0.6},
                99999: {"state": "active", "progress": 0.3},
                988: {"state": "active", "progress": 0.7},
            }
        )
    prod1, prod2 = apdb.getProductions()
    assert prod1["request_id"] == 1234
    assert prod1["state"] == "active"
    assert prod1["progress"] == 0.5
    assert prod2["request_id"] == 988
    assert prod2["state"] == "active"
    assert prod2["progress"] == 0.4


def test_getKnownAutoTags(apdb):
    apdb.registerRequests([REQUEST_2])
    assert set(apdb.getKnownAutoTags()) == {"config", "polarity", "datatype"}
    apdb.registerRequests([REQUEST_1])
    assert set(apdb.getKnownAutoTags()) == {"config", "polarity", "eventtype", "datatype"}


def test_setTagsNoChanges(apdb):
    """Setting tags to the same value should be a no-op."""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    apdb.setTags(
        {
            1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
            2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
        },
        {
            1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
            2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
        },
    )
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
        3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
    }
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }


def test_setTagsCaseInsensitive(apdb):
    """Tags should always be lowercased"""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    apdb.setTags(
        {
            2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
        },
        {
            2: {"config": "lhcb", "Polarity": "MagUp", "datatype": "2018"},
        },
    )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }
    apdb.setTags(
        {
            2: {"config": "lhcb", "Polarity": "MagUp", "datatype": "2018"},
        },
        {
            2: {"config": "lhcb", "polarity": "MagUp", "datatype": "2018"},
        },
    )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }
    apdb.setTags(
        {
            2: {"config": "lhcb", "Polarity": "MagUp", "datatype": "2018"},
        },
        {
            2: {"config": "lhcb", "polarity": "MagUp", "dataType": "2018", "HELLO": "WORLD", "FoO": 123},
        },
    )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "hello": "world", "foo": "123"}
    }
    with pytest.raises(ValueError, match=r".*contains duplicate keys.*"):
        apdb.setTags(
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
            },
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "hello": "world", "HELLO": 123},
            },
        )
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
        3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
    }


def test_setTagsWithChanges(apdb):
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    apdb.setTags(
        {
            3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
        },
        {
            3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"},
        },
    )
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
        3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_ss"},
    }
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }


def test_setTagsMissingOldTags(apdb):
    """Tags cannot be changed if oldTags isn't up to date"""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    with pytest.raises(ValueError, match=r".*must contain the same keys.*"):
        apdb.setTags(
            {},
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"},
            },
        )
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
        3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
    }
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }


def test_setTagsWrongOldTags(apdb):
    """Tags cannot be changed if oldTags isn't up to date"""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    apdb.setTags(
        {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}},
        {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"}},
    )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_ss"}
    }
    with pytest.raises(ValueError, match=r"oldTags is out of date"):
        apdb.setTags(
            {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}},
            {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}},
        )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_ss"}
    }
    with pytest.raises(ValueError, match=r"oldTags is out of date"):
        apdb.setTags(
            {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_os"}},
            {2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_ws"}},
        )
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "dptokpipi_ss"}
    }


# def test_setTagsOutdated(apdb):


def test_setTagsAutoTags(apdb):
    """Ensure AutoTags cannot be added, removed or modified"""
    apdb.registerRequests([REQUEST_1, REQUEST_2, REQUEST_3])
    with pytest.raises(ValueError, match=r"Cannot modify AutoTags.*"):
        apdb.setTags(
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
                2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
            },
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"},
                2: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "eventtype": "90000000"},
            },
        )
    with pytest.raises(ValueError, match=r"Cannot modify AutoTags.*"):
        apdb.setTags(
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
                2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
            },
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"},
                2: {"config": "lhcb", "polarity": "magdown", "datatype": "2018"},
            },
        )
    with pytest.raises(ValueError, match=r"Cannot modify AutoTags.*"):
        apdb.setTags(
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
                2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
            },
            {
                3: {"config": "lhcb", "polarity": "magup", "datatype": "2018", "sample": "DpToKpipi_SS"},
                2: {"config": "lhcb", "polarity": "magup"},
            },
        )
    assert apdb.getTags("MyWG", "MyAnalysis") == {
        1: {"config": "mc", "polarity": "magdown", "eventtype": "23133002", "datatype": "2012"},
        3: {"config": "lhcb", "polarity": "magup", "datatype": "2018"},
    }
    assert apdb.getTags("AnotherWG", "AnotherAnalysis") == {
        2: {"config": "lhcb", "polarity": "magup", "datatype": "2018"}
    }
