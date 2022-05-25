from django.core.management.base import BaseCommand
from allianceauth.authentication.models import State
from blacklist import app_settings
from blacklist.models import EveNote


class Command(BaseCommand):
    help = 'Sync existing members from the Blacklist State into the Blacklist State.'

    def handle(self, *args, **options):
        self.stdout.write("Syncing existing members from the Blacklist State. This may be slow if you have thousands.")
        blacklist_name = app_settings.BLACKLIST_STATE_NAME
        member_chars = State.objects.get(name=blacklist_name).member_characters.all()
        member_corps = State.objects.get(name=blacklist_name).member_corporations.all()
        member_allis = State.objects.get(name=blacklist_name).member_alliances.all()

        for c in member_chars:
            en = EveNote.objects.filter(eve_id=c.character_id, blacklisted=True)

            if not en.exists():
                EveNote.objects.create(blacklisted=True,
                                       reason="Blacklisted By Admin!",
                                       added_by="Admin",
                                       eve_catagory="character",
                                       eve_id=c.character_id,
                                       eve_name=c.character_name,
                                       corporation_id=c.corporation_id,
                                       corporation_name=c.corporation_name,
                                       alliance_id=c.alliance_id,
                                       alliance_name=c.alliance_name)

                self.stdout.write(f"Created Blacklist Note for Character: {c}")
            else:
                self.stdout.write(f"Blacklist Note Exists for Character: {c}")

        for c in member_corps:
            en = EveNote.objects.filter(eve_id=c.corporation_id, blacklisted=True)

            if not en.exists():
                EveNote.objects.create(blacklisted=True,
                                       reason="Blacklisted By Admin!",
                                       added_by="Admin",
                                       eve_catagory="corporation",
                                       eve_id=c.corporation_id,
                                       eve_name=c.corporation_name,
                                       alliance_id=c.alliance.alliance_id,
                                       alliance_name=c.alliance.alliance_name)

                self.stdout.write(f"Created Blacklist Note for Corp: {c}")
            else:
                self.stdout.write(f"Blacklist Note Exists for Corp: {c}")

        for a in member_allis:
            en = EveNote.objects.filter(eve_id=a.alliance_id, blacklisted=True)

            if not en.exists():
                EveNote.objects.create(blacklisted=True,
                                       reason="Blacklisted By Admin!",
                                       added_by="Admin",
                                       eve_catagory="alliance",
                                       eve_id=a.alliance_id,
                                       eve_name=a.alliance_name)

                self.stdout.write(f"Created Blacklist Note for Alliance: {a}")
            else:
                self.stdout.write(f"Blacklist Note Exists for Alliance: {a}")

        self.stdout.write("Completed!")
