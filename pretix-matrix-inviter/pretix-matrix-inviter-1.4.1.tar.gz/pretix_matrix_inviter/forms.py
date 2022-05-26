from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    MultipleChoiceField,
    RegexField,
)
from django.utils.translation import ugettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextInput
from pretix.base.forms import SettingsForm

from .helpers import matrix_room_info_for_event


class MatrixInviterForm(SettingsForm):
    matrix_inviter_items = MultipleChoiceField(
        widget=CheckboxSelectMultiple(attrs={"class": "scrolling-multiple-choice"}),
        label=_("Ask Matrix ID for"),
        required=True,
        choices=[],
        help_text=_("These products will ask for a Matrix ID."),
    )
    matrix_inviter_authorization_token = CharField(
        label=_("Access token"),
        strip=True,
        help_text=_(
            "This should be the access token of a user that can invite attendees to the target Room or Space. "
            "Please note that other administrators of this event will be able to see this token, it should not be from "
            "your own Matrix account but from a dedicated Matrix account."
        ),
    )
    matrix_inviter_matrix_server = CharField(
        label=_("Matrix server"),
        strip=True,
        help_text=_("The matrix server the above access token is valid for."),
    )
    matrix_inviter_hint = I18nFormField(
        widget=I18nTextInput,
        label=_("Matrix ID field help text"),
        required=True,
        help_text=_(
            "This will be shown as help text on the Matrix ID field. It is recommended to inform your attendees "
            "which room they will be invited to and what that room will be used for."
        ),
    )
    matrix_inviter_reason = I18nFormField(
        widget=I18nTextInput,
        label=_("Invitation message"),
        required=False,
        help_text=_("This message will be added to the invitation to the Matrix room."),
    )
    matrix_inviter_matrix_room = RegexField(
        label=_("Matrix room"),
        regex="(!|#)[^:]+:.+",
        strip=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["matrix_inviter_items"].choices = [
            (i.pk, i.name) for i in self.obj.items.all()
        ]

        room_info = matrix_room_info_for_event(self.obj)
        if not room_info["room_id"]:
            room_help_text = ""
        elif self.obj.settings.matrix_inviter_matrix_room.startswith("!"):
            if room_info["canonical_alias"]:
                room_help_text = _(
                    '"{name}" (main address: <code>{canonical_alias}</code>)'
                )
            else:
                room_help_text = _('"{name}"')
        else:
            if room_info["canonical_alias"]:
                room_help_text = _(
                    '"{name}" (<code>{room_id}</code>, main address: <code>{canonical_alias}</code>)'
                )
            else:
                room_help_text = _('"{name}" (<code>{room_id}</code>)')
        self.fields["matrix_inviter_matrix_room"].help_text = room_help_text.format_map(
            room_info
        )
