from .crud import KeycloakCRUD

def hack_rest_roles_remove_endpoint(that, kc):
    custom_delete = that.targets.targets['delete'].copy()
    custom_delete.replaceResource('clients', 'roles-by-id')
    kc.targets.targets['delete'] = custom_delete

    return kc

def new_child(kc, query, child_resource):
    client_id = kc.findFirst(query)['id']
    return KeycloakCRUD.get_child(kc, client_id, child_resource)

class Clients(KeycloakCRUD):

    def secrets(self, client_query):
        obj = super().findFirst(client_query)
        child = KeycloakCRUD.get_child(self, obj['id'], 'client-secret')
        return child

    def roles(self, client_query):
        client_id = super().findFirst(client_query)['id']
        child = KeycloakCRUD.get_child(self, client_id, 'roles')
        return hack_rest_roles_remove_endpoint(self, child)
