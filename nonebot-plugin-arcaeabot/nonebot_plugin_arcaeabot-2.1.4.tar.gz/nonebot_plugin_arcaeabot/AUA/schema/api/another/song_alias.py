from ...basemodel import Base
from typing import Optional, List

"""
{
  "status": 0,
  "content": {
    "song_id": "climax",
    "alias": [
      "高潮",
      "妖艳魔男",
      "妖艳猛男"
    ]
  }
}
"""


class Content(Base):
    song_id: str
    alias: List[str]


class SongAlias(Base):
    status: Optional[int]
    message: Optional[str]
    content: Optional[Content]
