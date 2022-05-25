from django.db import models
from allianceauth.authentication.models import CharacterOwnership
from django.contrib.auth.models import User
from django.db.models import Q
from collections import defaultdict


class EveNote(models.Model):
    eve_id = models.IntegerField()
    eve_name = models.CharField(max_length=500)
    eve_catagory = models.CharField(max_length=30)

    blacklisted = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)

    added_by = models.CharField(max_length=500)
    added_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    # character additions
    corporation_id = models.IntegerField(null=True, default=None)
    corporation_name = models.CharField(max_length=500, null=True, default=None)

    # corp/character additions
    alliance_id = models.IntegerField(null=True, default=None)
    alliance_name = models.CharField(max_length=500, null=True, default=None)

    def __str__(self):
        return "%s added by: %s" % (self.eve_name, self.added_by)

    class Meta:
        permissions = (
            # View Perms
            ('view_basic_eve_notes', 'Can View own corps notes'),
            ('view_eve_blacklist', 'Can View the Blacklist'),
            ('view_eve_notes', 'Can view all eve notes'),
            # Add Perms
            ('add_basic_eve_notes', 'Can Add own corp members to notes'),
            ('add_new_eve_notes', 'Can add new eve notes'),
            ('add_to_blacklist', 'Can add to Blacklist'),
            # Higher Level Perms
            ('view_restricted_eve_notes', 'Can View restricted eve notes'),
            ('add_restricted_eve_notes', 'Can Add restricted eve notes'),
        )


class EveNoteComment(models.Model):
    eve_note = models.ForeignKey(EveNote, on_delete=models.CASCADE, related_name='comment')
    added_by = models.CharField(max_length=500)
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
    restricted = models.BooleanField(default=False)

    def __str__(self):
        return "Comment on: %s added by: %s" % (self.eve_note.eve_name, self.added_by)

    class Meta:
        permissions = (
            # View
            ('view_eve_note_comments', 'Can view eve note comments'),
            ('view_eve_note_restricted_comments', 'Can view restricted eve note comments'),
            # Add
            ('add_new_eve_note_comments', 'Can add comments on eve notes'),
            ('add_new_eve_note_restricted_comments', 'Can add new restricted comments to eve notes'),
        )


class FilterBase(models.Model):

    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}: {self.description}"

    def process_filter(self, user: User):
        raise NotImplementedError("Please Create a filter function!")

    def audit_filter(self, user: User):
        raise NotImplementedError("Please Create a audit function!")


class BlacklistFilter(FilterBase):
    class Meta:
        verbose_name = "Smart Filter: User Has Blacklisted Char"
        verbose_name_plural = verbose_name

    def process_filter(self, user: User):
        return self.audit_filter(User.objects.filter(pk=user.pk))[user.pk]['check']

    def audit_filter(self, users):
        blacklisted_char = EveNote.objects.filter(blacklisted=True,
                                                  eve_catagory='character').values('eve_id')
        blacklisted_corp = EveNote.objects.filter(blacklisted=True,
                                                  eve_catagory='corporation').values('eve_id')
        blacklisted_alli = EveNote.objects.filter(blacklisted=True,
                                                  eve_catagory='alliance').values('eve_id')
        co = CharacterOwnership.objects.filter((
            Q(character__character_id__in=blacklisted_char) |
            Q(character__corporation_id__in=blacklisted_corp) |
            Q(character__alliance_id__in=blacklisted_alli)),
            user__in=users).values('user__id', 'character__character_name')

        chars = defaultdict(list)
        for c in co:
            chars[c['user__id']].append(c['character__character_name'])

        output = defaultdict(lambda: {"message": "", "check": True})
        for c, char_list in chars.items():
            output[c] = {"message": ", ".join(char_list), "check": False}
        return output
