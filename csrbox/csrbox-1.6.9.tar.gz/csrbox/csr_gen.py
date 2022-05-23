import logging
import re
import sys
import os
import csrbox
import csrbox.utils as utils
from csrbox.constants import *
import csrbox.csrgrp_check as csrgrp_check
import datetime
import textwrap
import math
from riscv_config.warl import warl_interpreter

version = csrbox.__version__
logger = logging.getLogger(__name__)

def priv2bits (priv_mode):
    if priv_mode == 'M':
        return 3
    if priv_mode == 'S':
        return 1
    if priv_mode == 'U':
        return 0
    logger.error('Unsupported priv mode found')
    raise SystemExit

def csr_gen (isa_file, grp_file, custom_file, debug_file, custom_attr_file, work_dir,
        probeinst, logging=False):
    '''
        Top level function which validates the sanity of the grouping yaml
        followed by calls to subfunctions which generated the corresponding
        bluespec code. This function further assumes that the riscv-config
        isa yaml provided is the validated/normalized version.

        We also update the the size node for the csrs in the attributes YAML
        file based on the csrs that have been instantiated in the riscv-config
        YAML

        :param isa_file: path to the **validated** riscv-config ISA yaml file
        :param grp_file: path to the csr grouping YAML file.
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_file: str
        :type grp_file: str
        :type work_dir: str
    '''

    isa_yaml = utils.load_yaml(isa_file)
    grp_yaml = utils.load_yaml(grp_file)
    global debug_enabled
    global compressed_enabled
    global supervisor_enabled
    global hypervisor_enabled
    global physical_addr_sz
    global pmp_grain
    global satp_mode_condition

    if 'C' in isa_yaml['hart0']['ISA']:
        compressed_enabled = True
    else:
        compressed_enabled = False

    if 'S' in isa_yaml['hart0']['ISA']:
        supervisor_enabled = True
    else:
        supervisor_enabled = False

    if 'H' in isa_yaml['hart0']['ISA']:
        hypervisor_enabled = True
    else:
        hypervisor_enabled = False

    if custom_file :
        custom_yaml= utils.load_yaml(custom_file)
        isa_yaml['hart0'].update(custom_yaml['hart0'])
    if debug_file:
        debug_yaml = utils.load_yaml(debug_file)
        isa_yaml['hart0'].update(debug_yaml['hart0'])
        debug_enabled = True

    else:
        debug_enabled = False

    physical_addr_sz = isa_yaml['hart0']['physical_addr_sz']
    pmp_grain = isa_yaml['hart0']['pmp_granularity']
    valid_satp_modes=[]
    xlen = max(isa_yaml['hart0']['supported_xlen'])
    if supervisor_enabled:
        satp_modewarl =\
                    (warl_interpreter(isa_yaml['hart0']['satp']['rv'+str(xlen)]['mode']['type']['warl']))
        for x in [0, 1, 8, 9, 10]:
            if satp_modewarl.islegal(x,[]):
                if xlen == 64:
                    valid_satp_modes.append('word[63:60] == ' +str(x))
                else:
                    valid_satp_modes.append('word[31] == ' +str(x))
    satp_mode_condition = '||'.join(valid_satp_modes)

    csrgrp_check.csrgrp_check(isa_yaml, grp_yaml, logging)
    attr_yaml = csrgrp_check.calculate_size(isa_yaml, custom_attr_file)
    csr_define(isa_yaml , work_dir , 'csrbox.defines', logging)
    csr_decoder(isa_yaml, work_dir , 'csrbox_decoder.bsv', logging)
    csr_types(isa_yaml  , work_dir , 'csr_types.bsv', logging)
    groups_gen(isa_yaml, grp_yaml, attr_yaml, work_dir, probeinst, logging)

def csr_types(isa_yaml, work_dir,  bsv, logging=False):
    '''
        Function to generate the types bluespec file which includes structures
        and functions that are used across the csrbox modules

        :param isa_yaml: the riscv-config isa YAML
        :param work_dir: path to the directory where the bluespec files should be generated
        :param bsv: name of the file to be created inside the work_dir

        :type isa_yaml: dict
        :type work_dir: str
        :type bsv: str

    '''
    if logging:
        logger.info('Creating File: ' + bsv)
    bsvfile = open(work_dir + bsv, 'w')
    pkg_name = bsv[:-4]

    xlen = str(isa_yaml['hart0']['supported_xlen'][0])

    bsvfile.write(license_header.format(version, str(datetime.datetime.now())))
    bsvfile.write('''
package {0} ;
    `include "csrbox.defines"
    `include "Logger.bsv"

'''.format(pkg_name))
    if 'C' in isa_yaml['hart0']['ISA'] :
        c_str = 'Bit#(1) pc_1;'
    else:
        c_str = ''
    bsvfile.write(csrreq_struct_temp.format(xlen, c_str))
    bsvfile.write(func_temp.format(xlen))
    if hypervisor_enabled:
        bsvfile.write(func_address)
    bsvfile.write(func_external.format(1))
    bsvfile.write(end_package_temp)
    bsvfile.close()


def groups_gen(isa_yaml, grp_yaml, attr_yaml, work_dir, probeinst, logging=False):
    '''
        Function which co-ordinates the generation of all the bluespec code for
        the individual groups/stations and the top level bluespec module.

        The function first creates a subset of the
        riscv-config isa yaml based on the csrs present in each group and calls
        various sub-functions to generate the corresponding bsv file of the
        individual groups/station.

        Once the station files are generated the csr_top is called which is used
        to generate the top module instantiating and connecting all the
        individual groups/stations.

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type work_dir: str
    '''

    global physical_addr_sz

    rvxlen = 'rv' + str(max(isa_yaml['hart0']['supported_xlen']))
    xlen = str(max(isa_yaml['hart0']['supported_xlen']))

    station_isa = {}
    aux_info = {}
    csr_isa = {}

    not_acc = []
    max_len = len(grp_yaml)

    aux_info['custom_exceptions']=isa_yaml['hart0']['custom_exceptions']
    aux_info['custom_interrupts']=isa_yaml['hart0']['custom_interrupts']

    for grp, elems in grp_yaml.items():
        if elems != None:
          if 'grp'+str(max_len) == grp:
              last = True
          else:
              last = False
          for node in isa_yaml['hart0']:
             if isinstance(isa_yaml['hart0'][node], dict):
                if 'description' in isa_yaml['hart0'][node]:
                    csr_name = node
                    name_str = str(csr_name)
                    if isa_yaml['hart0'][csr_name][rvxlen]['accessible'] == True:
                      if csr_name.upper() in elems:
                          station_isa[csr_name] = isa_yaml['hart0'][node]
                          csr_isa[csr_name] = isa_yaml['hart0'][node]
                    else:
                       not_acc.append(name_str)

        filename = 'csrbox_' + grp + '.bsv'
        bsvstr = ''
        bsvfile = open(work_dir+filename, 'w')
        if logging:
            logger.info('Writing file: ' + filename)
        pkg_name = filename[:-4]
        bsvstr += str(license_header.format(version, str(datetime.datetime.now())))
        bsvstr += (package_temp.format(pkg_name))
        bsvstr = station_interface(station_isa, grp_yaml, attr_yaml, aux_info, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr = station_module(station_isa, grp_yaml, attr_yaml, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr = station_regs(station_isa, grp_yaml, attr_yaml, aux_info, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr = station_modbody(station_isa, grp_yaml, attr_yaml, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr = station_req(station_isa, grp_yaml, attr_yaml, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr = station_methods(station_isa, grp_yaml, attr_yaml, aux_info, rvxlen,
                pkg_name, last, bsvstr, logging)
        bsvstr += (end_module_temp)
        bsvstr +=(end_package_temp)
        bsvfile.write(bsvstr)
        station_isa.clear()
    bsvstr = csr_top(csr_isa, grp_yaml, attr_yaml, aux_info, rvxlen,
             'csrbox', logging)
    filename = 'csrbox.bsv'
    bsvfile = open(work_dir + filename, 'w')
    bsvfile.write(bsvstr)
    bsvfile.close()

    filename = 'csr_probe.bsv'
    bsvfile = open(work_dir + filename, 'w')
    bsvfile.write(csr_probe_function(csr_isa, attr_yaml, probeinst, logging))
    bsvfile.close()


def csr_probe_function(isa_yaml, attr_yaml,probeinst, logging=False):
    bsvstr = ''
    bsvstr += '''
  function Bit#(`xlen) fn_probe_csr (Bit#(12) csr_addr);
    case (csr_addr)
'''
    if logging:
        logger.info('-- Creating Probe function ')
    for csrname in isa_yaml:
        if attr_yaml[csrname]['value_method']['required']:
            bsvstr += '''
        `{0} : return zeroExtend({2}.sbread.mv_csr_{1});'''.format(csrname.upper(),
                csrname.lower(), probeinst)
    bsvstr += '''
    default: return 0;
    endcase
  endfunction
'''
    return bsvstr



def csr_decoder(isa_yaml, work_dir, bsv, logging=False):

    '''
        Function to generate the bluespec decoder file indicating if the access
        to the CSR if valid or not
        :param isa_yaml: the riscv-config isa YAML
        :param work_dir: path to the directory where the bluespec files should be generated
        :param bsv: name of the file to be created inside the work_dir

        :type isa_yaml: dict
        :type work_dir: str
        :type bsv: str
    '''

    rvxlen = 'rv' + str(isa_yaml['hart0']['supported_xlen'][0])

    definefile = open(work_dir + bsv, 'w')
    definefile.write(license_header.format(version, str(datetime.datetime.now())))
    definefile.write("////////////////CSR DECODER////////////////")
    pkg_name = bsv[:-4]
    definefile.write(package_temp.format(pkg_name))
    definefile.write(func_decoder)

    for node in isa_yaml['hart0']:
        cond_str = ''
        if isinstance(isa_yaml['hart0'][node], dict):
            if 'address' in isa_yaml['hart0'][node] and ( isa_yaml['hart0'][node][rvxlen]['accessible'] == True) :
                if 'S' in isa_yaml['hart0'][node]['priv_mode']:
                    cond_str = 'if (misa[18] == 1)'
                elif 'U' in isa_yaml['hart0'][node]['priv_mode'] and \
                    isa_yaml['hart0'][node]['address'] in user_trap_csrs:
                        cond_str = 'if ((misa[13]&misa[20]) == 1)'

                csr_name = node
                definefile.write(
                        case_address_temp.format(csr_name.upper(), cond_str))
    definefile.write('\n           endcase')
    definefile.write('\n     return valid;')
    definefile.write('\n     endfunction')

    definefile.write(func_csr_to_csr)
    for node in isa_yaml['hart0']:
        cond_str = ''
        if isinstance(isa_yaml['hart0'][node], dict):
            if 'address' in isa_yaml['hart0'][node] and ( isa_yaml['hart0'][node][rvxlen]['accessible'] == True) :
                addr = int(isa_yaml['hart0'][node]['address'])
                definefile.write(csr_str_temp.format(node.upper(), addr,
                    node.lower()))
    definefile.write('\n           endcase')
    definefile.write('\n     endfunction')

    definefile.write('''

    function Bool fn_csrbox_access(Bit#(12) csr_addr, Bit#(5) operand, Bit#(2) operation, Bit#(2) prv);
      Bool write = (operand != 0 || operation=='b01) ? True:False;
      return ((prv >= csr_addr[9:8]) && !(write && csr_addr[11:10]==2'b11) );
    endfunction:fn_csrbox_access

''')

    definefile.write(end_package_temp)
    definefile.close()

def csr_define(isa_yaml, work_dir, bsv, logging=False):
    '''
        Function which generates the defines file which captues the macro
        encodings used across the csrbox bsv modules

        :param isa_yaml: the riscv-config isa YAML
        :param work_dir: path to the directory where the bluespec files should be generated
        :param bsv: name of the file to be created inside the work_dir

        :type isa_yaml: dict
        :type work_dir: str
        :type bsv: str
    '''

    if logging:
        logger.info('Creating Defines file: ' + bsv)
    rvxlen = 'rv' + str(isa_yaml['hart0']['supported_xlen'][0])
    definefile = open(work_dir + bsv, 'w')
    definefile.write(license_header.format(version, str(datetime.datetime.now())))
    definefile.write("////////////////CSR LIST////////////////")

    for node in isa_yaml['hart0']:
        if isinstance(isa_yaml['hart0'][node], dict):
            if 'address' in isa_yaml['hart0'][node] and ( isa_yaml['hart0'][node][rvxlen]['accessible'] == True) :
                csr_name = node
                if logging:
                 logger.debug('Processing CSR: ' + str(csr_name.upper()))

                csr_address = format(isa_yaml['hart0'][csr_name]['address'],'x')

                if logging:
                 logger.debug('|-- address: ' + str(csr_address))

                definefile.write(address_temp.format(csr_name.upper(),csr_address))

    if isa_yaml['hart0']['custom_exceptions'] is not None:
        for ce in isa_yaml['hart0']['custom_exceptions']:
            definefile.write('\n`define {0} {1}'.format(ce['cause_name'],
                ce['cause_val']))
    if isa_yaml['hart0']['custom_interrupts'] is not None:
        for ce in isa_yaml['hart0']['custom_interrupts']:
            definefile.write('\n`define {0} {1}'.format(ce['cause_name'],
                ce['cause_val']))
    if 'parking_loop' in isa_yaml['hart0'] and \
            isa_yaml['hart0']['parking_loop'] is not None:
        definefile.write("\n`define debug_parking_loop "+ \
                str(isa_yaml['hart0']['parking_loop'])+"\n")
    definefile.close()


def create_concat_vector(mylist, xlen):
    '''
    Function to return a bsv-string for a csr which is the concetation of the
    all its subfields and gaps replaced with zeros'

    :param mylist: A list of 3 tuple entries. Each entry has the following
    information per subfield [msb of subfield, width of the subfield, name of
    the subfield]

    :return: string with concatenation of all the sub-fields.
  '''
    concat_length = 0
    newlist = sorted(mylist, key=lambda x: x[0])[::-1]
    cv = ' '
    last_lsb = xlen - 1
    while len(newlist) != 0:
        msb, width, name, type_reg, prefix = newlist[0]
        newlist.pop(0)
        if msb != last_lsb:
            cv += readonly_temp.format(last_lsb - msb) + ','
            concat_length += 1
        if 'ro_variable' in type_reg and (name != 'mstatus_sd'):
            cv += 'readOnlyReg({0}{1}), '.format(prefix , str(name))
        else:
            cv += prefix + str(name) + ' ,'
        concat_length += 1
        last_lsb = msb - width
    if last_lsb != -1 :
       cv += readonly_temp.format(last_lsb + 1)
       concat_length += 1
    return concat_length, cv[:-1]


def get_reset_val(value, width, lsb, xlen):
    '''
    Function to extract 'width' number of bits starting at the 'lsb' position of
    the value. Note here that the python indexes the binary string from the let
    while the lsb defines the position from the right. Hence the need for this
    function

    :param value: the integer value from which bits need to be extracted.
    :param width: size of extraction
    :param lsb:   starting position of extraction

    :return: returns the reset value in decimal form
  '''
    b = '{:0' + xlen + 'b}'
    # convert number into binary first
    binary = b.format(value)

    # remember python indexes from left to right
    end = len(binary) - lsb - 1
    start = end - width + 1
    kBitSubStr = binary[start:end + 1]

    # convert extracted sub-string into decimal again
    return int(kBitSubStr, 2)

def derive_wlrl_func(wlrl_list):

    legal_list = []
    for l in wlrl_list:
        if ':' in l:
            minval = int(l.split(':')[0],16)
            maxval = int(l.split(':')[1],16)
            legal_list += list(range(minval,maxval+1))

    act_width = int(math.log2(max(legal_list)))

    act_list = list(range(0,(2**act_width)+1))
    if sorted(legal_list) == act_list:
        full_wlrl = True
    else:
        full_wlrl = False

    return full_wlrl, act_width


def derive_warl_func(field_name, width, warl, csr_dep, post_op=''):
    '''
        Function to convert the warl strings in the riscv-config YAML to
        corresponding bluespec code.

        The function first splits the warl string into the condition and the
        legalizing strings. A regular expression is then applied to both strings
        separately to extract parameters and create bluespec code.


        :param field_name: string indicating the name of the csr
        :param width: indicates the max size of the csr
        :param warl_str: containts the warl string from the riscv-config YAML string

        :type field_name: str
        :type width: int
        :type warl_str: str
    '''

    bsv_str = ''
    regex_range = re.compile(field_name + '\[(.*?)\]\s*(in|not in)\s*\[(.*?)\]')
    regex_bitmask = re.compile(field_name + '\[(.*?)\]\s*bitmask\s*\[(.*?)\]')
    regex_cond = re.compile('\s*(.*?)\[(.*?)\]\s*(.*?)\s*\[(.*?)\]')
    for warl_str in warl:
        warl_split = warl_str.split('->')
        legal = warl_split[-1]
        if csr_dep:
            condition_str = 'if ('
        else:
            condition_str = ''
        if csr_dep:
            search = regex_cond.findall(warl_split[0])
            for part in search:
                csr, indices, op, val = part
                if field_name == csr:
                    csr_write = 'r'
                else:
                    for dep_csr in csr_dep:
                        if csr in dep_csr and '::' in dep_csr:
                            csr_write = 'rg_' + dep_csr.split('::')[0] + '_'+dep_csr.split('::')[1]
                        elif csr == dep_csr:
                            csr_write = 'rg_' + csr
                op = '!=' if 'not in' in op else '=='
                condition_str += ' {0}[{1}] {2} {3}'.format(csr_write, indices, op, val)
                condition_str += ' && '
            condition_str = condition_str[:-4] + ' )begin\n                  '



        range_vals = regex_range.findall(legal)
        bitmask_vals = regex_bitmask.findall(legal)
        full_warl = False
        curr_bsv_str = ''
        if range_vals != []:
            curr_bsv_str += 'if ( ('
            for x in range_vals:
                curr_bsv_str += '('
                indices = x[0]
                if 'not' in x[1]:
                    not_eq = True
                else:
                    not_eq = False
                values = x[2].split(',')
                for v in values:
                    if ':' in v:
                        base_bound = v.split(':')
                        if int(base_bound[0],16) == 0 and int(base_bound[1],16) == (2**int(width) -1):
                            full_warl = True
                        curr_bsv_str += '( x[' + indices + '] >= ' +\
                        base_bound[0] + ' && x[' + indices + '] <= ' +base_bound[1] + ') ||'
                    elif not_eq:
                        curr_bsv_str += '( x[' + indices + '] != ' + v + ') &&'
                    else:
                        curr_bsv_str += '( x[' + indices + '] == ' + v + ') ||'
                curr_bsv_str = curr_bsv_str[:-2] + ') && '
            curr_bsv_str = curr_bsv_str[:-3] + ')'
            curr_bsv_str = curr_bsv_str.replace('0x', "'h") + ')begin\n'
            curr_bsv_str += '                       let _x = x;'
            if post_op != '':
                curr_bsv_str += post_op
            curr_bsv_str = curr_bsv_str + 'r._write(_x);end\n'
        elif bitmask_vals != []:
            indices = bitmask_vals[0][0]
            mask_fixed = bitmask_vals[0][1].split(',')
            mask = mask_fixed[0][2:]
            fixedval = mask_fixed[1][3:]
            curr_bsv_str = "let _x = ( (x & 'h" + mask + ") | (~'h" + mask + " & 'h" + fixedval + ") );"
            if post_op != '':
                curr_bsv_str = curr_bsv_str + post_op + ';'
            curr_bsv_str = curr_bsv_str + 'r._write(_x);'
        if full_warl:
            curr_bsv_str = 'let _x = x;'
            if post_op != '':
                curr_bsv_str = curr_bsv_str + post_op + ';'
            curr_bsv_str = curr_bsv_str + 'r._write(_x);'
        if condition_str != '':
            curr_bsv_str += ' end\n'
        bsv_str += condition_str + curr_bsv_str
        bsv_str += '                else  '
    bsv_str = bsv_str[:-22]
    return bsv_str

def station_interface(isa_yaml, grp_yaml, attr_yaml, aux_info, rvxlen, pkg_name,
        last, bsvstr, logging = False):

    '''
        Function to create the interface definition of individual
        groups/stations.

        First Value methods are created for all csrs that are instantiated in
        the particular group. Next, custom action methods required for specific
        csrs of their subfields are created.

        Finally action methods to read shadow or dependent csrs is created.

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''
    global debug_enabled
    global compressed_enabled
    global supervisor_enabled
    global hypervisor_enabled
    global physical_addr_sz
    xlen = int(rvxlen[2:])
    bsvstr += interface_temp.format(pkg_name)

    if logging:
        logger.info('Initiating interface generation for : ' + pkg_name)
    # define additional methods for certain csrs
    req_ifcs = []
    for csrname in isa_yaml:
        if csrname.lower() in attr_yaml and 'additional_method' in attr_yaml[csrname.lower()]:
            for add_ifc in attr_yaml[csrname.lower()]['additional_method']:
                if '::' in add_ifc:
                    cond = add_ifc.split('::')[0]
                    if cond:
                        add_ifc = add_ifc.split('::')[1]
                    else:
                        add_ifc = ''
                if add_ifc not in req_ifcs:
                    bsvstr +=\
                        textwrap.indent(add_ifc, '    ') + '\n'
                    req_ifcs.append(add_ifc)

    # define a value method for each csr.
    for csrname in isa_yaml:
        if attr_yaml[csrname]['value_method']['required']:
            if  logging:
                logger.debug('-- Creating value methods for ' + csrname)
            size = attr_yaml[csrname]['size']
            if 'pmpaddr' in csrname:
                size = physical_addr_sz -2
            bsvstr +=(methodv_dec_temp.format(size, csrname))

    # define csr specific action methods.
    for csrname in isa_yaml:
        if attr_yaml[csrname]['action_method']['required']:
            if  logging:
                logger.debug('-- Creating action methods for ' + csrname)
            size = attr_yaml[csrname]['size']
            for arguments in attr_yaml[csrname]['action_method']['def_arguments']:
                arguments = arguments.replace('xlen',str(xlen))
                arguments = arguments.replace('size',str(size))
                if '::' in arguments:
                    cond, args = re.findall(r'^(.*?)::(.*?)$',arguments)[0]
                    if eval(cond):
                        args = textwrap.indent(args, '')
                    else:
                        args = ''
                else:
                    args = arguments
                bsvstr +=('\n    '+args)
    bsvstr +=('\n')

    # create action methods of dependent csrs
    incomming_reads = []
    for csrname in isa_yaml:
        if 'depends_on_csr' in attr_yaml[csrname]:
            if len(attr_yaml[csrname]['depends_on_csr']) != 0:
                if  logging:
                    logger.debug('-- Creating action/read methods for dependencies of ' + csrname)
                for dependent in attr_yaml[csrname]['depends_on_csr']:
                    create_sideband = True
                    dcsr = dependent
                    if '::' in dependent:
                        condition, csr = re.findall(r'^(.*?)::(.*?)$',dependent)[0]
                        if eval(condition) :
                            dcsr = csr
                        else:
                            create_sideband = False
                    if create_sideband and dcsr not in isa_yaml and \
                            dcsr not in incomming_reads \
                            and attr_yaml[dcsr]['size'] is not None:
                        size = attr_yaml[dcsr]['size']
                        bsvstr +=(methoda_read_temp.format('Bit#('+str(size)
                            + ') _' + dcsr, dcsr))
                        incomming_reads.append(dcsr)

    # create methods for shadow csrs not in the current station
    for csrname, content in isa_yaml.items():
        subfields = []
        for s in content[rvxlen]['fields']:
            if isinstance(s, list):
                continue
            else:
                subfields.append(s)
        if not subfields:
            size = attr_yaml[csrname]['size']
            if content[rvxlen]['shadow'] is not None:
                if  logging:
                    logger.debug('-- Creating action/read methods for shadow csr :' + csrname)
                shadow_csr = content[rvxlen]['shadow'].split('.')[0]
                if shadow_csr not in isa_yaml and \
                        shadow_csr not in incomming_reads and\
                        attr_yaml[shadow_csr]['size']is not None:
                    bsvstr +=(methoda_read_temp.format('Bit#('+str(size)
                            + ') _' + shadow_csr, shadow_csr))
                    incomming_reads.append(shadow_csr)

    # create methods for custom interrupts
    if 'mip' in isa_yaml:
        for ci in aux_info['custom_interrupts']:
            bsvstr += '\n    method Action ma_set_mip_{0} (Bit#(1) _{0});'.format( \
                ci['cause_name'])
    if logging:
        logger.info('Interface created for : ' + pkg_name)
    # define generic methods for all stations
    bsvstr +=(method_station_generic)
    if debug_enabled:
        bsvstr += method_station_generic_debug
    if not last:
        bsvstr +=(method_fwd_temp)
    bsvstr += (end_interface_temp)
    return bsvstr

def station_module(isa_yaml, grp_yaml, attr_yaml, rvxlen, pkg_name,
        last, bsvstr, logging = False):

    '''
        Function to create the bluespec module syntax and other synthesis
        attributes of the module

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''

    if logging:
        logger.info('Creating module for : ' + pkg_name)
    xlen = int(rvxlen[2:])
    attr_str = ''
    for csrname in isa_yaml:
        if 'mod_attributes' in attr_yaml[csrname]:
            for modattr in attr_yaml[csrname]['mod_attributes']:
               if '::' in modattr :
                        condition, _modattr = re.findall(r'^(.*?)::(.*?)$',modattr)[0]
                        if eval(condition) :
                           attr_str += _modattr +'\n'
               else:
                attr_str += '  ' + modattr + '\n'
    bsvstr += (module_temp.format(pkg_name, attr_str, ''))
    if logging:
        logger.info('Module created for : ' + pkg_name)

    return  bsvstr

def station_modbody (isa_yaml, grp_yaml, attr_yaml, rvxlen, pkg_name,
        last, bsvstr, logging = False):
    '''
        Function to create the bluespec module rules/body requirements per csr
        basis

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''

    if logging:
        logger.info('Creating custom rules/module elements for : ' + pkg_name)
    for csrname in isa_yaml:
        if 'module_body' in attr_yaml[csrname]:
            bsvstr += textwrap.indent(attr_yaml[csrname]['module_body'],'    ') + '\n'
    if logging:
        logger.info('Custom rules/module elements created for : ' + pkg_name)
    return bsvstr

def station_methods(isa_yaml, grp_yaml, attr_yaml, aux_info, rvxlen, pkg_name,
        last, bsvstr, logging = False):
    '''
        Function to create the bluespec method definitions for each
        group/station. First the value methods of each csr in the group is
        created. Followed by custom action method and then the shadow/dependent
        csrs.

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''

    global debug_enabled

    xlen = int(rvxlen[2:])
    if logging:
        logger.info('Creating method definitions for : ' + pkg_name)

    # default value methods
    for csrname in isa_yaml:
        if logging:
            logger.debug('-- Defining value methods for : ' + csrname)
        if attr_yaml[csrname]['value_method']['required']:
            size = attr_yaml[csrname]['size']
            if 'dec_body' in attr_yaml[csrname]['value_method']:
                for _str in attr_yaml[csrname]['value_method']['dec_body']:
                    _str = _str.replace('size', str(size))
                    _str = _str.replace('xlen', str(xlen))
                    if '::' in _str:
                        cond = _str.split('::')[0]
                        if eval(cond):
                            _str = _str.split('::')[1]
                            bsvstr += methodv_def_temp.format(csrname, '', _str)
                    else:
                        bsvstr += methodv_def_temp.format(csrname,'',_str)
            else:
                bsvstr += methodv_def_temp.format(csrname, 'rg_', csrname)

    # custom action methods
    for csrname in isa_yaml:
        if logging:
            logger.debug('-- Defining custom Action methods for : ' + csrname)
        if attr_yaml[csrname]['action_method']['required']:
            size = attr_yaml[csrname]['size']
            for _str in attr_yaml[csrname]['action_method']['dec_body']:
                _str = _str.replace('size', str(size))
                _str = _str.replace('xlen', str(xlen))
                if '::' in _str:
                    cond = _str.split('::')[0]
                    if eval(cond):
                        _str = _str.split('::')[1]
                    else:
                        _str = ''
                bsvstr += textwrap.indent( _str+ '\n', '    ')

    # create action methods of dependent csrs
    incomming_reads = []
    for csrname in isa_yaml:
        if 'depends_on_csr' in attr_yaml[csrname]:
            if len(attr_yaml[csrname]['depends_on_csr']) != 0:
                if logging:
                    logger.debug('-- Defining action methods for dependencies of : ' + csrname)
                for dependent in attr_yaml[csrname]['depends_on_csr']:
                    create_sideband = True
                    dcsr = dependent
                    if '::' in dependent:
                        condition, csr = re.findall(r'^(.*?)::(.*?)$',dependent)[0]
                        if eval(condition) :
                            dcsr = csr
                        else:
                            create_sideband = False
                    if create_sideband and dcsr not in isa_yaml and \
                            dcsr not in incomming_reads \
                            and attr_yaml[dcsr]['size'] is not None:
                        size = attr_yaml[dcsr]['size']
                        if 'reg_instantiation' in attr_yaml[csrname]:
                            if len(attr_yaml[csrname]['reg_instantiation']) !=0 :
                                bsvstr += temp_method_shadow.format(str(size), dcsr)
                        else:
                            bsvstr += temp_method_shadow.format(str(size), dcsr)
                        incomming_reads.append(dcsr)
    # create methods for shadow csrs not in the current station
    for csrname, content in isa_yaml.items():
        subfields = []
        for s in content[rvxlen]['fields']:
            if isinstance(s, list):
                continue
            else:
                subfields.append(s)
        if not subfields:
            size = attr_yaml[csrname]['size']
            if content[rvxlen]['shadow'] is not None:
                if logging:
                    logger.debug('-- Defining Action methods for shadows of : ' + csrname)
                shadow_csr = content[rvxlen]['shadow'].split('.')[0]
                if shadow_csr not in isa_yaml and\
                        attr_yaml[shadow_csr]['size']is not None and \
                        shadow_csr not in incomming_reads:
                    if 'reg_instantiation' in attr_yaml[csrname]:
                        if len(attr_yaml[csrname]['reg_instantiation']) !=0 :
                            bsvstr += temp_method_shadow.format(str(size), shadow_csr)
                    else:
                        bsvstr += temp_method_shadow.format(str(size), shadow_csr)
                    incomming_reads.append(shadow_csr)
    req_ifc = []
    for csrname in isa_yaml:
        if csrname.lower() in attr_yaml and 'additional_method_body' in attr_yaml[csrname.lower()]:
            for add_ifc in attr_yaml[csrname.lower()]['additional_method_body']:
                if '::' in add_ifc:
                    cond = add_ifc.split('::')[0]
                    if cond:
                        add_ifc = add_ifc.split('::')[1]
                    else:
                        add_ifc = ''
                if add_ifc not in req_ifc:
                    bsvstr +=\
                        textwrap.indent(add_ifc, '    ') + '\n'
                    req_ifc.append(add_ifc)

    # create methods for custom interrupts
    if 'mip' in isa_yaml:
        for ci in aux_info['custom_interrupts']:
            bsvstr += '''
    method Action ma_set_mip_{0} (Bit#(1) _{0});
        rg_mip_{0} <= _{0};
    endmethod:ma_set_mip_{0}
'''.format(ci['cause_name'])

    bsvstr += method_generic_def_temp
    if debug_enabled:
        bsvstr += method_generic_debug_def_temp
    if not last:
        bsvstr += method_fwd_def_temp
    return bsvstr

def station_req(isa_yaml, grp_yaml, attr_yaml, rvxlen, pkg_name,
        last, bsvstr, logging = False):
    '''
        The function to create the final methods which serves the request from
        the core for each csr.

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''
    global debug_enabled
    global compressed_enabled
    global supervisor_enabled
    global hypervisor_enabled
    global satp_mode_condition
    if supervisor_enabled:
        satp_mode_condn = satp_mode_condition

    if logging:
        logger.info('Generating Core request routine for : ' + pkg_name)
    bsvstr += method_csr_req_def_temp.format(pkg_name)
    bsvstr += method_case_req
    xlen = int(rvxlen[2:])

    for csrname in isa_yaml:
        size = attr_yaml[csrname]['size']
        address = isa_yaml[csrname]['address']
        ro = False
        is_shadow = False
        shadow_csr = None
        regname = csrname

        if not isa_yaml[csrname][rvxlen]['fields'] :
            if isa_yaml[csrname][rvxlen]['shadow'] is not None:
                is_shadow = True
                shadow_csr = isa_yaml[csrname][rvxlen]['shadow']

        if (address & 0xC00) == 0xC00:
            ro = True

        if 'write_condition' in attr_yaml[csrname]:
            write_cond = attr_yaml[csrname]['write_condition']
        else:
            write_cond = ''

        if is_shadow:
            regname = shadow_csr.replace('.','_')
        logger.debug('Case statement for ' +csrname + ' Address: ' +\
                str(address))

        if 'csr_op' in attr_yaml[csrname] and (\
                shadow_csr is None or shadow_csr.split('.')[0] in isa_yaml):
                for csrop in attr_yaml[csrname]['csr_op']:
                    if '::' in csrop:
                        cond = csrop.split('::')[0]
                        if eval(cond):
                            cust_csrop = csrop.split('::')[1]
                            if logging:
                                logger.debug('-- Creating custom logic for : ' + csrname)
                            break
                        else:
                            cust_csrop = ''
                    else:
                        cust_csrop = csrop
                        break
                _t = cust_csrop.format(**locals())
                _t = textwrap.indent(_t, '            ') + '\n'
                bsvstr += _t
        elif ro:
            bsvstr += case_def_ro.format(csrname.upper(), regname, xlen)
            if logging:
                logger.debug('-- Creating read-only logic for : ' + csrname)
        else:
            bsvstr += case_def.format(csrname.upper(), regname, xlen, write_cond)
            if logging:
                logger.debug('-- Creating default logic for : ' + csrname)

    if last:
        bsvstr += (endcase_temp)
    else:
        bsvstr += (endcase_fwd_temp.format(pkg_name))
    if logging:
        logger.info('Core request routine created for : ' + pkg_name)

    return bsvstr

def station_regs(isa_yaml, grp_yaml, attr_yaml, aux_info, rvxlen, pkg_name,
        last, bsvstr, logging = False):
    '''
        Function to create the register and wires required to create the csrs.
        The function also creates WARL bluespec syntax using the
        derive_warl_func function.

        First the shadow/dependent wires are declared followed by the
        instantiation of the csrs present in the current group

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkg_name: name of the bluespec package this code belongs to.
        :param last: indicating this is the last station in the chain
        :param bsvstr: string containing rest of the code generated for the particular group/station
        :param work_dir: path to the directory where the bluespec files should be generated

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkg_name: str
        :type last: bool
        :type bsvstr: str
        :type work_dir: str
    '''
    global debug_enabled
    global physical_addr_sz
    global pmp_grain

    if logging:
        logger.info('Generating storage elements for : ' + pkg_name)
    bsvstr += (other_vars_temp)
    if debug_enabled:
        bsvstr += other_vars_debug_temp
    shadows = []
    xlen = int(rvxlen[2:])
    # creating additional required registers
    req_regs = []
    for csrname in isa_yaml:
        if 'pmpaddr' in csrname:
            if pmp_grain == 0:
                bsvstr += pmp_masks_grain0.format(physical_addr_sz-2)
            elif pmp_grain == 1:
                bsvstr += pmp_masks_grain1.format(physical_addr_sz-2)
            else:
                bsvstr += pmp_masks_grain2.format(physical_addr_sz-2)
            break
    for csrname in isa_yaml:
        if csrname in attr_yaml and 'additional_regs' in attr_yaml[csrname.lower()]:
            for add_reg in attr_yaml[csrname.lower()]['additional_regs']:
                if '::' in add_reg:
                    cond = add_reg.split('::')[0]
                    if eval(cond):
                        add_reg = add_reg.split('::')[1]
                    else:
                        add_reg = ''
                if add_reg not in req_regs:
                    bsvstr += '\n'+textwrap.indent(add_reg,'    ')
                    req_regs.append(add_reg)
#        if csrname.upper() in additional_regs:
#            if additional_regs[csrname.upper()] not in req_regs:
#                bsvstr += textwrap.indent(additional_regs[csrname.upper()],'    ')
#                req_regs.append(additional_regs[csrname.upper()])

    # create wires of dependent csrs
    incomming_reads = []
    for csrname in isa_yaml:
        if 'depends_on_csr' in attr_yaml[csrname]:
            if len(attr_yaml[csrname]['depends_on_csr']) != 0:
                for dependent in attr_yaml[csrname]['depends_on_csr']:
                    create_sideband = True
                    dcsr = dependent
                    if '::' in dependent:
                        condition, csr = re.findall(r'^(.*?)::(.*?)$',dependent)[0]
                        if eval(condition) :
                            dcsr = csr
                        else:
                            create_sideband = False
                    if create_sideband and dcsr not in isa_yaml and \
                            dcsr not in incomming_reads \
                            and attr_yaml[dcsr]['size'] is not None:
                        size = attr_yaml[dcsr]['size']
                        bsvstr += temp_wire.format(size, dcsr)
                        incomming_reads.append(dcsr)


    for csrname,content in isa_yaml.items():
        if logging:
            logger.debug('-- Creating storage for : ' + csrname)
        subfields = []
        for s in content[rvxlen]['fields']:
            if isinstance(s, list):
                continue
            else:
                subfields.append(s)
        description = content['description']
        reset_val = content['reset-val']
        size = attr_yaml[csrname]['size']
        concat = []

        if not subfields:
            if 'reg_instantiation' in attr_yaml[csrname]:
                if len(attr_yaml[csrname]['reg_instantiation']) !=0 :
                    bsvstr += attr_yaml[csrname]['reg_instantiation'] + '\n'
            elif content[rvxlen]['shadow'] is not None:
                shadow_csr = content[rvxlen]['shadow'].split('.')[0]
                if shadow_csr not in isa_yaml and shadow_csr not in incomming_reads and\
                        attr_yaml[shadow_csr]['size']is not None:
                    bsvstr += temp_wire.format(size, shadow_csr)
                    incomming_reads.append(shadow_csr)
            elif 'ro_constant' in content[rvxlen]['type']:
                bsvstr += temp_readOnlyRegister.format(description, str(size),
                        csrname, reset_val)
            elif ('warl' in content[rvxlen]['type']):
                bsv_str = derive_warl_func( csrname, str(size),
                        content[rvxlen]['type']['warl']['legal'],
                        content[rvxlen]['type']['warl']['dependency_fields'])
                if 'pmpaddr' in csrname:
                    pmpaddrnum = int(csrname.split('pmpaddr')[1],10)
                    pmpcfgnum = int(pmpaddrnum / int(xlen/8))
                    bsvstr += temp_warlReg_pmpaddr.format(description,
                            physical_addr_sz-2, csrname, reset_val, bsv_str,
                            pmpcfgnum, pmpaddrnum)
                else:
                    bsvstr += temp_warlReg.format(description, str(size),
                            csrname, reset_val, bsv_str)
            else:
                bsvstr +=  temp_register.format(description, str(xlen), csrname,
                        reset_val)
        else:
            for subfield in subfields:
                if logging:
                    logger.debug('|---- Subfield: ' + subfield)
                if subfield is not 'wlrl':
                    subcontent = isa_yaml[csrname][rvxlen][subfield]
                    if 'type' in subcontent:
                        type_reg = subcontent['type']
                    else:
                        type_reg = ''
                    msb = subcontent['msb']
                    lsb = subcontent['lsb']
                    subdescription = subcontent['description']
                    width = msb - lsb + 1
                    subreset_val = get_reset_val(reset_val, width, lsb, str(xlen))
                    storage_type = 'rg_'
                    if subcontent['shadow'] is not None:
                        if subcontent['shadow_type'] == 'ro':
                            type_reg = 'ro_variable'
                        else:
                            type_reg = 'warl'
                        concat.append([ msb, width,
                            subcontent['shadow'].replace('.','_'), type_reg,
                            storage_type])
                    else:
                        concat.append([ msb, width, csrname + '_' + subfield,
                         type_reg, storage_type])

                    if subfield == 'sd' and csrname == 'mstatus':
                        bsvstr += temp_readOnlyRegister.format(subdescription,
                                str(width), csrname+'_'+subfield,
                                "pack((rg_mstatus_xs == 2\'b11) || (rg_mstatus_fs == 2\'b11))")
                    elif subfield in ['meip','msip','mtip']:
                        bsvstr += temp_wire.format(width,csrname+'_'+subfield)
                    elif subcontent['shadow'] is not None:
                        shadow_csr = subcontent['shadow'].split('.')[0]
                        if (shadow_csr not in isa_yaml and #shadow_csr not in incomming_reads #and\
                                attr_yaml[shadow_csr]['size']is not None)  :
                            bsvstr += temp_readOnlyRegister.format(subdescription,str(width), shadow_csr+'_'+subfield, 0)
                            #incomming_reads.append(shadow_csr)
                        elif shadow_csr not in isa_yaml and attr_yaml[shadow_csr]['size']is None:
                            bsvstr += temp_readOnlyRegister.format(subdescription,str(width), shadow_csr+'_'+subfield, 0)
                    elif 'ro_constant' in type_reg:
                        bsvstr += temp_readOnlyRegister.format(subdescription,
                                str(width), csrname+'_'+subfield, subreset_val)
                    elif 'ro_variable' in type_reg:
                        bsvstr += temp_register.format(subdescription,
                                str(width), csrname+'_'+subfield, subreset_val)
                    elif 'warl' in type_reg:
                        bsv_str = derive_warl_func( subfield,
                            str(width),subcontent['type']['warl']['legal'],
                            subcontent['type']['warl']['dependency_fields'])
                        bsvstr += temp_warlReg.format(subdescription,
                                    str(width), csrname+'_'+subfield, subreset_val, bsv_str)
                    elif 'wlrl' in type_reg:
                        full_wlrl, awidth = derive_wlrl_func(subcontent['type']['wlrl'])
                        if full_wlrl:
                            bsvstr +=  temp_register.format(subdescription,
                                str(width), csrname+'_'+subfield, subreset_val)
                        else:
                            bsvstr += temp_wlrlReg.format(subdescription,
                                    str(width), csrname+'_'+subfield, \
                                            subreset_val, awidth)
                    else:
                        bsvstr += temp_readOnlyRegister.format(subdescription,
                                str(width), csrname+'_'+subfield, 0)
            if csrname.lower() in ['mie']:
                for ci in aux_info['custom_interrupts']:
                    bsvstr += temp_register.format('',1,csrname+'_'+ci['cause_name'],ci['on_reset_enable'])
                    concat.append([ci['cause_val'],1,csrname+'_'+ci['cause_name'],'','rg_'])
            if csrname.lower() in ['sie']:
                for ci in aux_info['custom_interrupts']:
                    if ci['priv_mode']== 'S':
                        concat.append([ci['cause_val'],1,'mie_'+ci['cause_name'],'','rg_'])
            if csrname.lower() in ['mip']:
                for ci in aux_info['custom_interrupts']:
                    bsvstr += temp_wire.format(1,csrname+'_'+ci['cause_name'])
                    concat.append([ci['cause_val'],1,csrname+'_'+ci['cause_name'],'ro_variable', 'rg_'])
            length, cv = create_concat_vector(concat, int(xlen))
            bsvstr += concat_temp.format(description, xlen, csrname,\
                      length, cv)
        if 'reg_dec' in attr_yaml[csrname]['action_method'] :
            bsvstr += attr_yaml[csrname]['action_method']['reg_dec']
            if logging:
                logger.debug('-- Creating external pending interrupt logic for : ' + csrname)

    if logging:
        logger.info('Storage elements created for : ' + pkg_name)
    return bsvstr

def find_group(bar, csrname, logging=False):
    '''
        Function to find the group which a particular csr belongs to in the
        grouping yaml

        :param bar: the grouping YAML
        :param csrname: the name of the csr
        :type bar: dict
        :type csrname: str

        :return: name of thr group where the csr belongs. None if it is absent altogether
    '''
    for grps in bar:
        if csrname.upper() in bar[grps]:
            return grps
    return None

def csr_top(isa_yaml, grp_yaml, attr_yaml, aux_info, rvxlen, pkgname, logging = False):
    '''
        Function to create the top level bluespec module which instantiates the
        individual group/station and creates the connection between them.

        The function also creates the methods required for handling traps and
        returns.

        :param isa_yaml: the riscv-config isa YAML
        :param grp_yaml: the grouping YAML
        :param attr_yaml: the attributes YAML
        :param rvxlen: a string containing the format: "rv32" or "rv64" depending on the XLEN value of the DUT
        :param pkgname: name of the bluespec package this code belongs to.

        :type isa_yaml: dict
        :type grp_yaml: dict
        :type attr_yaml: dict
        :type rvxlen: str
        :type pkgname: str
    '''
    global debug_enabled
    global compressed_enabled
    global physical_addr_sz

    grp_list = sorted(list(grp_yaml))
    xlen = int(rvxlen[2:])
    if logging:
        logger.info('Creating file Top file : ' + str(pkgname))
    bsvstr = ''

    # initial license and imports
    bsvstr += license_header.format(version, str(datetime.datetime.now()))
    bsvstr += package_temp.format(pkgname)

    misa_grp = find_group(grp_yaml, 'misa')
    mstatus_grp = find_group(grp_yaml, 'mstatus')
    mstatush_grp = find_group(grp_yaml, 'mstatush')
    mepc_grp = find_group(grp_yaml, 'mepc')
    mtval_grp = find_group(grp_yaml, 'mtval')
    mtval2_grp = find_group(grp_yaml, 'mtval2')
    mcause_grp = find_group(grp_yaml, 'mcause')
    mtinst_grp = find_group(grp_yaml, 'mtinst')
    mtvec_grp = find_group(grp_yaml, 'mtvec')
    sstatus_grp = find_group(grp_yaml, 'sstatus')
    sepc_grp = find_group(grp_yaml, 'sepc')
    stval_grp = find_group(grp_yaml, 'stval')
    scause_grp = find_group(grp_yaml, 'scause')
    stvec_grp = find_group(grp_yaml, 'stvec')
    vsepc_grp = find_group(grp_yaml, 'vsepc')
    vstval_grp = find_group(grp_yaml, 'vstval')
    vsstatus_grp = find_group(grp_yaml, 'vsstatus')
    vscause_grp = find_group(grp_yaml, 'vscause')
    vstvec_grp = find_group(grp_yaml, 'vstvec')
    htval_grp = find_group(grp_yaml, 'htval')
    htinst_grp = find_group(grp_yaml, 'htinst')
    hstatus_grp = find_group(grp_yaml, 'hstatus')
    ustatus_grp = find_group(grp_yaml, 'ustatus')
    uepc_grp = find_group(grp_yaml, 'uepc')
    utval_grp = find_group(grp_yaml, 'utval')
    ucause_grp = find_group(grp_yaml, 'ucause')
    utvec_grp = find_group(grp_yaml, 'utvec')
    medeleg_grp = find_group(grp_yaml, 'medeleg')
    mideleg_grp = find_group(grp_yaml, 'mideleg')
    sedeleg_grp = find_group(grp_yaml, 'sedeleg')
    sideleg_grp = find_group(grp_yaml, 'sideleg')
    hedeleg_grp = find_group(grp_yaml, 'hedeleg')
    hideleg_grp = find_group(grp_yaml, 'hideleg')
    dpc_grp = find_group(grp_yaml,'dpc')
    dcsr_grp_name = find_group(grp_yaml,'dcsr')
    mip_grp_name = find_group(grp_yaml, 'mip')

    if debug_enabled:
        if dpc_grp is None or dcsr_grp_name is None:
            logger.error('Debug is enabled but one/both of dpc, dcsr is not available in any group')
            sys.exit(1)

    pmp_entries = 0


    usertraps = False
    if None not in (ustatus_grp, uepc_grp, utval_grp, ucause_grp, utval_grp):
        usertraps = True
    supervisor = False
    if None not in (sstatus_grp, sepc_grp, stval_grp, scause_grp, stval_grp):
        supervisor = True
    hypervisor=False
    if None not in (hstatus_grp, htval_grp, htinst_grp, vsepc_grp, vstval_grp, vscause_grp, vstvec_grp):
        hypervisor = True

    # imports of each station
    if logging:
        logger.debug('-- Creating imports')
    for groups in grp_yaml:
        bsvstr += 'import csrbox_' + groups + ' :: * ;\n'
    bsvstr += 'import csrbox_decoder :: * ;'


    if logging:
        logger.debug('-- Creating interface')
    # define a value method for each csr.
    bsvstr += '''
  interface Sbread;'''
    for csrname in isa_yaml:
        if logging:
            logger.debug('-- Creating Interface for ' + csrname)
        if attr_yaml[csrname]['value_method']['required']:
            size = attr_yaml[csrname]['size']
            if 'pmpaddr' in csrname:
                size = physical_addr_sz -2
            bsvstr +=(methodv_dec_temp.format(size, csrname))
    bsvstr += '''
  endinterface:Sbread'''



    bsvstr += interface_temp.format(pkgname)
    bsvstr += '''    interface Sbread sbread;\n'''
    # define additional required interfaces
    req_ifcs = []
    for csrname in isa_yaml:
        if csrname.lower() in attr_yaml and 'additional_top_method' in attr_yaml[csrname.lower()]:
            for add_ifc in attr_yaml[csrname.lower()]['additional_top_method']:
                if '::' in add_ifc:
                    cond = add_ifc.split('::')[0]
                    if cond:
                        add_ifc = add_ifc.split('::')[1]
                    else:
                        add_ifc = ''
                if add_ifc not in req_ifcs:
                    bsvstr +=\
                        textwrap.indent(add_ifc, '    ') + '\n'
                    req_ifcs.append(add_ifc)
        if 'pmpaddr' in csrname.lower():
            if isa_yaml[csrname]['rv'+str(xlen)]['accessible']:
                pmp_entries += 1

    # pmp methods if required
    if pmp_entries > 0:
        bsvstr += pmp_ifc.format(pmp_entries, physical_addr_sz)

    # define csr specific action methods.
    for csrname in isa_yaml:
        if logging:
            logger.debug('-- Creating custom action methods for : ' + csrname)
        if attr_yaml[csrname]['action_method']['required'] and \
                attr_yaml[csrname]['action_method']['global']:
            size = attr_yaml[csrname]['size']
            for arguments in attr_yaml[csrname]['action_method']['def_arguments']:
                arguments = arguments.replace('xlen',str(xlen))
                arguments = arguments.replace('size',str(size))
                if '::' in arguments:
                    cond, args = re.findall(r'^(.*?)::(.*?)$',arguments)[0]
                    if eval(cond):
                        args = textwrap.indent(args, '')
                    else:
                        args = ''
                else:
                    args = arguments
                bsvstr +=('\n    '+args)

    for ci in aux_info['custom_interrupts']:
        bsvstr += '\n    method Action ma_set_mip_{0} (Bit#(1) _{0});'.format( \
                ci['cause_name'])
    # debug specific interfaces
    if debug_enabled:
        bsvstr += method_top_debug_dec;
    bsvstr += ('\n')
    if hypervisor_enabled:
        bsvstr += (method_top_generic_h.format(xlen))
    else:
        bsvstr += (method_top_generic.format(xlen))
    bsvstr += (end_interface_temp)
    # -------------- interface definition done ------------------------------#

    #--- create module
    if logging:
        logger.debug('-- Creating module')
    mod_attr_str = ''
    if 'minstret' in isa_yaml:
        if isa_yaml['minstret']['rv'+str(xlen)]['accessible']:
            mod_attr_str = '(*conflict_free="ma_incr_minstret,sbread.mv_csr_minstret"*)'

    for i in range(len(grp_list)-1):
        mod_attr_str += '\n(*mutually_exclusive="mav_upd_on_trap,x{0}_mkConnectionAVtoAf"*)'.format(str(i))
        mod_attr_str += '\n(*mutually_exclusive="mav_upd_on_ret,x{0}_mkConnectionAVtoAf"*)'.format(str(i))
    extra_reset = ''
    bsvstr += top_module_temp.format(pkgname,mod_attr_str, extra_reset) + '\n'

    if logging:
        logger.debug('-- Instatiating groups')
    # -- instantiate groups
    for grps in grp_yaml:
        bsvstr += '    let ' + grps + ' <- mk_csrbox_' + grps + ';\n'

    bsvstr += '''
    let lv_misa_s = {0}.mv_csr_misa[18];
    let lv_misa_h = {0}.mv_csr_misa[7];
    let lv_misa_u = {0}.mv_csr_misa[20];
    let lv_misa_n = {0}.mv_csr_misa[13];
    let lv_misa_c = {0}.mv_csr_misa[2];
    /*doc:reg: holds the current privilege level*/
    Reg#(Privilege_mode) rg_prv <- mkReg(Machine);
    /*doc:reg: holds the current virtual mode */
    Reg#(Bit#(1)) rg_virtual <- mkReg(0);
'''.format(misa_grp)

    if debug_enabled:
        bsvstr += '''
    /*doc:reg:The register indicates that the core is in debug mode*/
    Reg#(Bit#(1)) rg_debug_mode <- mkReg(0);
'''

    anyhit = ''
    anydata = ''
    anyupdated = ''
    for grp in grp_yaml:
        anyhit += grp + '.mv_core_resp.hit' + ' || '
        anydata += grp + '.mv_core_resp.data' + ' | '
        anyupdated += grp + '.mv_core_resp.csr_updated' + ' || '
    anyhit = anyhit[:-4]
    anydata = anydata[:-3]
    anyupdated = anyupdated[:-3]
    bsvstr += check_hit_temp.format(anyhit, anydata, xlen, anyupdated)

    # additional wires/regs
    req_regs = []
    for csrname in isa_yaml:
        if csrname.lower() in attr_yaml and 'additional_top_regs' in attr_yaml[csrname.lower()]:
            grp_name = find_group(grp_yaml, csrname.upper())
            for add_reg in attr_yaml[csrname.lower()]['additional_top_regs']:
                add_reg = add_reg.replace('grp_name',str(grp_name))
                if '::' in add_reg:
                    cond = add_reg.split('::')[0]
                    if cond:
                        add_reg = add_reg.split('::')[1]
                    else:
                        add_reg = ''
                if add_reg not in req_regs and add_reg != '' :
                    bsvstr +=\
                        textwrap.indent(add_reg, '    ') + '\n'
                    req_regs.append(add_reg)

    # req=response connection across stations
    if logging:
        logger.debug('-- Creating connections between core-fwd interfaces')
    for i in range(len(grp_list)-1):
        bsvstr += temp_req_connection.format(grp_list[i], grp_list[i+1], str(i))

    # -- connect rg_prv to all stations
    for grp in grp_yaml:
        bsvstr += temp_prv_connection.format(grp)
        if debug_enabled:
            bsvstr += temp_dbg_connection.format(grp)


    # create action methods of dependent csrs
    if logging:
        logger.debug('-- defining action methods')
    for grp in grp_yaml:
        incomming_reads = []
        if grp_yaml[grp] != None :
         for csrs in grp_yaml[grp]:
            csrname = csrs.lower()
            if 'depends_on_csr' in attr_yaml[csrname]:
                if len(attr_yaml[csrname]['depends_on_csr']) != 0:
                    for dependent in attr_yaml[csrname]['depends_on_csr']:
                        create_sideband = True
                        dcsr = dependent
                        if '::' in dependent:
                            condition, csr = re.findall(r'^(.*?)::(.*?)$',dependent)[0]
                            if eval(condition) :
                                dcsr = csr
                            else:
                                create_sideband = False
                        if create_sideband and dcsr.upper() not in grp_yaml[grp] and \
                                dcsr not in incomming_reads \
                                and attr_yaml[dcsr]['size'] is not None:
                            if logging:
                                logger.debug('-- Creating connections for dependencies\
 of csr: ' +csrname + ' : ' +  str(dcsr))
                            dcsr_grp = find_group(grp_yaml, dcsr)
                            bsvstr += temp_top_csr_connection.format(\
                                    grp, dcsr, dcsr_grp )
                            incomming_reads.append(dcsr)
            subfields = []
            for s in isa_yaml[csrname][rvxlen]['fields']:
                if isinstance(s, list):
                    continue
                else:
                    subfields.append(s)
            if not subfields:
                size = attr_yaml[csrname]['size']
                if isa_yaml[csrname][rvxlen]['shadow'] is not None:
                    shadow_csr = isa_yaml[csrname][rvxlen]['shadow'].split('.')[0]
                    if shadow_csr.upper() not in grp_yaml[grp] and \
                            shadow_csr not in incomming_reads and\
                            attr_yaml[shadow_csr]['size']is not None:
                        if logging:
                            logger.debug('-- Creating connections for shadows of csr: ' +csrname + ' : ' + shadow_csr)
                        shadow_grp = find_group(grp_yaml, shadow_csr)
                        bsvstr += temp_top_csr_connection.format(\
                                    grp, shadow_csr, shadow_grp )
                        incomming_reads.append(shadow_csr)

    # return and trap method definitions
    if logging:
        logger.debug('-- Defining trap and return methods')
    bsvstr += method_top_def_temp

    if debug_enabled:
        dret_str = dret_temp.format(dpc_grp, dcsr_grp_name, mstatus_grp)
    else:
        dret_str = ''

    if not supervisor_enabled:
        bsvstr += xret_mu.format(xlen, dret_str, mstatus_grp, mepc_grp)
    elif not hypervisor_enabled:
        bsvstr += xret_msu.format(xlen, dret_str, mstatus_grp, mepc_grp)
    else:
      if xlen == 64:
        bsvstr += xret_mhsu.format(xlen, dret_str, sepc_grp, vsstatus_grp,
                mstatus_grp, hstatus_grp, mepc_grp, vsepc_grp)
      else:
        bsvstr += xret_mhsu32.format(xlen, dret_str, sepc_grp, vsstatus_grp,
                mstatus_grp, hstatus_grp, mepc_grp, vsepc_grp, mstatush_grp)


    if debug_enabled:
        debug_trap_str = trap_debug.format(dpc_grp, dcsr_grp_name)
    else:
        debug_trap_str = ''

    if not supervisor:
        bsvstr += trap_mu.format(xlen, mtval_grp, mepc_grp, mcause_grp,
                mstatus_grp, mtvec_grp, debug_trap_str)
    elif supervisor and not hypervisor:
        bsvstr += trap_msu.format(xlen, medeleg_grp, mideleg_grp, stval_grp,
                sepc_grp, scause_grp, mstatus_grp, stvec_grp, mtval_grp,
                mepc_grp, mcause_grp, mtvec_grp, debug_trap_str)
    elif supervisor and hypervisor:
        if xlen == 64:
            bsvstr += trap_mhsu.format(xlen, medeleg_grp, mideleg_grp, hedeleg_grp,
                hideleg_grp, vstval_grp, vsepc_grp, vscause_grp, vstvec_grp,
                vsstatus_grp, scause_grp, sepc_grp, stval_grp, stvec_grp,
                htval_grp, htinst_grp, hstatus_grp, mstatus_grp, mtval_grp,
                mepc_grp, mcause_grp, mtval2_grp, mtinst_grp, mtvec_grp,
                debug_trap_str)
        else:
            bsvstr += trap_mhsu32.format(xlen, medeleg_grp, mideleg_grp, hedeleg_grp,
                hideleg_grp, vstval_grp, vsepc_grp, vscause_grp, vstvec_grp,
                vsstatus_grp, scause_grp, sepc_grp, stval_grp, stvec_grp,
                htval_grp, htinst_grp, hstatus_grp, mstatus_grp, mtval_grp,
                mepc_grp, mcause_grp, mtval2_grp, mtinst_grp, mtvec_grp,
                debug_trap_str, mstatush_grp)

    # define additional required interfaces
    req_ifc = []
    for csrname in isa_yaml:
        if csrname.lower() in attr_yaml and 'additional_top_method_body' in attr_yaml[csrname.lower()]:
            for add_ifc in attr_yaml[csrname.lower()]['additional_top_method_body']:
                if '::' in add_ifc:
                    cond = add_ifc.split('::')[0]
                    if cond:
                        add_ifc = add_ifc.split('::')[1]
                    else:
                        add_ifc = ''
                if add_ifc not in req_ifc:
                    bsvstr +=\
                        textwrap.indent(add_ifc, '    ') + '\n'
                    req_ifc.append(add_ifc)

    # pmp method definitions
    pmpaddr_str = ''
    pmpcfg_str = ''
    cfg_count = 0
    count = 0
    if pmp_entries > 0:
        for csrname in isa_yaml:
            if 'pmpaddr' in csrname.lower():
                num = int(re.findall('\d+',csrname.lower())[0])
                grp = find_group(grp_yaml, csrname.upper())
                pmpaddr_str += "        lv_pmpaddr[{0}] = {{truncate({1}.mv_csr_{2}),2'b0}};\n".format(\
                        count, grp, csrname.lower())
                count += 1

                # cgfs are notoriously ordered and hence the following logic
                cfg_num = (num // (xlen//8))
                if xlen == 64 and (cfg_num%2) == 1:
                    cfg_num = cfg_num + 1
                cfg_offset = int(num%(xlen//8))
                cfg_grp = find_group(grp_yaml, 'PMPCFG'+str(cfg_num))
                pmpcfg_str += \
            '        lv_pmpcfg[{0}] = {1}.mv_csr_pmpcfg{2}[{3}:{4}];\n'.format(\
                    cfg_count, cfg_grp, cfg_num, cfg_offset*8+7,
                    cfg_offset*8)
                cfg_count += 1
        bsvstr += pmpaddr_def.format(pmp_entries, physical_addr_sz, pmpaddr_str)
        bsvstr += pmpcfg_def.format(pmp_entries, pmpcfg_str)
    if hypervisor:
        bsvstr += '''
        method Action ma_core_req(CSRReq req) ;
            req.csr_address = fn_address_virtual(req.csr_address, rg_virtual);
            grp1.ma_core_req(req);
        endmethod '''
    else:
        bsvstr += '''
        method Action ma_core_req(CSRReq req) ;
            grp1.ma_core_req(req);
        endmethod '''
    # complete the value method for each csr.
    if logging:
        logger.debug('-- Defining value methods')
    bsvstr +='''
    interface Sbread sbread;'''
    for csrname in isa_yaml:
        if attr_yaml[csrname]['value_method']['required']:
            grp = find_group(grp_yaml, csrname.upper())
            bsvstr += textwrap.indent(methodv_def_temp.format(csrname, grp+'.mv_csr_', csrname), '  ')
    bsvstr +='''
    endinterface'''


    # define csr specific action methods.
    if logging:
        logger.debug('-- Defining custom action methods')
    for csrname in isa_yaml:
        logger.debug('Top CSR Interface: ' + csrname)
        if attr_yaml[csrname]['action_method']['required'] and \
                attr_yaml[csrname]['action_method']['global']:
#            defs =  attr_yaml[csrname]['action_method']['def_arguments']
            csr_grp = find_group(grp_yaml, csrname.upper())
            for arguments in attr_yaml[csrname]['action_method']['def_arguments']:
                arguments = arguments.replace('xlen',str(xlen))
                arguments = arguments.replace('size',str(size))
                if '::' in arguments:
                    cond, args = re.findall(r'^(.*?)::(.*?)$',arguments)[0]
                    if eval(cond):
                        args = textwrap.indent(args, '')
                    else:
                        args = ''
                else:
                    args = arguments
                methods = re.findall(r'\s*method\s*Action\s*(.*?)[\s(]', args)
                for x in methods:
                    bsvstr += methoda_top_temp.format(x, csr_grp)
    for ci in aux_info['custom_interrupts']:
        bsvstr += '\n    method ma_set_mip_{0} = {1}.ma_set_mip_{0};'.format( \
                ci['cause_name'], mip_grp_name)
    # debug specific interfaces
    if debug_enabled:
        bsvstr += method_top_debug_def.format(dcsr_grp_name);


    # -- end the module
    bsvstr += end_module_temp
    # end package
    bsvstr += end_package_temp
    return bsvstr

