from dataclasses import dataclass, field
from typing import List, Union

from dataclasses_json import dataclass_json
from typer.models import NoneType


@dataclass_json
@dataclass
class JiraTestScriptStep:
    description: str = ""
    testData: str = ""
    expectedResult: str = ""


@dataclass_json
@dataclass
class JiraTestScript:
    id: str = ""
    text: str = ""
    type: str = "PLAIN_TEXT"  # PLAIN_TEXT | STEP_BY_STEP
    steps: List[JiraTestScriptStep] = field(default_factory=list)


@dataclass_json
@dataclass
class JiraTestData:
    id: int = 0
    key: str = ""
    projectKey: str = ""
    name: str = ""
    folder: str = ""
    status: str = "Draft"  # Approved | Draft
    priority: str = "Normal"
    objective: str = ""
    precondition: str = ""
    testScript: Union[JiraTestScript, NoneType] = None
    labels: List[str] = field(default_factory=list)
    issueLinks: List[str] = field(default_factory=list)
    confluenceLinks: List[str] = field(default_factory=list)
    webLinks: List[Union[str, dict]] = field(default_factory=list)

    # test result fields
    testrun_folder: str = ""
    testrun_status: str = ""
    testrun_environment: str = ""
    testrun_comment: str = ""
    testrun_duration: str = ""  # 100000 ms
    testrun_date: str = ""  # YYYY-MM-DDThh:mm:ssZ
