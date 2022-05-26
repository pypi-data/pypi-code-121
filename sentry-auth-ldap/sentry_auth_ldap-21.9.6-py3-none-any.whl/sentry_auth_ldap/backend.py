from django_auth_ldap.backend import LDAPBackend
from django.conf import settings
from django.db.models import Q
from sentry.models import (
    Organization,
    OrganizationMember,
    UserOption,
)


def _get_effective_sentry_role(group_names):
    role_priority_order = [
        'member',
        'admin',
        'manager',
        'owner',
    ]

    role_mapping = getattr(settings, 'AUTH_LDAP_SENTRY_GROUP_ROLE_MAPPING', None)

    if not group_names or not role_mapping:
        return None

    applicable_roles = [role for role, groups in role_mapping.items() if group_names.intersection(groups)]

    if not applicable_roles:
        return None

    highest_role = [role for role in role_priority_order if role in applicable_roles][-1]

    return highest_role


class SentryLdapBackend(LDAPBackend):
    def get_or_build_user(self, username, ldap_user):
        (user, built) = super().get_or_build_user(username, ldap_user)
        if not built:
            return (user, built)

        user.is_managed = True

        # Add the user email address
        try:
            from sentry.models import (UserEmail)
        except ImportError:
            pass
        else:
            mail_attr = ldap_user.attrs.get('mail')
            if mail_attr:
                email = mail_attr[0]
            elif hasattr(settings, 'AUTH_LDAP_DEFAULT_EMAIL_DOMAIN'):
                email = username + '@' + settings.AUTH_LDAP_DEFAULT_EMAIL_DOMAIN
            else:
                email = None

            if email:
                user.email = email

            user.save()

            if email:
                UserEmail.objects.get_or_create(user=user, email=email)

        # Check to see if we need to add the user to an organization
        if not settings.AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION:
            return (user, built)

        # Find the default organization
        organizations = Organization.objects.filter(name=settings.AUTH_LDAP_DEFAULT_SENTRY_ORGANIZATION)

        if not organizations or len(organizations) < 1:
            return (user, built)

        member_role = _get_effective_sentry_role(ldap_user.group_names)
        if not member_role:
            member_role = getattr(settings, 'AUTH_LDAP_SENTRY_ORGANIZATION_ROLE_TYPE', None)

        has_global_access = getattr(settings, 'AUTH_LDAP_SENTRY_ORGANIZATION_GLOBAL_ACCESS', False)

        # Add the user to the organization with global access
        OrganizationMember.objects.create(
            organization=organizations[0],
            user=user,
            role=member_role,
            has_global_access=has_global_access,
            flags=getattr(OrganizationMember.flags, 'sso:linked'),
        )

        if not getattr(settings, 'AUTH_LDAP_SENTRY_SUBSCRIBE_BY_DEFAULT', True):
            UserOption.objects.set_value(
                user=user,
                project=None,
                key='subscribe_by_default',
                value='0',
            )

        return (user, built)
