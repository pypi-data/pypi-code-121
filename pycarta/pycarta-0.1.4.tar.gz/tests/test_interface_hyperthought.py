import hyperthought as ht
import json
import numpy as np
import os
import pytest
from pycarta.interface.hyperthought import get_hyperthought_auth
from pycarta.interface.hyperthought import get_children
from pycarta.interface.hyperthought import get_templates
from pycarta.interface.hyperthought import get_workspaces
from pycarta.interface.hyperthought.base import Workspace
from pycarta.interface.hyperthought.base import Template
from pycarta.interface.hyperthought.base import HyperThoughtKeyFinder
from pycarta.interface.hyperthought.schema import Schema, build
from pycarta.interface.hyperthought import update_process


@pytest.fixture
def hyperthought_base_workspace():
    with open("expected_output.json") as ifs:
        data = json.load(ifs)
    return data["integrations"]["hyperthought"]["base"]["workspace"]


@pytest.fixture
def hyperthought_base_template():
    with open("expected_output.json") as ifs:
        data = json.load(ifs)
    return data["integrations"]["hyperthought"]["base"]["template"]


@pytest.fixture
def hyperthought_base_process():
    with open("expected_output.json") as ifs:
        data = json.load(ifs)
    return data["integrations"]["hyperthought"]["base"]["process"]


@pytest.fixture(scope="module")
def hyperthought_auth():
    if "HYPERTHOUGHT_AUTH" not in os.environ:
        print("Set 'export HYPERTHOUGHT_AUTH=[HyperThought auth token]' before testing.")
        raise ValueError(
            "Environment variable HYPERTHOUGHT_AUTH must be set to run tests."
        )
    return get_hyperthought_auth(os.environ["HYPERTHOUGHT_AUTH"])


@pytest.fixture
def rng():
    return np.random.default_rng()


class TestBase:
    def test_workspace(self, hyperthought_base_workspace):
        pkg = hyperthought_base_workspace
        workspace = Workspace(**pkg)
        assert workspace.id == pkg["id"]
        b = [
            workspace[k] == v
            for k,v in pkg.items()
            if not isinstance(v, (list, dict))
        ]
        assert all(b), \
            "Workspace does not contain expected items"

    def test_template(self, hyperthought_base_template):
        pkg = hyperthought_base_template
        template = Template(**pkg)
        assert template.id == pkg["key"]
        b = [
            template[k] == v
            for k,v in pkg.items()
            if not isinstance(v, (list, dict))
        ]
        assert all(b), \
            "Workspace does not contain expected items"

    def test_hyperthought_key_finder(self, hyperthought_auth):
        auth = hyperthought_auth
        key_finder = HyperThoughtKeyFinder(auth)
        workspace = {
            "uid": "07b519d0-7a0d-44fd-b985-75610c5db46b",
            "path": "KappesBR"
        }
        template = {
            "uid": "4cda7abf-d3ca-4126-adc1-02fc329873e6",
            "path": "KappesBR/Workflow01"
        }
        workflow = {
            "uid": "ce182e59-0912-4a0d-b994-d7da1164653e",
            "path": "KappesBR/Workflow01/Workflow03"
        }
        process = {
            "uid": "ea44eec1-b3df-4161-a606-02d46bc55e70",
            "path": "KappesBR/Workflow01/Workflow03/Process04"
        }
        for obj in (workspace, template, workflow, process):
            assert key_finder(obj["uid"]) == obj["uid"]
            assert key_finder(obj["path"]) == obj["uid"]


class TestAccessors:
    def test_get_children(self, hyperthought_auth, hyperthought_base_process):
        auth = hyperthought_auth
        key_finder = HyperThoughtKeyFinder(auth)
        process = hyperthought_base_process
        children = get_children(auth, process["content"]["parent_process"])
        for child in children:
            if key_finder(child) == key_finder(process):
                return
        assert False, "get_children failed"

    def test_get_templates(self, hyperthought_auth, hyperthought_base_workspace, hyperthought_base_template):
        auth = hyperthought_auth
        key_finder = HyperThoughtKeyFinder(auth)
        workspace = hyperthought_base_workspace
        template = hyperthought_base_template
        templates = get_templates(auth, key_finder(workspace))
        for k,v in templates.items():
            if key_finder(v) == key_finder(template):
                return
        assert False, f"Failed to find {template['name']}"

    def test_get_workspaces(self, hyperthought_auth, hyperthought_base_workspace):
        auth = hyperthought_auth
        key_finder = HyperThoughtKeyFinder(auth)
        workspace = hyperthought_base_workspace
        retrieved = get_workspaces(auth)
        b = [(key_finder(r) == key_finder(workspace)) for r in retrieved]
        assert any(b), f"Failed to find {workspace['name']}"


class TestSchema:
    def test_schema_small(self, hyperthought_auth, workspace, template, name):
        schema = Schema([
            {
                "id": "Build",
                "type": "WorkflowBuilder",
                "contains": [
                    {
                        "type": "Measurement",
                        "name": "Measurement"
                    }
                ]
            },
            {
                "id": "SMeasure",
                "type": "ProcessBuilder",
                "contains": [
                    {
                        "key": "Sa",
                        "units": "µm"
                    }
                ]
            },
            {
                "id": "Measurement",
                "type": "SMeasure",
                "contains": [
                    {
                        "key": "Vmc",
                        "value": 1.23,
                        "units": "mL/m^2"
                    }
                ]
            }
        ])
        if name is None:
            raise IOError("Must call schema test with the --name=[workflow name] option.")
        builder = schema["Build"](f"{name}-small")
        wf = builder.build(
            auth=hyperthought_auth,
            workspace=workspace,
            parent=f"{workspace}/{template}"
        )

    # def test_schema_large(self, hyperthought_auth, workspace, template, name):
    #     schema = Schema("data/schema.json")
    #     if name is None:
    #         raise IOError("Must call schema test with the --name=[workflow name] option.")
    #     builder = schema["Build"](f"{name}-large")
    #     wf = builder.build(
    #         auth=hyperthought_auth,
    #         workspace=workspace,
    #         parent=f"{workspace}/{template}"
    #     )
    #
    # def test_single_build(self, hyperthought_auth, workspace, template, name):
    #     if name is None:
    #         raise IOError("Must call schema test with the --name=[workflow name] option.")
    #     build(
    #         hyperthought_auth,
    #         typename="Build",
    #         name="UTEP04",
    #         parent=template,
    #         workspace=workspace,
    #         schema="data/schema.json"
    #     )
    #
    # def test_multi_build(self, hyperthought_auth, workspace, template, name):
    #     if name is None:
    #         raise IOError("Must call schema test with the --name=[workflow name] option.")
    #     build(
    #         hyperthought_auth,
    #         typename="GTADExPArtifact",
    #         name=[f"GTADExP Artifact {i}" for i in range(2, 4)],
    #         parent=template + "/UTEP04/Parts",
    #         workspace=workspace,
    #         schema="data/schema.json"
    #     )


class TestSetters:
    @staticmethod
    def document_to_key_value(doc):
        return {
            m["keyName"]: m["value"]["link"] for m in doc["metadata"]
        }

    @staticmethod
    def document_to_key_unit(doc):
        return {
            m["keyName"]: m["unit"] for m in doc["metadata"]
        }

    @staticmethod
    def document_to_key_annotation(doc):
        return {
            m["keyName"]: m["annotation"] for m in doc["metadata"]
        }

    @staticmethod
    def random_letter(rng, size=1):
        return [
            chr(i) for i in
            rng.integers(ord('a'), ord('z')+1, size=size)
        ]

    def test_update_process(self, hyperthought_auth, rng):
        auth = hyperthought_auth
        rng = np.random.default_rng()
        processNode = "Carta Development/pytest/Process Node Update/Process Node"
        processNodeId = HyperThoughtKeyFinder(auth)(processNode)
        # test existing metadata entry
        values = {
            "Numeric": 100*(2*rng.random() - 1)
        }
        units = {
            "Numeric": "".join(TestSetters.random_letter(rng, size=2))
        }
        annotations = {
            "Numeric": " ".join([
                "".join(TestSetters.random_letter(rng, size=rng.integers(2, 6)))
                for _ in range(5)
            ])
        }
        update_process(
            auth,
            processNode,
            values=values,
            units=units,
            annotations=annotations
        )
        doc = ht.api.workflow.WorkflowAPI(auth).get_document(processNodeId)
        assert np.isclose(
            TestSetters.document_to_key_value(doc)["Numeric"],
            values["Numeric"]
        )
        assert TestSetters.document_to_key_unit(doc)["Numeric"] == units["Numeric"]
        assert TestSetters.document_to_key_annotation(doc)["Numeric"] == annotations["Numeric"]
        # test new metadata entry
        values = {
            "foo": 100 * (2 * rng.random() - 1)
        }
        units = {
            "foo": "".join(TestSetters.random_letter(rng, size=2))
        }
        annotations = {
            "foo": " ".join([
                "".join(TestSetters.random_letter(rng, size=rng.integers(2, 6)))
                for _ in range(5)
            ])
        }
        update_process(
            auth,
            processNode,
            values=values,
            units=units,
            annotations=annotations,
            add=True
        )
        tmp = ht.api.workflow.WorkflowAPI(auth).get_document(processNodeId)
        assert np.isclose(
            TestSetters.document_to_key_value(tmp)["foo"],
            values["foo"]
        )
        assert TestSetters.document_to_key_unit(tmp)["foo"] == units["foo"]
        assert TestSetters.document_to_key_annotation(tmp)["foo"] == annotations["foo"]
        # return the process
        ht.api.workflow.WorkflowAPI(auth).update_document(doc)
