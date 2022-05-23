import logging
import re
import sys
import os
import csrbox
import csrbox.utils as utils
from functools import reduce
from csrbox.constants import *
from itertools import chain 
import datetime
import textwrap

version = csrbox.__version__
logger = logging.getLogger(__name__)

def calculate_size(isa_yaml, custom_attr, logging=False):
    attr_yaml = utils.load_yaml(attr_file)
    if custom_attr:
        c_attr_yaml = utils.load_yaml(custom_attr)
    else:
        c_attr_yaml = {}
    rvxlen = 'rv' + str(isa_yaml['hart0']['supported_xlen'][0])
    std_subfields = standard_csr_fields.copy()
    std_subfields.remove('fields')
    for node in isa_yaml['hart0']:
        size = -1
        if isinstance(isa_yaml['hart0'][node] , dict) and \
                'address' in isa_yaml['hart0'][node]:
            if isa_yaml['hart0'][node][rvxlen]['accessible']:
                csrname = str(node).lower()
                if logging:
                    logger.debug('Calculating size for :' + str(csrname))
                if 'msb' in isa_yaml['hart0'][node][rvxlen]:
                    size = isa_yaml['hart0'][node][rvxlen]['msb']
                    if csrname in attr_yaml:
                        attr_yaml[csrname]['size'] = size + 1
                    elif csrname in c_attr_yaml:
                        c_attr_yaml[csrname]['size'] = size + 1
                        attr_yaml[csrname] = c_attr_yaml[csrname]
                    else:
                        attr_yaml[csrname] = {'size': size + 1,\
                                'value_method': {'required': True},
                                'action_method': {'required': False}}
                else:
                    for subfield, content in isa_yaml['hart0'][node][rvxlen].items():
                        if subfield not in std_subfields:
                            if subfield == 'fields':
                                for x in content:
                                    if isinstance(x,list):
                                        list_max = max([sublist[-1] for sublist in x])
                                        size = max(size, list_max)
                            else:
                                size = max(size, content['msb'])
                    if csrname in attr_yaml:
                        attr_yaml[csrname]['size'] = size + 1
                    elif csrname in c_attr_yaml:
                        c_attr_yaml[csrname]['size'] = size + 1
                        attr_yaml[csrname] = c_attr_yaml[csrname]
                    else:
                        attr_yaml[csrname] = {'size': size + 1,\
                                'value_method': {'required': True},
                                'action_method': {'required': False}}

    return attr_yaml

def csr_acc_false(bar):
   not_acc = []
   rvxlen = 'rv' + str(bar['hart0']['supported_xlen'][0])  
   for node in bar['hart0']:
            if isinstance(bar['hart0'][node], dict):
                if 'description' in bar['hart0'][node]:
                    csr_name = node
                    name_str = str(csr_name)
                    if bar['hart0'][csr_name][rvxlen]['accessible'] == False:
                       not_acc.append(name_str) 
   return not_acc 

def find_group(bar, csrname, logging=False):
    for grps in bar:
        if csrname.upper() in bar[grps]:
            return grps
    return None


def csrgrp_check(isa_yaml, grp_yaml, logging=False):
    if logging:
        logger.info('Sanity check for Grouping File')

    grp_list = list(grp_yaml)
    rvxlen = 'rv' + str(max(isa_yaml['hart0']['supported_xlen']))



    # - check for duplicates
    for grp, elem in grp_yaml.items():
      if elem != None :
        if len(elem) != len(set(elem)) :
            dup = list(set([x for x in elem if elem.count(x) > 1]))
            logger.error( grp + ' has the following duplicates ' + str(dup))
            raise SystemExit

    # - check of overlaps
    for i in range(0,len(grp_list)-1):
        x = grp_yaml[grp_list[i]]
        for j in range(i+1, len(grp_list)):
            y = grp_yaml[grp_list[j]]
            if x != None and y != None:
             intersection = list(set(x) & set(y))
            if intersection:
                logger.error(grp_list[i] + ' and ' + grp_list[j] + 
                        ' have the following common entries '+ str(intersection))
                raise SystemExit
    if rvxlen == 'rv64':
        same_groups = same_groups_rv64
    else:
        same_groups = same_groups_rv32

    # - same group checks
    for grp, elem in grp_yaml.items():
      if elem != None :
        for csrs in elem:
            for pairs in same_groups:
                if csrs in pairs:
                    grp1 = find_group(grp_yaml, pairs[0])
                    grp2 = find_group(grp_yaml, pairs[1])
                    if grp1 is not None and grp2 is not None and grp1 != grp2:
                        logger.error(str(pairs) + ' Need to be in same group')
                        raise SystemExit
            if rvxlen == 'rv32':
                for pairs in necessary_pairs_rv32:
                    if csrs in pairs:
                        grp1 = find_group(grp_yaml, pairs[0])
                        grp2 = find_group(grp_yaml, pairs[1])
                        if grp1 is None or grp2 is None:
                            logger.error('Please instantiate both the following pairs: ' + str(pairs))
                            raise SystemExit
    # -- grp naming required
    for i in range(1, len(grp_list)+1):
        if 'grp'+str(i) not in grp_yaml:
            logger.error('grp'+str(i) + ' is missing')
            raise SystemExit

    # -- grp csrs must be accessible
    for grp, elems in grp_yaml.items():
      if elem != None :
        for csr in elems:
            if csr.lower() not in isa_yaml['hart0']:
                logger.error(csr + ' in grouping YAML not found in ISA-YAML')
                raise SystemExit
            if not isa_yaml['hart0'][csr.lower()][rvxlen]['accessible']:
                logger.error( csr + ' in grouping yaml is not accessible in ISA=YAML')
                raise SystemExit

    # -- missing csrs in grp_yaml
    missing = []
    for csr, elem in isa_yaml['hart0'].items():
        if isinstance(elem, dict):
            if 'description' in elem and elem[rvxlen]['accessible']:
                if find_group(grp_yaml, csr) is None:
                    missing.append(csr)
    if missing:
        logger.warn('The following CSRS are accessible in the ISA-YAML but missing the grouping yaml' + str(missing))

    logger.info('Grouping Yaml is valid')

