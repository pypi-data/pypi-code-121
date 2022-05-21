# flake8: noqa: W291
# pylint: disable=too-many-lines,trailing-whitespace

"""
annoworkapiのmodel
enumならば列挙体として定義する。
それ以外は型ヒントしてして宣言する。

Note:
    このファイルはopenapi-generatorで自動生成される。
"""
from __future__ import annotations

import warnings  # pylint: disable=unused-import
from enum import Enum
from typing import Any, NewType, Optional, Union  # pylint: disable=unused-import


class Authority(Enum):
    """
    アカウントの権限
    """

    USER = "user"
    ADMIN = "admin"


class Locale(Enum):
    """
    ロケール
    """

    JA_JP = "ja-JP"
    EN_US = "en-US"


class Role(Enum):
    """
    ワークスペースメンバーの権限
    """

    WORKER = "worker"
    MANAGER = "manager"
    OWNER = "owner"


class ScheduleType(Enum):
    """
    値の形式(hours: 固定値の時間、percentage: 予定稼働時間に対する割合(%))
    """

    HOURS = "hours"
    PERCENTAGE = "percentage"
