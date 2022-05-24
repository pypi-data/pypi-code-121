from datetime import datetime

from django.utils import translation


def get_participant_from_path_or_none(path):
    from otree.models import Participant
    from django.conf import settings

    # expecting '/p/<participant_code>/foo/bar/..'
    try:
        participant_code = path.split("/")[2]
        participant = Participant.objects.filter(code=participant_code).last()
        # activate user-specific language
        translation.activate(participant.vars.get("lang", settings.LANGUAGE_CODE))
        return participant
    except:
        return None


def get_participant_last_player_or_none(participant):
    players = participant.get_players()
    if len(players):
        return players[-1]
    return None


def get_error_code(participant=None):
    timestamp = datetime.now().isoformat()
    if participant and participant.label:
        return "{}-{}".format(participant.label, timestamp)
    else:
        return timestamp
