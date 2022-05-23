from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from djangoldp.admin import DjangoLDPUserAdmin
from djangoldp_account.models import LDPUser
from .models import Account, ChatProfile


class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class LDPUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = LDPUser


class AccountInline(admin.StackedInline):
    model = Account
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink', 'slug')
    extra = 0


class ChatProfileInline(admin.StackedInline):
    model = ChatProfile
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink', 'slug')
    extra = 0


class LDPUserAdmin(DjangoLDPUserAdmin):
    exclude = ('is_backlink', 'allow_create_backlink')
    form = LDPUserChangeForm

    inlines = DjangoLDPUserAdmin.inlines + [
        AccountInline,
        ChatProfileInline
    ]

    fieldsets = DjangoLDPUserAdmin.fieldsets + (
        (None, {'fields': ('default_redirect_uri',)}),
    )
    add_fieldsets = DjangoLDPUserAdmin.add_fieldsets + (
        (None, {'fields': ('email',)}),
    )


admin.site.register(LDPUser, LDPUserAdmin)
admin.site.register(Account, EmptyAdmin)
admin.site.register(ChatProfile, EmptyAdmin)