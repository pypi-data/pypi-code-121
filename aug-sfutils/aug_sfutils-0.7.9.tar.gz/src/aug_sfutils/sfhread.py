import logging
from struct import unpack, pack
import numpy as np
from aug_sfutils import sfdics, str_byt

n_rel = 8

logger = logging.getLogger('aug_sfutils.sfhread')
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)


for key, val in sfdics.obj_name.items():
    exec('%s=%d' %(val, key))


def read_sfh(byt_str):
    """
    Reads a full shotfile header
    """

    sfhead = {}
    obj_names = []
    n_max = 1000
    n_obj = n_max
    for j in range(n_max):
        sfo = SFH_READ(byt_str[j*128: (j+1)*128])
        if not hasattr(sfo, 'obj_type'):
            continue
        sfo.objid = j
        onam = str_byt.to_str(sfo.objnam.strip())
        if sfo.obj_type == Diagnostic:
            if n_obj == n_max: # There might be several diags objects in a SFH
                n_obj = sfo.num_objs
        sfhead[onam] = sfo
        obj_names.append(onam)
        if j == n_obj - 1:
            break

    for sfo in sfhead.values():
        sfo.relations = [obj_names[jid] for jid in sfo.rel if jid != 65535]

    return sfhead


class SFH_READ:
    """
    Reads a generic object's metadata from the SFH's byte string
    """

    def __init__(self, byte_str):
        """
        Reads the SFH part of an object, common to all objects
        """
        self.objnam = str_byt.to_str(byte_str[0:8])

        if not self.objnam:
            logger.error('Error: empty object name')
            return

        self.obj_type, self.level, self.status = unpack('>3H', byte_str[ 8: 14])
        typ = self.obj_type
        if typ in sfdics.obj_name.keys():
            self.object_type = sfdics.obj_name[typ]
        else:
            self.object_type = 'Unknown'
        self.errcode  = unpack('>h', byte_str[14: 16])[0]
        fmt = '>%dH' %n_rel
        self.rel      = list(unpack(fmt,  byte_str[16        : 16+2*n_rel]))
        self.address, self.length = unpack('>2I', byte_str[16+2*n_rel: 24+2*n_rel])
        self.val      = byte_str[40:  64]
        logger.debug(self.objnam)
        self.descr    = str_byt.to_str(byte_str[64: 128].strip())
        logger.debug(self.descr)

        val_func = { \
            1 : self.sfdiag, 2: self.list, 3: self.device, 4: self.parmset, \
            5 : self.mapping, 6: self.sig, 7: self.sig, 8: self.tbase, \
            9 : self.sf_list, 10: self.algorithm, 11: self.update_set, \
            12: self.loctimer, 13: self.abase, 14: self.qualifier, \
            15: self.modobj, 16: self.mapext, 17: self.resource, \
            18: self.addrlen }

        if typ in val_func.keys():
            val_func[typ]()
        else:
            logger.error('Object type %d of object %s not supported', self.obj_type, self.objnam)


    def sfdiag(self):
        """
        Metadata of a DIAG object
        """
        self.diag_code = self.val[: 4]
        self.num_objs, self.diag_type  = unpack('>2H', self.val[4: 8])
        self.shot_nr , self.c_time     = unpack('>2I', self.val[8: 16])
        self.up_limit, self.exp, self.version, self.s_type = unpack('>4H', self.val[16: 24])


    def list(self):
        """
        Metadata of a LIST object
        """

        self.data_format, self.nitems, self.ordering, self.list_type = unpack('>4H', self.val[ : 8])


    def device(self):
        """
        Metadata of a DEVICE object
        """

        self.data_format, self.acquseq, self.nitems, self.dev_type = unpack('>4H', self.val[:8])
        self.dev_addr, self.n_chan  = unpack('>2I', self.val[ 8: 16])
        self.task    , self.dev_num = unpack('>2H', self.val[16: 20])
        self.n_steps                = unpack('>I' , self.val[20: 24])[0]  


    def parmset(self):
        """
        Metadata of a ParameterSet object
        """

        self.nitems, self.cal_type = unpack('>2H', self.val[4: 8])
        if self.cal_type in sfdics.cal_type.keys():
            self.calibration_type = sfdics.cal_type[self.cal_type]


    def mapping(self):
        """
        Metadata of a MAP object
        """

        self.nitems, self.map_type = unpack('>2H' , self.val[4: 8])
        self.task = unpack('>H' , self.val[16: 18])[0]


    def sig(self):
        """
        Metadata of a Signal or SignalGroup object
        """

        self.data_format, self.physunit, self.num_dims = unpack('>3H' , self.val[: 6])
        self.phys_unit = sfdics.unit_d[self.physunit]
        self.stat_ext = unpack('>h' , self.val[6: 8])[0]
        self.index    = list(unpack('>4I', self.val[8: 24]))


    def tbase(self):
        """
        Metadata of a TIMEBASE object
        """

        self.data_format, self.burstcount, self.event, self.tbase_type = unpack('>4H', self.val[: 8])
        self.s_rate = unpack('>I', self.val[ 8: 12])[0] #Hz
        self.n_pre, self.n_steps = unpack('>2I', self.val[16: 24])
        if self.tbase_type in sfdics.tbtype_d.keys():
            self.timebase_type = sfdics.tbtype_d[self.tbase_type]


    def sf_list(self):
        """
        Metadata of a SF_LIST object
        """

        self.nitems = unpack('>H', self.val[2: 4])


    def algorithm(self):
        """
        Metadata of an ALGORITHM object
        """

        self.hostname = self.val[ 8: 16]
        self.date     = self.val[16: 24] 


    def update_set(self):
        """
        Metadata of an UPDATE_SET object
        """

        self.nitems =  unpack('>H' , self.val[ 2: 4])[0]
        self.input_vals = unpack('>i' , self.val[ 4: 8])[0]
        self.next_index, self.size = unpack('>I' , self.val[ 16: 24])


    def loctimer(self):
        """
        Metadata of an LOCTIMER object
        """

        self.data_format, self.resolution = unpack('>2H', self.val[: 4])
        self.size = unpack('>I', self.val[20: 24])[0]


    def abase(self):
        """
        Metadata of an AREABASE object
        """

        self.data_format = unpack('>H' , self.val[ : 2])[0]
        self.physunit    = unpack('>3H', self.val[2: 8])
        self.phys_unit = [sfdics.unit_d[x] for x in self.physunit]
        self.size_x, self.size_y, self.size_z, self.n_steps = unpack('>4I' , self.val[8: 24])
        self.sizes = [self.size_x, self.size_y, self.size_z]


    def qualifier(self):
        """
        Metadata of a QUALIFIER object
        """

        self.data_format = unpack('>H' , self.val[ : 2])[0]
        self.num_dims, self.qsub_typ = unpack('>2H' , self.val[4: 8])
        self.index_4, self.index_3, self.index_2, self.max_sections = unpack('>4I' , self.val[8: 24])


    def modobj(self):
        """
        Metadata of a MODOBJ object
        """

        self.nitems = unpack('>H' , self.val[ : 2])[0]


    def mapext(self):
        """
        Metadata of a MAPEXT object
        """

        self.nitems, self.mapalg = unpack('>2H' , self.val[ : 4])
        self.tbeg  , self.tend   = unpack('>2I', self.val[4: 12])
        self.val_0 , self.val_1  = unpack('>2H', self.val[12: 16])
        self.val_2 , self.val_3  = unpack('>2I', self.val[16: 24])


    def resource(self):
        """
        Metadata of a RESOURCE object
        """

        self.num_cpus, self.first_cpu = unpack('>2H' , self.val[ : 4])


    def addrlen(self):
        """
        Value of ADDRLEN object
        """

        self.addrlen = unpack('>H' , self.val[ : 2])[0]
