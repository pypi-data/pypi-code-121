from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.db import models


class UserEveCharacter(models.Model):
    """The Eve character an user was created with."""

    CHARACTER_IMAGE_URL_BASE = "https://images.evetech.net/characters/"
    DEFAULT_PORTRAIT_SIZE = 32

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eve_character"
    )
    # the character fields from esi.models.Token needs to be doubled here,
    # because the esi app might delete tokens automatically (e.g. invalid tokens)
    character_id = models.PositiveIntegerField()
    character_name = models.CharField(max_length=255)
    character_owner_hash = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.character_name

    def character_portrait_url(self, size: int = DEFAULT_PORTRAIT_SIZE) -> str:
        """Return the image URL of this user's character portrait"""
        return self.generic_character_portrait_url(self.character_id, size)

    @classmethod
    def generic_character_portrait_url(
        cls, character_id: int, size: int = DEFAULT_PORTRAIT_SIZE
    ) -> str:
        """Return the image URL of the given character ID's portrait"""
        size = int(size)
        if not size or size < 32 or size > 1024 or (size & (size - 1) != 0):
            raise ValueError(f"Invalid size: {size}")
        path = f"{int(character_id)}/portrait"
        query = urlencode({"size": size})
        return urljoin(cls.CHARACTER_IMAGE_URL_BASE, f"{path}?{query}")
