from .crud import KeycloakCRUD
from .targets import Targets
from .recovery import add_failiure_recovery_decorator

def AuthenticationFlowURLBuilder(url):
    return Targets.makeWithURL(url).addResources(['flows'])

def add_remote_id_to_payload(kc, payload):
    child_nodes = kc.all()
    for child in child_nodes:
        if child['displayName'] == payload['displayName'] and child['index'] == payload['index'] and child['level'] == \
                payload['level']:
            payload['id'] = child['id']
            return payload


def adjustments_only_update(kc):
    crud_update = kc.update
    return lambda object_id, payload: crud_update(None, add_remote_id_to_payload(kc, payload))


def update_by_doing_delete_and_create(kc, payload):
    unique_identifier = payload['alias'] if 'alias' in payload else payload['displayName']
    key = 'alias' if 'alias' in payload else 'displayName'

    kc.removeFirstByKV(key, unique_identifier)
    kc.create(payload).isOk()
    return True


# These flows cannot be deleted, this mean the user can only adjust parameters.
def is_flow_built_in(root_node):
    kc_default_not_removable_flows = ['browser', 'direct grant', 'registration', 'reset credentials', 'clients',
                                      'first broker login', 'docker auth', 'http challenge']

    return root_node['alias'] in kc_default_not_removable_flows

def choose_update_strategy(kc, root_node):

    if is_flow_built_in(root_node):
        return adjustments_only_update(kc)
    else:
        return kc.update



# The keycloak API is a bit crazy here they add with:
# Post /parentId/executions/execution 
# 
# But they delete with: 
#
# DELETE /executions/<id>
#
# Sadly we need to customize the URL's in order to make it work.
#

def build_action(kc, root_node, action_type):
    parent = root_node['alias']
    resources = [parent, 'executions']

    t = kc.targets.targets
    t['create'].addResources(resources + [action_type])
    t['update'].addResources(resources)
    t['read'].addResources(resources)
    t['delete'].replaceResource('flows', 'executions')

    # Sadly the REST Endpoint to update executions components inside an authentication flow is somewhat broken.
    kc.update = choose_update_strategy(kc, root_node)
    return kc


class AuthenticationFlows(KeycloakCRUD):
    def setURL(self, url):
        super().setURL(url)
        self.targets.addResources(['flows'])

    def _load(self, token, targets):
        flow = KeycloakCRUD()
        flow.token = token
        flow.targets = targets.copy()
        return add_failiure_recovery_decorator(flow)

    def is_built_in(self, root_node):
        return is_flow_built_in(root_node)


    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/flow
    def flows(self, auth_flow):
        flow = self._load(self.token, self.targets)

        return build_action(
            kc=flow,
            root_node=auth_flow,
            action_type='flow')

    # Generate a CRUD object pointing to /realm/<realm>/authentication/flow_alias/executions/execution
    def executions(self, execution):
        flow = self._load(self.token, self.targets)

        return build_action(
            kc=flow,
            root_node=execution,
            action_type='execution')
