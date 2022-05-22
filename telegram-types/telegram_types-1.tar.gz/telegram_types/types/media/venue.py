from typing import Optional

from .location import Location
from telegram_types.base import Base


class Venue(Base):
    location: Location
    title: str
    address: str
    foursquare_id: Optional[str]
    foursquare_type: Optional[str]
