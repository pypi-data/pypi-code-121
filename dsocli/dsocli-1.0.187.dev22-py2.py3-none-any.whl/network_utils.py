import ipaddress
import re
from .logger import Logger
from .exceptions import DSOException
from .dict_utils import *

UNNAMED_SUBNET = 'N/A'

def ipv4_to_binary(ip, sep="."):
    return  sep.join(map(str,["{0:08b}".format(int(x)) for x in ip.split(".")]))


class IPv4AddressX(ipaddress.IPv4Address):
    def to_binary(self, sep="."):
        """Represent IPv4 as 4 blocks of 8 bits."""
        return sep.join(f"{i:08b}" for i in self.packed)

    @classmethod
    def from_binary_repr(cls, binary_repr: str):
        """Construct IPv4 from binary representation."""
        # Remove anything that's not a 0 or 1
        i = int(re.sub(r"[^01]", "", binary_repr), 2)
        return cls(i)



def layout_subnet_plan(subnet_plan, filters=None, summary=True):

    def add_segment_subnets(segments, segment_ix, supernet, result: dict):

        def is_subnet_selected(supernet, subnet, selects):
            if not subnet.subnet_of(supernet):
                return False
            subnetIP = IPv4AddressX(subnet.network_address).to_binary(sep='')
            result = True
            for select in map(lambda x: x.strip(), selects.split('|')):
                try:
                    invert, operation, base, msd_dontcare, digits, lsd_dontcare = re.match('^(!|not)?\s*(msd|lsd)\(0(\w)([x]*)([01]*)([x]*)\)$', select).groups()[0:]
                except:
                    raise DSOException(f"Invalid value for 'select': {select}")
                invert = 'not' if invert == '!' else '' if invert is None else invert
                if not base in ['b']:
                    raise NotImplementedError
                ### most significant digit
                if operation == 'msd':
                    target = subnetIP[supernet.prefixlen + len(msd_dontcare):]
                ### least significant digit
                elif operation == 'lsd':
                    target = subnetIP[supernet.max_prefixlen - len(digits) - len(lsd_dontcare):]
                selected = eval(f"{invert} target.startswith(digits)")
                result = result and selected
            return result

        ### if last segment, add host count
        if segment_ix == len(segments):
            hosts = list(supernet.hosts())
            result['Hosts'] = {
                'Count': len(hosts),
                'IP': f"{hosts[0]}/32-{hosts[-1]}/32"
            }
            return

        segment = segments[segment_ix]
        # key = segment.get('plural', f"{segment.get('name')}s")
        key = segment.get('name')
        if segment['bits'] > 0:
            subnets = list(supernet.subnets(segment['bits']))
            result[key] = {
                'Count': 0, ### to be incremented while adding subnets
                'Ranges': []
            }
            range_first_subnet = None
            range_last_subnet = None
            for i, subnet in enumerate(subnets):
                if 'select' in segment:
                    if not is_subnet_selected(supernet, subnet, segment['select']): 
                        ### add the last subnet in the range if in summary mode
                        if summary and not range_last_subnet is None:
                            result[key]['Ranges'][-1]['Subnets'].append({
                                'CIDR' : range_last_subnet.with_prefixlen,
                                'Number': result[key]['Count'] + 1,
                                'Name' : segment['labels'].get(str(result[key]['Count']-1), UNNAMED_SUBNET),
                            })
                            add_segment_subnets(segments, segment_ix+1, range_last_subnet, result[key]['Ranges'][-1]['Subnets'][-1])

                        range_first_subnet = None
                        range_last_subnet = None
                        Logger.debug(f"{key} {i} excluded: {subnet}")
                        continue

                ### if start of a range, append a new Range
                if range_first_subnet is None:
                    range_first_subnet = subnet
                    result[key]['Ranges'].append({
                        'CIDR': range_first_subnet.with_prefixlen,
                        'Count': 0, ### to be incremented while adding subnets
                        'Subnets': []
                    })
                    if summary:
                        result[key]['Ranges'][-1]['Subnets'].append({
                            'CIDR': range_first_subnet.with_prefixlen,
                            'Number': result[key]['Count'] + 1,
                            'Name': segment['labels'].get(result[key]['Count'], UNNAMED_SUBNET),
                        })
                        add_segment_subnets(segments, segment_ix+1, range_first_subnet, result[key]['Ranges'][-1]['Subnets'][-1])
                else:
                    range_last_subnet = subnet
                    cidr = f"{range_first_subnet.with_prefixlen}-{range_last_subnet.with_prefixlen}"
                    ### updare Range CIDR
                    result[key]['Ranges'][-1]['CIDR'] = cidr
                    ### if in summary mode, always add the last subnet in the list
                    if summary and range_last_subnet == subnets[-1]:
                        result[key]['Ranges'][-1]['Subnets'].append({
                            'CIDR' : range_last_subnet.with_prefixlen,
                            'Number': result[key]['Count'] + 1,
                            'Name': segment['labels'].get(result[key]['Count'], UNNAMED_SUBNET),
                        })
                        add_segment_subnets(segments, segment_ix+1, range_last_subnet, result[key]['Ranges'][-1]['Subnets'][-1])

                ### always add the subnet if not in summary mode
                if not summary:
                    cidr = {
                            'CIDR' : subnet.with_prefixlen,
                            'Number': result[key]['Count'] + 1,
                            'Name': segment['labels'].get(result[key]['Count'], UNNAMED_SUBNET),
                    }
                    selected = True
                    if filters and 'selector' in filters:
                        if key in filters['selector']:
                            for k,v in filters['selector'][key].items():
                                selected = selected and k in cidr and cidr[k] == v
                                if not selected: break
                    if selected:
                        result[key]['Ranges'][-1]['Subnets'].append(cidr)
                        add_segment_subnets(segments, segment_ix+1, subnet, result[key]['Ranges'][-1]['Subnets'][-1])


                result[key]['Count'] = result[key]['Count'] + 1
                result[key]['Ranges'][-1]['Count'] = result[key]['Ranges'][-1]['Count'] + 1

            # ### comporess Range list if has only one element
            # if compress and len(result[key]['Ranges']) == 1:
            #     result[key].update(result[key]['Ranges'][0])
            #     result[key].pop('Ranges')

        ### skip segments with 0 bits long, and move to the next segment
        else:
            add_segment_subnets(segments, segment_ix+1, supernet, result)


    ####################################################################################

    if filters:
        summary = False
        if 'plan' in filters and filters['plan']:
            plans = list(filter(lambda x: x['name'] == filters['plan'], subnet_plan['plans']))
            if not plans:
                raise DSOException(f"Plan '{filters['plan']}' not found in the given subnet plan.")
    else:
        plans = subnet_plan['plans']

    plans = list(filter(lambda x: str(x['enabled']).lower() in ['1', 'yes', 'true'], plans))
    if not plans:
        if filters['plan']:
            raise DSOException(f"Plan '{filters['plan']}' is disabled in the given subnet plan.")
        else:
            raise DSOException(f"No active plan found in the given subnet plan.")

    layouts = []
    for plan in plans:
        layouts.append({})
        add_segment_subnets(plan['segments'], 0, ipaddress.ip_network(subnet_plan['cidr']), layouts[-1])


    merged = {}
    for layout in layouts:
        merge_dicts(layout, merged, merge_key='CIDR')

    result = {'SubnetPlanLayout': {
                'Name': subnet_plan['name'],
                'Description': subnet_plan['description'],
                'CIDR': subnet_plan['cidr'],
                'Layout': merged
            }
    }

    return result

