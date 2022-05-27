from typing import List, Optional

from pydantic import BaseModel


class TestInfo(BaseModel):
    """用例信息"""

    name: str
    browser: Optional[str]


class TestStep(BaseModel):
    """用例步骤"""

    步骤名: str
    关键字: str
    参数: List[str]


class BaseTestCase(BaseModel):
    """测试用例"""

    info: TestInfo
    steps: List[TestStep]


class BaseTestSuite(BaseModel):
    """测试套件"""

    info: TestInfo
    case_list: List[BaseTestCase]
