from ldap3 import Server, Connection, SAFE_SYNC, ALL, NTLM, ALL_OPERATIONAL_ATTRIBUTES
from ldap3 import Reader, ObjectDef, BASE, SUBTREE, MODIFY_REPLACE

_DEFAULT_ATTRIBUTES = ['cn', 'c', 'title', 'physicalDeliveryOfficeName', 'telephoneNumber', 'distinguishedName', 'instanceType',
                       'whenCreated', 'whenChanged', 'uSNCreated', 'uSNChanged', 'co', 'department', 'company', 'personalTitle',
                       'givenName', 'initials', 'middleName', 'sn', 'name', 'displayName', 'objectGUID', 'userAccountControl',
                       'badPwdCount', 'codePage', 'countryCode', 'primaryGroupID', 'objectSid', 'logonCount', 'sAMAccountName',
                       'sAMAccountType', 'userPrincipalName', 'objectCategory', 'mail', 'homePhone']


class ActiveDirectory(object):
    def __init__(self, host, user, password):
        self.server = Server(host, get_info=ALL)
        self.conn = Connection(self.server,
                                    user=user,
                                    password=password,
                                    auto_bind=True,
                                    client_strategy=SAFE_SYNC,  #Very important
                                    authentication=NTLM)
        # if not self.conn.bind():
        #     print('error in bind', self.conn.result)
        # print (f"user:{self.conn.extend.standard.who_am_i()}")
        # print (f"schema: {self.server.schema.object_classes['Person']}\r\n")

    def search_user(self, user):
        """
        :param user: user data in dictionary format, with "samaccountname" as identifier
        :return: status: A boolean value to indicate if the request is successful or not
        :return: message: If the status is True, then return the data, otherwise return the error message
        The search() function returns a tuple of four elements: status, result, response and request.
                    status: states if the operation was successful
                    result: the LDAP result of the operation
                    response: the response of a LDAP Search Operation
                    request: the original request of the operation
        """
        samaccountname = user['sAMAccountName']
        if 'search_fields' in user:
            search_fields = user['search_fields']
        elif 'changed_fields' in user:
            search_fields = [k for k in user['changed_fields'].keys()]
        else:
            search_fields = _DEFAULT_ATTRIBUTES

        status, result, response, _ = self.conn.search(
            search_base=f'CN={samaccountname},CN=Users,DC=salureconnect-agent,DC=local',
            search_filter='(objectClass=*)',  # required
            search_scope=BASE,
            attributes=search_fields)
        if not status:
            message = {samaccountname: result['description']}
        else:
            message = {samaccountname: dict(response[0]['attributes'])}
        return status, message


    def add_user(self, user):
        """
        Add a new user to the active directory.
        dn: distinguished name is the identifier for each command,
        object_class: the class of the ldap entry. To add a user use object_class=['top','person','organizationalPerson','user']
                        Update this field to add department or organizationUnit.
        it is the most important variable and is mandatory for almost every command.
        :return: status: A boolean value to indicate if the request is successful or not
        :return: message: If the status is True, then return the data, otherwise return the error message
        """
        samaccountname = user['sAMAccountName']
        status, result, response, _ = self.conn.add(dn=f'CN={samaccountname},CN=Users,DC=salureconnect-agent,DC=local',
                      object_class=['top','person','organizationalPerson','user'],
                      attributes=user,
                      controls=None)
        if not status:
            message = {samaccountname: result['description']}
        else:
            status, message = self.search_user(user)
        return status, message


    def modify_user(self, user):
        """
        Modify a new user to the active directory.
        :param: user data in dict() format, which contains the samaccountname as identifier,
                and changed_fields with new values to indicate the attributes to be changed
        dn: distinguished name is the identifier for each command.
        changes:
        :return: status: A boolean value to indicate if the request is successful or not
        :return: message: If the status is True, then return the data, otherwise return the error message
        """
        samaccountname = user['sAMAccountName']
        changes = {k: [(MODIFY_REPLACE,[v])] for k, v in user['changed_fields'].items()}
        dn = f"CN={samaccountname},CN=Users,DC=salureconnect-agent,DC=local"
        status, result, response, _ =self.conn.modify(dn=dn, changes=changes)
        if not status:
            message = {samaccountname: result['description']}
        else:
            status, message = self.search_user(user)
        return status, message
