from django.test import TestCase, RequestFactory
from django.urls import reverse
from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from allianceauth.authentication.models import CharacterOwnership
from django.contrib.auth.models import User
from django.utils import timezone
from securegroups import models as gb_models
from django.contrib.auth.models import Group
from ..models import BlacklistFilter, EveNote


class TestBlacklistFilters(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        EveCharacter.objects.all().delete()
        User.objects.all().delete()
        CharacterOwnership.objects.all().delete()
        gb_models.SmartGroup.objects.all().delete()
        userids = range(1, 11)

        cls.blacklist_filter = BlacklistFilter.objects.create(
            name="Test Blacklist", description="NO BLACKLISTS!!!!"
        )
        _sf = gb_models.SmartFilter.objects.all().last()

        users = []
        characters = []
        for uid in userids:
            user = AuthUtils.create_user(f"User_{uid}")
            main_char = AuthUtils.add_main_character_2(
                user,
                f"Main {uid}",
                uid,
                corp_id=1,
                corp_name="Test Corp 1",
                corp_ticker="TST1",

            )
            CharacterOwnership.objects.create(
                user=user, character=main_char, owner_hash=f"main{uid}"
            )

            characters.append(main_char)
            users.append(user)

        # add some extra characters to users in 2 corps/alliance
        for uid in range(0, 5):  # test corp 2
            character = EveCharacter.objects.create(
                character_name=f"Alt {uid}",
                character_id=11 + uid,
                corporation_name="Test Corp 2",
                corporation_id=2,
                corporation_ticker="TST2",
                alliance_id=9,
                alliance_name="Test Alliance 9",
                alliance_ticker="TSTA9",

            )
            CharacterOwnership.objects.create(
                character=character, user=users[uid], owner_hash=f"ownalt{11+uid}"
            )
            characters.append(character)

        for uid in range(5, 10):  # Test alliance 1
            character = EveCharacter.objects.create(
                character_name=f"Alt {uid}",
                character_id=11 + uid,
                corporation_name="Test Corp 3",
                corporation_id=3,
                corporation_ticker="TST3",
                alliance_id=5,
                alliance_name="Test Alliance 1",
                alliance_ticker="TSTA1",
            )
            CharacterOwnership.objects.create(
                character=character, user=users[uid], owner_hash=f"ownalt{11+uid}"
            )
            characters.append(character)

        cls.char_evenote = EveNote.objects.create(
            eve_id=11,
            eve_name="Alt 11",
            eve_catagory='character',
            blacklisted=False,
            added_by="Tests",
            added_at=timezone.now(),
            reason="blacklist Test"
        )

        cls.corp_evenote = EveNote.objects.create(
            eve_id=3,
            eve_name="Corp 3",
            eve_catagory='corporation',
            blacklisted=False,
            added_by="Tests",
            added_at=timezone.now(),
            reason="blacklist Test"
        )

        cls.alli_evenote = EveNote.objects.create(
            eve_id=5,
            eve_name="Alli 5",
            eve_catagory='alliance',
            blacklisted=False,
            added_by="Tests",
            added_at=timezone.now(),
            reason="blacklist Test"
        )

    def test_no_blacklists(self):
        users = {}
        for user in User.objects.all():

            users[user.pk] = None

        tests = {}
        for k, u in users.items():
            tests[k] = self.blacklist_filter.process_filter(
                User.objects.get(pk=k))

        self.assertTrue(tests[1])
        self.assertTrue(tests[2])
        self.assertTrue(tests[3])
        self.assertTrue(tests[4])
        self.assertTrue(tests[5])
        self.assertTrue(tests[6])
        self.assertTrue(tests[7])
        self.assertTrue(tests[8])
        self.assertTrue(tests[9])
        self.assertTrue(tests[10])

    def test_char_blacklists(self):
        self.char_evenote.blacklisted = True
        self.char_evenote.save()
        users = []
        for user in User.objects.all():

            users.append(user.pk)

        tests = self.blacklist_filter.audit_filter(User.objects.filter(id__in=users))

        self.assertFalse(tests[1]['check'])
        self.assertTrue(tests[2]['check'])
        self.assertTrue(tests[3]['check'])
        self.assertTrue(tests[4]['check'])
        self.assertTrue(tests[5]['check'])
        self.assertTrue(tests[6]['check'])
        self.assertTrue(tests[7]['check'])
        self.assertTrue(tests[8]['check'])
        self.assertTrue(tests[9]['check'])
        self.assertTrue(tests[10]['check'])

    def test_corp_blacklists(self):
        self.corp_evenote.blacklisted = True
        self.corp_evenote.save()
        users = {}
        for user in User.objects.all():

            users[user.pk] = None

        tests = {}
        for k, u in users.items():
            tests[k] = self.blacklist_filter.process_filter(
                User.objects.get(pk=k))

        self.assertTrue(tests[1])
        self.assertTrue(tests[2])
        self.assertTrue(tests[3])
        self.assertTrue(tests[4])
        self.assertTrue(tests[5])
        self.assertFalse(tests[6])
        self.assertFalse(tests[7])
        self.assertFalse(tests[8])
        self.assertFalse(tests[9])
        self.assertFalse(tests[10])

    def test_alli_blacklists(self):
        self.alli_evenote.blacklisted = True
        self.alli_evenote.save()
        users = {}
        for user in User.objects.all():
            print
            users[user.pk] = None

        tests = {}
        for k, u in users.items():
            tests[k] = self.blacklist_filter.process_filter(
                User.objects.get(pk=k))

        self.assertTrue(tests[1])
        self.assertTrue(tests[2])
        self.assertTrue(tests[3])
        self.assertTrue(tests[4])
        self.assertTrue(tests[5])
        self.assertFalse(tests[6])
        self.assertFalse(tests[7])
        self.assertFalse(tests[8])
        self.assertFalse(tests[9])
        self.assertFalse(tests[10])
