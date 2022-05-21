"""
外部連携システム"AnnoFab"に依存したUtil関数です。
"""
from typing import Optional

ANNOFAB_PROJECT_URL_PREFIX = "https://annofab.com/projects/"
"""Annofabのプロジェクトを表すURLのプレフィックス"""


def get_annofab_project_id_from_url(url: str) -> Optional[str]:
    """ジョブの外部連携情報に設定されたURLからAnnofabプロジェクトのproject_idを取得します。

    Args:
        url: ジョブの外部連携情報であるURL

    Returns:
        Annofabプロジェクトのproject_id。URLからproject_idを取得できない場合は、Noneを返します。
    """
    url = url.strip()
    if not url.startswith(ANNOFAB_PROJECT_URL_PREFIX):
        return None
    tmp = url[len(ANNOFAB_PROJECT_URL_PREFIX) :]
    tmp_array = tmp.split("/")
    if len(tmp_array) == 0:
        # https://annofab.com/projects/foo のケース（末尾にスラッシュなし）
        return tmp
    # https://annofab.com/projects/foo/ のケース（末尾にスラッシュあり）
    return tmp_array[0]
