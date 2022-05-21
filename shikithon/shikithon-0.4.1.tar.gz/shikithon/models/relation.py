"""Model for /api/animes/:id/related"""
from typing import Optional

from pydantic import BaseModel

from shikithon.models.anime import Anime
from shikithon.models.manga import Manga


class Relation(BaseModel):
    """Represents relation entity for anime."""
    relation: str
    relation_russian: str
    anime: Optional[Anime]
    manga: Optional[Manga]
