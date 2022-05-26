# -*- coding: utf-8 -*-

from pprint import pprint

from django import forms
from annoying.decorators import autostrip

@autostrip
class NodeEditForm(forms.Form):
    hostname = forms.CharField()
    enabled = forms.BooleanField(required=False)
    is_application = forms.BooleanField(required=False)
    is_db = forms.BooleanField(required=False)

    admin_username = forms.CharField(required=False)
    admin_password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=True))

    replica_username = forms.CharField(required=False)
    replica_password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=True))

    def clean_admin_username(self):
        return self.cleaned_data['admin_username'] or None
    
    def clean_admin_password(self):
        return self.cleaned_data['admin_password'] or None
    
    def clean_replica_username(self):
        return self.cleaned_data['replica_username'] or None

    def clean_replica_password(self):
        return self.cleaned_data['replica_password'] or None

@autostrip
class ConfigForm(forms.Form):
    databases = forms.CharField(help_text=u"Comma-separated list of databases (plain names, not config-keys)", required=False)
    admins_names = forms.CharField(help_text=u"Comma-separated list of admin users", required=False)
    admins_roles = forms.CharField(help_text=u"Comma-separated list of admin roles", required=False)
    members_names = forms.CharField(help_text=u"Comma-separated list of member users", required=False)
    members_roles = forms.CharField(help_text=u"Comma-separated list of member roles", required=False)

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            kwargs['initial']['admins_names'] = ', '.join(kwargs['initial']['security']['admins']['names'])
            kwargs['initial']['admins_roles'] = ', '.join(kwargs['initial']['security']['admins']['roles'])
            kwargs['initial']['members_names'] = ', '.join(kwargs['initial']['security']['members']['names'])
            kwargs['initial']['members_roles'] = ', '.join(kwargs['initial']['security']['members']['roles'])
            kwargs['initial']['databases'] = ', '.join(kwargs['initial']['databases'])

        super(ConfigForm, self).__init__(*args, **kwargs)
    
    def clean_databases(self):
        return sorted([db.strip() for db in self.cleaned_data['databases'].split(',') if db.strip()])

    def clean_admins_names(self):
        return [name.strip() for name in self.cleaned_data['admins_names'].split(',') if name.strip()]
        
    def clean_admins_roles(self):
        return [name.strip() for name in self.cleaned_data['admins_roles'].split(',') if name.strip()]
        
    def clean_members_names(self):
        return [name.strip() for name in self.cleaned_data['members_names'].split(',') if name.strip()]
        
    def clean_members_roles(self):
        return [name.strip() for name in self.cleaned_data['members_roles'].split(',') if name.strip()]
    
    
    def clean(self):
        data = super(ConfigForm, self).clean()
        
        data['security'] = {
            'admins': {
                'names': data.get('admins_names', []),
                'roles': data.get('admins_roles', []),
            },
            'members': {
                'names': data.get('members_names', []),
                'roles': data.get('members_roles', []),
            }
        }
        
        if 'admins_names' in data:
            del(data['admins_names'])
        
        if 'admins_roles' in data:
            del(data['admins_roles'])
        
        if 'members_names' in data:
            del(data['members_names'])
            
        if 'members_roles' in data:
            del(data['members_roles'])
        
        return data
    
