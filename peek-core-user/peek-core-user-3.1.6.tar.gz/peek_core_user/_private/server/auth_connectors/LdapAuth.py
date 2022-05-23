import hashlib
import logging
from typing import List

from peek_core_user._private.server.auth_connectors.InternalAuth import (
    InternalAuth,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.LdapSetting import LdapSetting
from peek_core_user._private.storage.Setting import (
    globalSetting,
    LDAP_VERIFY_SSL,
)
from twisted.cred.error import LoginFailed

__author__ = "synerty"

logger = logging.getLogger(__name__)

import ldap

"""
{'objectClass': [b'top', b'person', b'organizationalPerson', b'user'], 'cn': [b'attest'],
 'givenName': [b'attest'],
 'distinguishedName': [b'CN=attest,OU=testou,DC=synad,DC=synerty,DC=com'],
 'instanceType': [b'4'], 'whenCreated': [b'20170505160836.0Z'],
 'whenChanged': [b'20190606130621.0Z'], 'displayName': [b'attest'],
 'uSNCreated': [b'16498'],
 'memberOf': [b'CN=Domain Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Enterprise Admins,CN=Users,DC=synad,DC=synerty,DC=com',
              b'CN=Administrators,CN=Builtin,DC=synad,DC=synerty,DC=com'],
 'uSNChanged': [b'73784'], 'name': [b'attest'],
 'objectGUID': [b'\xee\x1bV\x8dQ\xackE\x82\xd9%_\x18\xadjO'],
 'userAccountControl': [b'66048'], 'badPwdCount': [b'0'], 'codePage': [b'0'],
 'countryCode': [b'0'], 'badPasswordTime': [b'132042996316396717'], 'lastLogoff': [b'0'],
 'lastLogon': [b'132042996806397639'], 'pwdLastSet': [b'132042997225927009'],
 'primaryGroupID': [b'513'], 'objectSid': [
    b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00D:3|X\x8f\xc7\x08\xe6\xeaV\xc8Q\x04\x00\x00'],
 'adminCount': [b'1'], 'accountExpires': [b'9223372036854775807'], 'logonCount': [b'36'],
 'sAMAccountName': [b'attest'], 'sAMAccountType': [b'805306368'],
 'userPrincipalName': [b'attest@synad.synerty.com'], 'lockoutTime': [b'0'],
 'objectCategory': [b'CN=Person,CN=Schema,CN=Configuration,DC=synad,DC=synerty,DC=com'],
 'dSCorePropagationData': [b'20190606130621.0Z', b'20190606130016.0Z',
                           b'20170506090346.0Z', b'16010101000000.0Z'],
 'lastLogonTimestamp': [b'132042996806397639']}
"""


class LdapNotEnabledError(Exception):
    pass


class LdapAuth:
    FOR_ADMIN = InternalAuth.FOR_ADMIN
    FOR_OFFICE = InternalAuth.FOR_OFFICE
    FOR_FIELD = InternalAuth.FOR_FIELD

    def checkPassBlocking(
        self, dbSession, userName, password, forService: int
    ) -> List[str]:
        """Login User

        :param forService:
        :param dbSession:
        :param userName: The username of the user.
        :param password: The users secret password.
        :rtype
        """

        assert forService in (1, 2, 3), "Unhandled for service type"

        ldapSettings: List[LdapSetting] = dbSession.query(LdapSetting).all()

        if not globalSetting(dbSession, LDAP_VERIFY_SSL):
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        if not ldapSettings:
            raise Exception("No LDAP servers configured.")

        firstException = None

        for ldapSetting in ldapSettings:
            if forService == self.FOR_ADMIN:
                if not ldapSetting.adminEnabled:
                    continue

            elif forService == self.FOR_OFFICE:
                if not ldapSetting.desktopEnabled:
                    continue

            elif forService == self.FOR_FIELD:
                if not ldapSetting.mobileEnabled:
                    continue

            else:
                raise Exception(
                    "InternalAuth:Unhandled forService type %s" % forService
                )

            try:
                return self._tryLdap(dbSession, userName, password, ldapSetting)
            except LoginFailed as e:
                if not firstException:
                    firstException = e

        logger.error("Login failed for %s, %s", userName, str(firstException))

        if firstException:
            raise firstException

        raise LoginFailed("No LDAP providers found for this service")

    def _tryLdap(
        self, dbSession, userName, password, ldapSetting: LdapSetting
    ) -> List[str]:
        try:

            conn = ldap.initialize(ldapSetting.ldapUri)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_REFERRALS, 0)

            # make the connection
            conn.simple_bind_s(
                "%s@%s" % (userName, ldapSetting.ldapDomain), password
            )
            ldapFilter = (
                "(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))"
                % userName
            )

            dcParts = ",".join(
                ["DC=%s" % part for part in ldapSetting.ldapDomain.split(".")]
            )

            ldapBases = []
            if ldapSetting.ldapOUFolders:
                ldapBases += self._makeLdapBase(
                    ldapSetting.ldapOUFolders, userName, "OU"
                )
            if ldapSetting.ldapCNFolders:
                ldapBases += self._makeLdapBase(
                    ldapSetting.ldapCNFolders, userName, "CN"
                )

            if not ldapBases:
                raise LoginFailed("LDAP OU and/or CN search paths must be set.")

            userDetails = None
            for ldapBase in ldapBases:
                ldapBase = "%s,%s" % (ldapBase, dcParts)

                try:
                    # Example Base : 'CN=atuser1,CN=Users,DC=synad,DC=synerty,DC=com'
                    userDetails = conn.search_st(
                        ldapBase, ldap.SCOPE_SUBTREE, ldapFilter, None, 0, 10
                    )

                    if userDetails:
                        break

                except ldap.NO_SUCH_OBJECT:
                    logger.warning("CN or OU doesn't exist : %s", ldapBase)

        except ldap.NO_SUCH_OBJECT:
            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs"
            )

        except ldap.INVALID_CREDENTIALS:
            raise LoginFailed("Username or password is incorrect")

        if not userDetails:
            raise LoginFailed("User doesn't belong to the correct CN/OUs")

        userDetails = userDetails[0][1]

        groups = []
        for memberOf in userDetails["memberOf"]:
            group = memberOf.decode().split(",")[0]
            if "=" in group:
                group = group.split("=")[1]
            groups.append(group)

        userTitle = None
        if userDetails["displayName"]:
            userTitle = userDetails["displayName"][0].decode()

        email = None
        if userDetails["userPrincipalName"]:
            email = userDetails["userPrincipalName"][0].decode()

        userUuid = None
        if userDetails["objectGUID"]:
            md5Hash = hashlib.md5(userDetails["objectGUID"][0])
            userUuid = str(md5Hash.hexdigest())

        if ldapSetting.ldapGroups:
            ldapGroups = set(
                [s.strip() for s in ldapSetting.ldapGroups.split(",")]
            )

            if not ldapGroups & set(groups):
                raise LoginFailed("User is not apart of an authorised group")

        self._makeOrCreateInternalUserBlocking(
            dbSession,
            userName,
            userTitle,
            userUuid,
            email,
            ldapSetting.ldapTitle,
        )

        return groups

    def _makeOrCreateInternalUserBlocking(
        self, dbSession, userName, userTitle, userUuid, email, ldapName
    ):

        internalUser = (
            dbSession.query(InternalUserTuple)
            .filter(InternalUserTuple.userUuid == userUuid)
            .all()
        )

        if internalUser:
            return

        newInternalUser = InternalUserTuple(
            userName=userName,
            userTitle="%s (%s)" % (userTitle, ldapName),
            userUuid=userUuid,
            email=email,
        )

        dbSession.add(newInternalUser)
        dbSession.commit()

    def _makeLdapBase(self, ldapFolders, userName, propertyName):
        try:
            ldapBases = []
            for folder in ldapFolders.split(","):
                folder = folder.strip()
                if not folder:
                    continue

                parts = []
                for part in folder.split("/"):
                    part = part.strip()
                    if not part:
                        continue
                    parts.append("%s=%s" % (propertyName, part))

                ldapBases.append(",".join(reversed(parts)))

            return ldapBases

        except Exception as e:
            logger.error(
                "Login failed for %s, failed to parse LDAP %s Folders setting",
                propertyName,
                userName,
            )

            logger.exception(e)

            raise LoginFailed(
                "An internal error occurred, ask admin to check Attune logs"
            )
