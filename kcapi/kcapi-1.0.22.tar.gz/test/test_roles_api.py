import unittest, time
from .testbed import TestBed 

ADMIN_USER = "admin"
ADMIN_PSW  = "admin1234"
REALM = "test_heroes_test"
ENDPOINT = 'https://sso-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'


TEST_REALM = "TESTING"

class Testing_Roles_And_Groups_API(unittest.TestCase):
  
    def testing_roles_creation(self):
        role = {"name": "magic"}
        roles = self.kc.build("roles", self.realm)
        state = roles.create(role).isOk() 
        self.assertTrue(state)

        ret = roles.findFirstByKV('name', 'magic')

        self.assertTrue(ret, "We should get the created role back.")


    def testing_update_roles_creation(self):
        role = {"name": "magic"}
        roles = self.kc.build("roles", self.realm)
        state = roles.create(role).isOk()
        self.assertTrue(state)

        updated_role = {"name": "magic", "description": "aaaa"}
        ret = roles.updateUsingKV('name', 'magic', updated_role)

        magic = roles.findFirstByKV('name', 'magic')
        self.assertEqual(magic['description'], 'aaaa', "The role should be updated.")


    def testing_roles_removal(self):
        roles = self.kc.build("roles", self.realm)

        self.assertTrue(roles.removeFirstByKV("name", "magic"))
        ret = roles.findFirstByKV('name', 'magic')
        
        self.assertEqual(len(ret), 0, 'The role should be deleted')


    def testing_group_API(self):
        group_payload = {"name":"my_group"}
        groups = self.kc.build("groups", self.realm)
        state = groups.create(group_payload).isOk()
        self.assertEqual(state, True)

        ret = groups.findFirstByKV('name', 'my_group')
        self.assertTrue(ret, "We should get the created group (my_group) back.")


    def testing_adding_roles_to_group(self):
        groups = self.kc.build('groups', self.realm)
        self.assertTrue(hasattr(groups, "realmRoles"))

        #TestBed class will create one group called "DC"
        #And three roles called [level-1, level-2, level-3]
        group = {"key":"name", "value": self.groupName}
        roles_mapping = groups.realmRoles(group)
        state = roles_mapping.add(self.roleNames)
        self.assertEqual(state.status, 204, 'We should get a HTTP 204 response from the server')


    def testing_handling_adding_non_existing_roles_to_group(self):
        groups = self.kc.build('groups', self.realm)
        self.assertTrue(hasattr(groups, "realmRoles"))

        # TestBed class will create one group called "DC"
        # And three roles called [level-1, level-2, level-3]
        group = {"key": "name", "value": self.groupName}
        roles_mapping = groups.realmRoles(group)
        fail = False
        error = ""
        try:
            state = roles_mapping.add(['do-not-exist-1'])
        except Exception as E:
            fail = True
            error = str(E)

        self.assertTrue(fail, "We raise an role not found error.")
        self.assertEqual(error, "One or more roles from the provided list: ['do-not-exist-1'] do not exist.")

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed(REALM, ADMIN_USER, ADMIN_PSW, ENDPOINT)
        self.testbed.deleteRealms()
        self.testbed.createRealms()
        self.testbed.createGroups()
        self.kc = self.testbed.getKeycloak()
        self.realm = self.testbed.REALM 
        self.master_realm = self.testbed.getAdminRealm()
        self.roleNames = self.testbed.roleNames
        self.groupName = self.testbed.groupName
        
    @classmethod
    def tearDownClass(self):
        if self.master_realm.exist(TEST_REALM): 
            self.master_realm.remove(TEST_REALM)
            return True
        return True

if __name__ == '__main__':
    unittest.main()
