import logging
from struct import unpack, pack
import numpy as np
from aug_sfutils import sfdics, str_byt
from aug_sfutils.sfhread import SFH_READ

n_rel = 8

logger = logging.getLogger('aug_sfutils.sfhwrite')
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)


for key, val in sfdics.obj_name.items():
    exec('%s=%d' %(val, key))


def object_length(sfobj):

    otyp = sfobj.obj_type
    if otyp not in (Signal, SignalGroup, TimeBase, AreaBase):
        return None
    type_len = sfdics.type_len(sfobj.data_format)

    if otyp == Signal:
        obj_length = type_len * sfobj.index[-1]
    elif otyp == TimeBase:
        obj_length = type_len * sfobj.n_steps
    elif otyp == SignalGroup:
        shape_arr = np.array(sfobj.index[::-1][:sfobj.num_dims])
        obj_length = np.prod(shape_arr) * type_len
    elif otyp == AreaBase:
        shape_arr = np.array([sfobj.size_x + sfobj.size_y + sfobj.size_z, sfobj.n_steps])
        obj_length = np.prod(shape_arr) * type_len

    return obj_length


def param_length(param):

    parmlen = 16 # ParName(=key), unit, dfmt, n_items
    dfmt = param.data_format
    bytlen = param.n_items * sfdics.type_len(dfmt)
    parmlen += 8 * ( (bytlen + 13)//8 )

    return parmlen


def parset_length(pset_d):

    psetlen = 0
    for param in pset_d.values():
        psetlen += param_length(param)

    return psetlen


def par2byt(pname, param):


    dfmt = param.data_format
    n_items = param.n_items

    if dfmt in sfdics.fmt2len.keys(): # char variable
        dlen = sfdics.fmt2len[dfmt]
        bytlen = n_items * dlen
        dj0 = 8 * ( (bytlen + 9)//8 ) 
    elif dfmt in sfdics.fmt2typ.keys(): # number
        sfmt = sfdics.fmt2struc[dfmt]
        type_len = np.dtype(sfmt).itemsize
        val_len = n_items + 2
        bytlen = val_len * type_len
        dj0 = str_byt.next8(bytlen)
    blen = 16 + dj0
    byt = bytearray(blen)
    byt[  :  8] = str_byt.to_byt(pname.ljust(8))
    byt[ 8: 10] = pack('>h', param.physunit)
    byt[10: 12] = pack('>h', dfmt)
    byt[12: 14] = pack('>h', n_items)
    byt[14: 16] = pack('>h', param.status)
    if dfmt in sfdics.fmt2len.keys(): # character variable
        byt[16: 17] = param.dmin
        byt[17: 18] = param.dmax
        param = np.atleast_1d(param)
        for jitem in range(n_items):
            if len(param[jitem]) > 0:
                byt[18 + jitem*dlen: 18 + (jitem+1)*dlen] = param[jitem].ljust(dlen)
    elif dfmt in sfdics.fmt2typ.keys(): # number
        if dfmt == 7: # logical, bug if n_items > 1?
            byt[16: 17] = pack('>%s' %sfmt, param.dmin)
            byt[19: 20] = pack('>%s' %sfmt, param.dmax)
            byt[21: 22] = pack('>%s' %sfmt, param)
        else:
            byt[16         : 16+  type_len] = pack('>%s' %sfmt, param.dmin)
            byt[16+type_len: 16+2*type_len] = pack('>%s' %sfmt, param.dmax)
            param = np.atleast_1d(param)
            for jitem in range(n_items):
                byt[16 + (jitem+2)*type_len: 16 + (jitem+3)*type_len] = pack('>%s' %sfmt, param[jitem])

    return byt


def set_signals(sfo):

# SIGNALS list generated automatically, override input entry
    sigs = type('', (), {})()

    obj_list = []
    for jid in range(len(sfo.sfh)):
        objnam = sfo.getobjname(jid)
        sfobj = sfo.sfh[objnam]
        otyp = sfobj.obj_type
        if otyp in (SignalGroup, Signal, TimeBase, AreaBase): # Include areabases too
            obj_list.append(jid)

    sigs.nitems = len(obj_list)
    sigs.address = len(sfo.sfh)*128
    sigs.length = sigs.nitems*2
    sigs.data_format = 3
    sfmt = sfdics.fmt2struc[sigs.data_format]
    byt_objlist = pack('>%d%s' %(sigs.nitems, sfmt), *obj_list)
    bytlen = len(byt_objlist)
    dj0 = str_byt.next8(bytlen)
    sigs.objlist = bytearray(dj0)
    sigs.objlist[:bytlen] = byt_objlist

    return sigs


def set_length_address(sfo):

# ParSets

    logger.debug('Diag1 %s', sfo.diag)
    len_psets = 0
    for sfobj in sfo.sfh.values(): # sequence not important
        otyp = sfobj.obj_type
        if otyp in (ParamSet, ):
            sfobj.length = parset_length(sfobj.pars)
            len_psets += sfobj.length

# Set lengths and addresses

    sigs = set_signals(sfo)

    addr_diag = sigs.address + sigs.length + len_psets
    par_addr  = sigs.address + sigs.length 
    addr_diag = str_byt.next8(addr_diag)
    par_addr  = str_byt.next8(par_addr)

    addr = addr_diag

    for jid in range(len(sfo.sfh)):

        objnam = sfo.getobjname(jid)
        sfobj = sfo.sfh[objnam]
        otyp = sfobj.obj_type
        addr_in = sfobj.address # For debugging
        len_in  = sfobj.length  # For debugging
        if hasattr(sfobj, 'data_format'):
            type_len = sfdics.type_len(sfobj.data_format)
        else:
            type_len = 0

        if otyp == Diagnostic:
            sfobj.length = sfobj.length # GIT: evaluated at the end of the loop
            sfobj.address = addr
        elif otyp == List:
            if objnam == 'SIGNALS':
                for key, val in sigs.__dict__.items():
                    sfobj.__dict__[key] = val
                addr = addr_diag
        elif otyp in (Device, ParamSet):
            sfobj.address = par_addr
            par_addr += sfobj.length
        elif otyp == Signal:
            sfobj.length = object_length(sfobj)
            sfobj.address = addr
            addr += str_byt.next8(sfobj.length)
        elif otyp == TimeBase:
            sfobj.length = object_length(sfobj)
            sfobj.address = addr
            addr += str_byt.next8(sfobj.length)
        elif otyp == SignalGroup:
            shape_arr = np.array(sfobj.index[::-1][:sfobj.num_dims])
            sfobj.length = object_length(sfobj)
            sfobj.address = addr
            n_block = 2*((sfobj.length + 7)//8)
            addr += n_block*((sfobj.length + n_block-1)//n_block) + shape_arr[1]*2
        elif otyp == AreaBase:
            sfobj.length = object_length(sfobj)
            sfobj.address = addr
            addr += 8*((sfobj.length + 9)//8)
        else:
            continue

        logger.debug('%s (%s)' %(objnam, sfdics.obj_name[otyp]))
        logger.debug('Address in, out: %d %d', addr_in, sfobj.address)
        logger.debug('Length  in, out: %d %d', len_in , sfobj.length )

    len_tot = addr + sfobj.length + addr_diag

    sfobj = sfo.sfh[sfo.diag]
    len_in = sfobj.length
    sfobj.length = len_tot
    logger.debug('%s Length  in, out: %d %d', sfo.diag, len_in , sfobj.length )

    return sfo


def write_sfh(sfo_in, fout):
# Write SFH file

    sfo = set_length_address(sfo_in)
    f = open(fout, 'wb')

    len_sfh = 0
    for jid in range(len(sfo.sfh)):

        objnam = sfo.getobjname(jid)
        sfobj = sfo.sfh[objnam]

# Encode all attributes into byte strings(128)
        sfhbytes = SFH_WRITE(sfobj).bytstr
        f.write(sfhbytes)
        len_sfh += len(sfhbytes)

# Write SIGNALS list

    sigs = sfo.sfh['SIGNALS']
    f.write(sigs.objlist)
    len_sfh += len(sigs.objlist)

# Write content of ParSets
    for jid in range(len(sfo.sfh)):

        objnam = sfo.getobjname(jid)
        sfobj = sfo.sfh[objnam]
        otyp = sfobj.obj_type
        
        if otyp in (ParamSet, ):
            pset2byt = bytearray(parset_length(sfobj.pars))
            j0 = 0
            for pname, param in sfobj.pars.items():
                p2b = par2byt(pname, param)
                j1 = j0 + len(p2b)
                pset2byt[j0: j1] = p2b
                j0 = j1
            f.write(pset2byt)
    f.close()
    logger.info('Stored binary %s' %fout)


class SFH_WRITE:
    """
    Writes a generic SFH object metadata to a byte string
    """

    def __init__(self, sfo):
        """
        Writes the SFH part of an object
        """
        self.sfo = sfo
        objnam   = str_byt.to_byt(sfo.objnam)
        obj_type = pack('>H', sfo.obj_type)
        level    = pack('>H', sfo.level)
        status   = pack('>H', sfo.status)
        errcode  = pack('>h', sfo.errcode)
        rel      = pack('>8H', *sfo.rel)
        address  = pack('>I', sfo.address)
        length   = pack('>I', sfo.length)
        self.val = bytearray(24)
        descr    = str_byt.to_byt(sfo.descr)

        val_func = { \
            1 : self.sfdiag, 2: self.list, 3: self.device, 4: self.parmset, \
            5 : self.mapping, 6: self.sig, 7: self.sig, 8: self.tbase, \
            9 : self.sf_list, 10: self.algorithm, 11: self.update_set, \
            12: self.loctimer, 13: self.abase, 14: self.qualifier, \
            15: self.modobj, 16: self.mapext, 17: self.resource, \
            18: self.addrlen }

        if sfo.obj_type in val_func.keys():
#            logger.debug('%d %s %d', sfo.objid, sfo.objnam, sfo.obj_type)
            val_func[sfo.obj_type]()
        else:
            logger.warning('Object type %d not supported' %sfo.obj_type)

        self.bytstr = bytearray(128)
        self.bytstr[  :  8] = objnam.ljust(8)
        self.bytstr[ 8: 10] = obj_type
        self.bytstr[10: 12] = level
        self.bytstr[12: 14] = status
        self.bytstr[14: 16] = errcode
        self.bytstr[16: 32] = rel
        self.bytstr[32: 36] = address
        self.bytstr[36: 40] = length
        self.bytstr[40: 64] = self.val 
        self.bytstr[64:128] = descr.ljust(64)


    def sfdiag(self):
        """
        Metadata of a DIAG object
        """
        self.val[  :  4] = self.sfo.diag_code
        self.val[ 4:  6] = pack('>H', self.sfo.num_objs)
        self.val[ 6:  8] = pack('>H', self.sfo.diag_type)
        self.val[ 8: 12] = pack('>I', self.sfo.shot_nr)
        self.val[12: 16] = pack('>I', self.sfo.c_time)
        self.val[16: 18] = pack('>H', self.sfo.up_limit)
        self.val[18: 20] = pack('>H', self.sfo.exp)
        self.val[20: 22] = pack('>H', self.sfo.version)
        self.val[22: 24] = pack('>H', self.sfo.s_type)


    def list(self):
        """
        Metadata of a LIST object
        """

        self.val[ : 2] = pack('>H', self.sfo.data_format)
        self.val[2: 4] = pack('>H', self.sfo.nitems)
        self.val[4: 6] = pack('>H', self.sfo.ordering)
        self.val[6: 8] = pack('>H', self.sfo.list_type)


    def device(self):
        """
        Metadata of a DEVICE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.acquseq)
        self.val[ 4:  6] = pack('>H', self.sfo.nitems)
        self.val[ 6:  8] = pack('>H', self.sfo.dev_type)
        self.val[ 8: 12] = pack('>I', self.sfo.dev_addr)
        self.val[12: 16] = pack('>I', self.sfo.n_chan)
        self.val[16: 18] = pack('>H', self.sfo.task)
        self.val[18: 20] = pack('>H', self.sfo.dev_num)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def parmset(self):
        """
        Metadata of a ParameterSet object
        """

        self.val[4: 6] = pack('>H', self.sfo.nitems)
        self.val[6: 8] = pack('>H', self.sfo.cal_type)


    def mapping(self):
        """
        Metadata of a MAP object
        """

        self.val[ 4:  6] = pack('>H', self.sfo.nitems)
        self.val[ 6:  8] = pack('>H', self.sfo.map_type)
        self.val[16: 18] = pack('>H', self.sfo.task)


    def sig(self):
        """
        Metadata of a Signal or SignalGroup object
        """
        ind = list(self.sfo.index)[::-1]
        while len(ind) < 4:
            ind.append(1)
        self.sfo.index = ind[::-1]

        self.val[  :  2] = pack('>H' , self.sfo.data_format)
        self.val[ 2:  4] = pack('>H' , self.sfo.physunit)
        self.val[ 4:  6] = pack('>H' , self.sfo.num_dims)
        self.val[ 6:  8] = pack('>h' , self.sfo.stat_ext)
        self.val[ 8: 24] = pack('>4I', *self.sfo.index)


    def tbase(self):
        """
        Metadata of a TIMEBASE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.burstcount)
        self.val[ 4:  6] = pack('>H', self.sfo.event)
        self.val[ 6:  8] = pack('>H', self.sfo.tbase_type)
        self.val[ 8: 12] = pack('>I', self.sfo.s_rate)
        self.val[16: 20] = pack('>I', self.sfo.n_pre)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def sf_list(self):
        """
        Metadata of a SF_LIST object
        """

        self.val[2: 4] = pack('>H', self.sfo.nitems)


    def algorithm(self):
        """
        Metadata of an ALGORITHM object
        """

        self.val[ 8: 16] = self.sfo.hostname
        self.val[16: 24] = self.sfo.date


    def update_set(self):
        """
        Metadata of an UPDATE_SET object
        """

        self.val[ 2:  4] = pack('>H', self.sfo.nitems) 
        self.val[ 4:  8] = pack('>i', self.sfo.input_vals) 
        self.val[16: 20] = pack('>I', self.sfo.next_index) 
        self.val[20: 24] = pack('>I', self.sfo.size) 


    def loctimer(self):
        """
        Metadata of an LOCTIMER object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  4] = pack('>H', self.sfo.resolution)
        self.val[20: 24] = pack('>I', self.sfo.size)


    def abase(self):
        """
        Metadata of an AREABASE object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 2:  8] = pack('>3H', *self.sfo.physunit)
        self.val[ 8: 12] = pack('>I', self.sfo.size_x)
        self.val[12: 16] = pack('>I', self.sfo.size_y)
        self.val[16: 20] = pack('>I', self.sfo.size_z)
        self.val[20: 24] = pack('>I', self.sfo.n_steps)


    def qualifier(self):
        """
        Metadata of an QUALIFIER object
        """

        self.val[  :  2] = pack('>H', self.sfo.data_format)
        self.val[ 4:  6] = pack('>H', self.sfo.num_dims)
        self.val[ 6:  8] = pack('>H', self.sfo.qsub_typ)
        self.val[ 8: 12] = pack('>I', self.sfo.index_4)
        self.val[12: 16] = pack('>I', self.sfo.index_3)
        self.val[16: 20] = pack('>I', self.sfo.index_2)
        self.val[20: 24] = pack('>I', self.sfo.max_sections)


    def modobj(self):
        """
        Metadata of a MODOBJ object
        """

        self.val[ : 2] = pack('>H', self.sfo.nitems)


    def mapext(self):
        """
        Metadata of a MAPEXT object
        """

        self.val[  :  2] = pack('>H', self.sfo.nitems)
        self.val[ 2:  4] = pack('>H', self.sfo.mapalg)
        self.val[ 4:  8] = pack('>I', self.sfo.tbeg)
        self.val[ 8: 12] = pack('>I', self.sfo.tend)
        self.val[12: 14] = pack('>H', self.sfo.val_0)
        self.val[14: 16] = pack('>H', self.sfo.val_1)
        self.val[16: 20] = pack('>I', self.sfo.val_2)
        self.val[20: 24] = pack('>I', self.sfo.val_3)


    def resource(self):
        """
        Metadata of a RESOURCE object
        """

        self.val[  :  2] = pack('>H', self.sfo.num_cpus)
        self.val[ 2:  4] = pack('>H', self.sfo.first_cpu)


    def addrlen(self):
        """
        Value of ADDRLEN object
        """

        self.val[ : 2] = pack('>H', self.sfo.addrlen)
