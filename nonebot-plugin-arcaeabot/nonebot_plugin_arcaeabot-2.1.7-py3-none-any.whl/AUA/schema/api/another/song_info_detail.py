from typing import Union, List, Optional
from ...basemodel import Base
from ..v5.song_info import SongInfo

"""
{
  "status": 0,
  "content": {
    "song_id": "climax",
    "song_info": [
      {
        "name_en": "Climax",
        "name_jp": "",
        "artist": "USAO",
        "bpm": "190",
        "bpm_base": 190,
        "set": "chunithm_append_1",
        "set_friendly": "CHUNITHM Collaboration",
        "time": 154,
        "side": 1,
        "world_unlock": false,
        "remote_download": true,
        "bg": "chunithmthird_conflict",
        "date": "2021-01-21T00:00:00+00:00",
        "version": 3.5,
        "difficulty": 8,
        "rating": 45,
        "note": 773,
        "chart_designer": "Nitro -EXTRA ROUND-",
        "jacket_designer": "",
        "jacket_override": false,
        "audio_override": false
      },
    # More Song Info
    ]
  }
}
"""


class Content(Base):
    song_id: str
    song_info: Union[List[SongInfo], SongInfo]
    difficulty: int


class SongInfoDetail(Base):
    status: Optional[int]
    message: Optional[str]
    content: Optional[Content]
