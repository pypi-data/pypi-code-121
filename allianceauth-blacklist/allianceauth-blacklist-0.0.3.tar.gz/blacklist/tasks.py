from allianceauth.services.hooks import get_extension_logger

from celery import shared_task
from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveCharacter, EveAllianceInfo, EveCorporationInfo
from . import models
from . import app_settings

logger = get_extension_logger(__name__)


@shared_task
def run_blacklist_update(note_id):
    blk_state = State.objects.get(name=app_settings.BLACKLIST_STATE_NAME)
    instance = models.EveNote.objects.get(pk=note_id)
    if instance.eve_catagory == "character":
        logger.debug(f"Checking Character for blacklist '{instance.eve_name}'")
        eve_char = EveCharacter.objects.get_character_by_id(instance.eve_id)
        blacklist = instance.blacklisted
        exists = blk_state.member_characters.filter(character_id=instance.eve_id).exists()
        if blacklist and exists:
            logger.debug(f"'{instance.eve_name}'' is already Blacklisted")
        elif blacklist and not exists:
            if eve_char is None:
                logger.debug(f"Creating new Auth Model for '{instance.eve_name}'")
                eve_char = EveCharacter.objects.create_character(instance.eve_id)
            logger.debug(f"Blacklisted '{instance.eve_name}'")
            blk_state.member_characters.add(eve_char)
        elif not blacklist and exists:
            logger.debug(f"Removing '{instance.eve_name}' from Blacklist")
            blk_state.member_characters.remove(eve_char)

    if instance.eve_catagory == "corporation":
        logger.debug(f"Checking Corporation for blacklist '{instance.eve_name}'")
        eve_corp = EveCorporationInfo.objects.filter(corporation_id=instance.eve_id)
        blacklist = instance.blacklisted
        exists = blk_state.member_corporations.filter(corporation_id=instance.eve_id).exists()
        if blacklist and exists:
            logger.debug(f"'{instance.eve_name}'' is already Blacklisted")
        elif blacklist and not exists:
            if eve_corp.exists() is False:
                logger.debug(f"Creating new Auth Model for '{instance.eve_name}'")
                eve_corp = EveCorporationInfo.objects.create_corporation(instance.eve_id)
            else:
                eve_corp = eve_corp.first()
            logger.debug(f"Blacklisted '{instance.eve_name}'")
            blk_state.member_corporations.add(eve_corp)
        elif not blacklist and exists:
            logger.debug(f"Removing '{instance.eve_name}' from Blacklist")
            blk_state.member_corporations.remove(eve_corp.first())

    if instance.eve_catagory == "alliance":
        logger.debug(f"Checking Alliance for blacklist '{instance.eve_name}'")
        eve_alli = EveAllianceInfo.objects.filter(alliance_id=instance.eve_id)
        blacklist = instance.blacklisted
        exists = blk_state.member_alliances.filter(alliance_id=instance.eve_id).exists()
        if blacklist and exists:
            logger.debug(f"'{instance.eve_name}'' is already Blacklisted")
        elif blacklist and not exists:
            if eve_alli.exists() is False:
                logger.debug(f"Creating new Auth Model for '{instance.eve_name}'")
                eve_alli = EveAllianceInfo.objects.create_alliance(instance.eve_id)
            else:
                eve_alli = eve_alli.first()
            logger.debug(f"Blacklisted '{instance.eve_name}'")
            blk_state.member_alliances.add(eve_alli)
        elif not blacklist and exists:
            logger.debug(f"Removing '{instance.eve_name}' from Blacklist")
            blk_state.member_alliances.remove(eve_alli.first())
