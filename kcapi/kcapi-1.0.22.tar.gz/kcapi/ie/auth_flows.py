def create_flow(flow):
    alias = flow['displayName']
    pid = None if not 'provider' in flow else flow['providerId']
    provider = 'registration-page-flow' if not pid else pid
    flow_type = 'basic-flow' if not pid else 'form-flow'

    # WARN: The value description is not well validated in Keycloak, it can return 500.
    return {
        "alias": alias,
        "type": flow_type,
        "description": "empty",
        "provider": provider,
    }


def get_executions(execution):
    provider = execution['providerId']
    return {'provider': provider}


def is_auth_flow(body):
    return 'authenticationFlow' in body


def get_node_level(node):
    return node['level']


def consistent(parent, flow):
    published_flows = parent.all()

    for publishedFlow in published_flows:
        resource_id = False

        if 'providerId' in publishedFlow and 'providerId' in flow:
            resource_id = publishedFlow['providerId'] == flow['providerId']
        else:
            resource_id = publishedFlow['displayName'] == flow['displayName']

        level_is_equal = publishedFlow['level'] == flow['level']
        index_is_equal = publishedFlow['index'] == flow['index']

        if resource_id and level_is_equal and index_is_equal:
            publishedFlow['requirement'] = flow['requirement']
            parent.update(None, publishedFlow).isOk()
            return True

    return False


def get_node_identity_pair(root_node):
    key = 'alias' if 'alias' in root_node else 'displayName'
    unique_identifier = root_node[key]

    return [key, unique_identifier]

def get_matching_flow_from_server(flow, stored_flows):
    [_, flow_id] = get_node_identity_pair(flow)

    for stored_flow in stored_flows:
        [_, id] = get_node_identity_pair(stored_flow)
        if flow_id == id:
            return stored_flow

    raise Exception("Trying to updated a built-in flow, with the wrong flow: " + flow + ". \n Make sure that this flow is defined in the built-in flow.")


def merge_flows(flow_from_server = {}, local_flow={}):
    changed = False
    for key in local_flow.keys():
        if key in flow_from_server and flow_from_server[key] != local_flow[key] and key != 'flowId':
            flow_from_server[key] = local_flow[key]
            changed = True

    return [flow_from_server, changed]

class AuthenticationFlowsImporter():
    def __init__(self, authentication_api):
        self.flowAPI = authentication_api

    def update(self, root_node, flows):
        flow_api = self.flowAPI.flows(root_node)
        executions_api = self.flowAPI.executions(root_node)

        if self.flowAPI.is_built_in(root_node):
            stored_flows = flow_api.all()
            #stored_executions = executions_api.all()

            for flow in flows:
                if is_auth_flow(flow):
                    flow_from_server = get_matching_flow_from_server(flow, stored_flows)
                    [updated_flow, has_change] = merge_flows(flow_from_server, flow)

                    if has_change:
                        flow_api.update(None, updated_flow).isOk()
                else:
                    executions_api.update(None, flow).isOk()
        else:
            self.remove(root_node)
            self.flowAPI.create(root_node).isOk()
            self.publish(root_node, flows)

    def remove(self, root_node):
        [key, unique_identifier_value] = get_node_identity_pair(root_node)
        self.flowAPI.removeFirstByKV(key, unique_identifier_value)

    def publish(self, root_node, flows):
        if not isinstance(flows, list):
            raise Exception("Bad Parameters for Authentication Flow: auth_flow parameter should be an array.")

        root_node = root_node
        nodes = {0: root_node}

        root_flow = self.flowAPI.executions(root_node)

        for flow in flows:
            current_level = get_node_level(flow)
            parent = nodes[current_level]

            if is_auth_flow(flow):
                authentication_flow = create_flow(flow)
                nodes[current_level + 1] = authentication_flow
                self.flowAPI.flows(parent).create(authentication_flow).isOk()
            else:
                execution = get_executions(flow)
                self.flowAPI.executions(parent).create(execution).isOk()

            if not consistent(root_flow, flow):
                raise Exception(
                    'There is an inconsistency problem: Changes are not taking place in the server, latency problems ?.')
