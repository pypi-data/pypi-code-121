from ...basemodel import Base
from ..v5.song_info import SongInfo
from typing import List, Optional, Union

"""
{
  "status": 0,
  "content": {
    "song_id": "seclusion",
    "difficulty": 0,
    "song_info": {
      "name_en": "Seclusion",
      "name_jp": "",
      "artist": "Laur feat. Sennzai",
      "bpm": "175",
      "bpm_base": 175,
      "set": "observer",
      "set_friendly": "Esoteric Order",
      "time": 138,
      "side": 1,
      "world_unlock": true,
      "remote_download": true,
      "bg": "observer_conflict",
      "date": "2021-07-21T00:00:03+00:00",
      "version": 3.7,
      "difficulty": 8,
      "rating": 40,
      "note": 544,
      "chart_designer": "Exschwasion",
      "jacket_designer": "海鵜げそ",
      "jacket_override": false,
      "audio_override": false
    }
  }
}
"""


class Content(Base):
    song_id: str
    difficulty: int
    song_info: Union[SongInfo, List[SongInfo]]


class SongRandom(Base):
    status: Optional[int]
    message: Optional[str]
    content: Optional[Content]
