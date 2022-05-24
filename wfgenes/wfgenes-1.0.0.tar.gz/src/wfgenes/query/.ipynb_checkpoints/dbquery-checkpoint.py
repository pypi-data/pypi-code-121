""" a simple interface to query fireworks and workflows """


def get_launch(lpad, query):
    """ return a single firework from a query and its most recent launch """
    fw_list = list(lpad.fireworks.find(query))
    if len(fw_list) == 0:
        return None, None
    assert len(fw_list) == 1
    fw = fw_list[0]
    if len(fw['launches']) > 0:
        launch = lpad.launches.find_one({'launch_id': fw['launches'][-1]})
    else:
        launch = None
    return fw, launch


def db_select(lpad, filters={}, ids=[], selects=[]):
    """ apply workflow query filters and then select updates from launch """

    assert isinstance(filters, dict) or ids
    if not ids:
        wfq = filters.get('workflows', {})
        fwq = filters.get('fireworks', {})
        projection = {'nodes': True}
        wfns = [i['nodes'] for i in lpad.workflows.find(wfq, projection)]
        if fwq:
            projection = {'fw_id': True}
            fws = [i['fw_id'] for i in lpad.fireworks.find(fwq, projection)]
            wfnsf = [wfn[0] for wfn in wfns if any(i in wfn for i in fws)]
        else:
            wfnsf = [wfn[0] for wfn in wfns]
    else:
        wfnsf = ids

    result = []
    for wf_id in wfnsf:
        wf = lpad.workflows.find_one({'nodes': wf_id})
        wf_data = {}
        wf_data['name'] = wf['name']
        wf_data['metadata'] = wf['metadata']
        wf_data['state'] = wf['state']
        wf_data['fws'] = []
        for select in selects:
            query = {'name': select['fw_name'], 'fw_id': {'$in': wf['nodes']}}
            fw, launch = get_launch(lpad, query)
            fw_data = {}
            if fw:
                fw_data['name'] = select['fw_name']
                fw_data['id'] = fw['fw_id']
                fw_data['updated_on'] = fw['updated_on']
                fw_data['created_on'] = fw['created_on']
                fw_data['state'] = fw['state']
                fw_data['parents'] = wf['parent_links'].get(str(fw['fw_id']))
                if select.get('add fw_spec', False):
                    fw_data['spec'] = fw['spec']
                if launch and launch.get('action'):
                    outputs = select.get('fw_updates')
                    updates = launch['action'].get('update_spec')
                    if isinstance(outputs, list):
                        fw_data['updates'] = {o: updates[o] for o in outputs}
                    elif outputs:
                        fw_data['updates'] = updates
                    else:
                        fw_data['updates'] = None
                else:
                    fw_data['updates'] = None
                if launch:
                    fw_data['launch_dir'] = launch.get('launch_dir')
            wf_data['fws'].append(fw_data)
        result.append(wf_data)
    return result
