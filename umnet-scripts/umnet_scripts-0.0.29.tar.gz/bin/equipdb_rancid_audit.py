#!/usr/bin/env python

from umnet_scripts.utils import *
from umnet_scripts import UMnetequip
import argparse, os
import logging
from pprint import pprint
import re

logger = logging.getLogger(os.path.basename(__file__))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Audit equipdb against rancid files on wallace-new.")
    parser.add_argument('-l', '--log-level', dest='log_level', default="error",
            help='Set logging level (default=error)')

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        level=args.log_level.upper(),
    )

    # Get all active switches and routers
    eqdb = UMnetequip()
    devices = eqdb.get_devices_by_category('SWITCH OR ROUTER', active_only=True)

    # first need to merge stack entries in the DB. Sometimes 'monitored device'
    # is checked on one stack member, but 'rancid' is checked on another (ugh)
    merged_devices = {}
    for d in devices:
        if d['dns_name'] in merged_devices.keys():
            curr_d = merged_devices[d['dns_name']]
            curr_d['rancid'] = d['rancid'] or curr_d['rancid']
            curr_d['monitored_device'] = d['monitored_device'] or curr_d['monitored_device']
        else:
            merged_devices[d['dns_name']] = dict(d)

    # we only care about devices that are 'monitored' and 'online'
    monitored_devices = [d for d in merged_devices.values() if d['monitored_device'] and not d['off_line']]

    # Get a list of all the files on this machine's /home/rancid/*configs* directories
    # Stolen from Ben Meekhof in the umnet_netbox_etl code
    rancid_cmd = '''cd /home/rancid && find . -path ./.ssh -prune -false -o -path '*/configs/*' \
            -not -path '*CVS*'  -not -path './RouteTables/*' \
            -not -path './ARP/*' -not -path './CiscoWL/*' \
            -not -path './TEST/*' -mtime -7 -type f \
    '''
    with os.popen(rancid_cmd) as stream:
        lines = stream.read().splitlines()

    # peel off filename which maps to dns_name or IP address
    # of the device
    rancid_devices = [l.split('/')[-1].replace('.umnet.umich.edu','') for l in lines]

    # First let's print out all the 'on-line' devices in equipdb that don't have the rancid box checked
    no_rancid = [d['dns_name'] for d in monitored_devices if not d['rancid']] 
    if(no_rancid):
        print("The following devices are not marked as 'offline' but don't have their 'rancid' checkbox checked:\n")
        [print(d) for d in no_rancid]
    else:
        print("All online 'SWITCH_OR_ROUTER' devices are in rancid.")

    print("\n")
    # Now we'll print all the devices marked for rancid that don't have a recent backup
    failed_rancid = [d['dns_name'] for d in monitored_devices
        if d['dns_name'] not in rancid_devices and
           d['ip_address'] not in rancid_devices and
           d['rancid']
           ]

    if(failed_rancid):
        print("The following devices are checked for rancid backup but haven't been backed up recenty.\n")
        [print(d) for d in failed_rancid]
    else:
        print("All devices passed rancid backup check")
