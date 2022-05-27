import logging

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from .config import UNICEF_EMAIL
from .graph import default_group, Synchronizer, SyncResult
from .models import User

logger = logging.getLogger(__name__)


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)


class UNICEFUserFilter(SimpleListFilter):
    title = 'UNICEF user filter'
    parameter_name = 'email'

    def lookups(self, request, model_admin):
        return [
            ('unicef', 'UNICEF'),
            ('external', 'External'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'unicef':
            return queryset.filter(email__endswith=UNICEF_EMAIL)
        elif self.value() == 'external':
            return queryset.exclude(email__endswith=UNICEF_EMAIL)
        return queryset


@admin.register(User)
class UserAdminPlus(ExtraButtonsMixin, UserAdmin):
    list_display = ['username', 'display_name', 'email', 'is_staff',
                    'is_active', 'is_superuser', 'is_linked', 'last_login']
    list_filter = ['is_superuser', 'is_staff', 'is_active', UNICEFUserFilter]
    search_fields = ['username', 'display_name']
    fieldsets = (
        (None, {'fields': (('username', 'azure_id'), 'password')}),
        (_('Personal info'), {'fields': (('first_name', 'last_name',),
                                         ('email', 'display_name'),
                                         ('job_title',),
                                         )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('azure_id', 'job_title', 'display_name')

    def is_linked(self, obj):
        return bool(obj.azure_id)

    is_linked.boolean = True

    @button(label='Sync')
    def sync_user(self, request, pk):
        obj = self.get_object(request, pk)
        try:
            syncronizer = Synchronizer()
            syncronizer.sync_user(obj)
        except BaseException as e:
            self.message_user(request, str(e), messages.ERROR)

        self.message_user(request, "User synchronized")

    @button(label='Link user')
    def link_user_data(self, request, pk):
        opts = self.model._meta
        ctx = {
            'opts': opts,
            'app_label': 'security',
            'change': True,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,
            'has_add_permission': False,
            'has_change_permission': True,
        }
        obj = self.get_object(request, pk)
        syncronizer = Synchronizer()
        try:
            if request.method == 'POST':
                if request.POST.get('selection'):
                    data = syncronizer.get_user(request.POST.get('selection'))
                    syncronizer.sync_user(obj, data['id'])
                    self.message_user(request, "User linked")
                    return None
                else:
                    ctx['message'] = 'Select one entry to link'

            data = syncronizer.search_users(obj)
            ctx['data'] = data
            return TemplateResponse(request, 'admin/link_user.html', ctx)

        except BaseException as e:
            self.message_user(request, str(e), messages.ERROR)

    @button()
    def load(self, request):
        opts = self.model._meta
        ctx = {
            'opts': opts,
            'app_label': 'security',
            'change': True,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,
            'has_add_permission': False,
            'has_change_permission': True,
        }
        if request.method == 'POST':
            form = LoadUsersForm(request.POST)
            if form.is_valid():
                synchronizer = Synchronizer()
                emails = form.cleaned_data['emails'].split()
                total_results = SyncResult()
                for email in emails:
                    result = synchronizer.fetch_users("startswith(mail,'%s')" % email,
                                                      callback=default_group)
                    total_results += result
                self.message_user(request,
                                  f"{len(total_results.created)} users have been created, "
                                  f"{len(total_results.updated)} updated. "
                                  f"{len(total_results.skipped)} invalid entries found.")
        else:
            form = LoadUsersForm()
        ctx['form'] = form
        return TemplateResponse(request, 'admin/load_users.html', ctx)
