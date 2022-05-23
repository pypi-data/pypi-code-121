import logging
import aug_sfutils as sf
from aug_sfutils import sfdics, sfhwrite

fmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s', '%H:%M:%S')
hnd = logging.StreamHandler()
hnd.setFormatter(fmt)
logger = logging.getLogger('sfhmod')
logger.addHandler(hnd)
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)


for key, val in sfdics.obj_name.items():
    exec('%s=%d' %(val, key))


class SFHMOD:


    def __init__(self, fin=None):

        self.sfo = sf.SFREAD(sfh=fin)


    def modtime(self, name, nt):
        '''Changes the size of the time dimension of a TB, AB, Sig or SigGroup (if related to a TB)'''

        sfobj = self.sfo.sfh[name]
        otyp = sfobj.obj_type
        if name not in self.sfo.objects:
            logger.error('modtim accepts only TB, AB, Sig, SigName')
        elif otyp in (TimeBase, AreaBase):
            sfobj.n_steps = nt
        elif otyp == Signal:
            sfobj.index[-1] = nt
        elif otyp == SignalGroup:
            tdim = None
            for jrel, rel in enumerate(sfobj.relations):
                if self.sfo.sfh[rel].obj_type == TimeBase:
                    tdim = jrel
                    break
            if tdim is not None:
                sfobj.index[3-tdim] = nt


    def modtimeall(self, tbase, nt):
        '''Changes the size of the time dimension of input TB plus all AB, Sig or SigGroup related to it'''

        sfobj = self.sfo.sfh[tbase]
        if sfobj.obj_type not in (TimeBase, Signal):
            logger.error('modtimall needs a TB or SIG name')
            return

        self.modtime(tbase, nt)

        for sfobj in self.sfo.sfh.values():
            onam = sfobj.objnam
            if onam in self.sfo.objects:
                for rel in sfobj.relations:
                    if rel == tbase:
                        self.modtime(onam, nt)


    def modindex(self, sgr, index):
        '''Changes the dims of a SigGroup'''

        index = list(index)
        sfobj = self.sfo.sfh[sgr]
        if sfobj.obj_type != SignalGroup:
            logger.error('modindex needs a SigGroup')
            return
        while len(index) < 4:
            index.append(1)
        sfobj.index = index[::-1]


    def modareasize(self, abase, size_x=None, size_y=None, size_z=None):
        '''Changes the sizes of an AreaBase'''

        sfobj = self.sfo.sfh[abase]
        if sfobj.obj_type != AreaBase:
            logger.error('modareasize needs an AreaBase')
            return

        if size_x is not None:
            sfobj.size_x = size_x
        if size_y is not None:
            sfobj.size_y = size_y
        if size_z is not None:
            sfobj.size_z = size_z


    def modareaall(self, abase, nx):
        '''Changes size_x of a space-1D AreaBase and the spatial dim of all related SigGroups'''
 
        sfobj = self.sfo.sfh[abase]
        if sfobj.obj_type != AreaBase:
            logger.error('modareaall needs an AreaBase')
            return
        if sfobj.size_y > 0:
            logger.error('modareaall works only with space-1d AreaBases')
            return

        sfobj.size_x = nx

        for sfobj in self.sfo.sfh.values():
            otyp = sfobj.obj_type
            if otyp == SignalGroup:
                adim = None
                for jrel, rel in enumerate(sfobj.relations):
                    if rel == abase:
                        adim = jrel
                        break
                if adim is not None:
                    sfobj.index[3-adim] = nx


    def modpar(self, pset, pnam, data):
        '''Modify data content (and length) of parameter pnaf of ParSet pset'''

        par = self.sfo.sfh[pset].pars[pnam]
        par.n_items = len(data)
        par[:par.n_items] = data[:]


    def write(self, fout='mytest.fsh'):

        sfhwrite.write_sfh(self.sfo, fout)


if __name__ == '__main__':

    fsfh = 'RAB00000.sfh'
    sfh = SFHMOD(fin=fsfh)
    sfh.modtimeall('time', 12)
    print('')
    sfh.modareaall('rho_in', 21)
    print('')
    sfh.write(fout='myrab.sfh')

    fsfh = 'TST00000.sfh'
    sfh = SFHMOD(fin=fsfh)    
    sfh.modpar('NBIpar', 'rtcena', [0.,1.,2.,3.] )
    print('')
    sfh.write(fout='mytra.sfh')
