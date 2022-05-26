import logging
import sys
from pathlib import Path
from typing import Union, List, Tuple, Dict

import inspect
from astropy.io import fits
from astropy.io.fits.hdu.base import _BaseHDU
from astropy.table import Table as AstropyTable
import numpy as np

from weaveio.config_tables import progtemp_config
from weaveio.file import File, PrimaryHDU, TableHDU, BinaryHDU
from weaveio.hierarchy import unwind, collect, Multiple, Hierarchy, OneOf, Optional
from weaveio.opr3.hierarchy import Survey, Subprogramme, SurveyCatalogue, \
    WeaveTarget, SurveyTarget, Fibre, FibreTarget, Progtemp, ArmConfig, Obstemp, \
    OBSpec, OB, Exposure, Run, CASU, RawSpectrum, _predicate, WavelengthHolder
from weaveio.opr3.l1 import L1SingleSpectrum, L1StackSpectrum, L1SuperstackSpectrum, L1SupertargetSpectrum, L1Spectrum, L1StackedSpectrum, NoSS
from weaveio.writequery import groupby, CypherData


class HeaderFibinfoFile(File):
    is_template = True

    @classmethod
    def length(cls, path, part=None):
        return len(cls.read_fibinfo_dataframe(path))

    @classmethod
    def read_fibinfo_dataframe(cls, path, slc=None):
        hdus = fits.open(path)
        fibinfo_hdu = hdus['FIBTABLE']
        fibinfo = AstropyTable(fibinfo_hdu.data).to_pandas()
        fibinfo.columns = [i.lower() for i in fibinfo.columns]
        if 'nspec' in fibinfo.columns:
            fibinfo['spec_index'] = fibinfo['nspec'] - 1
        slc = slice(None) if slc is None else slc
        return fibinfo.iloc[slc]

    @classmethod
    def read_surveyinfo(cls, df_fibinfo):
        df_svryinfo = df_fibinfo[['targsrvy', 'targprog', 'targcat']].drop_duplicates()
        df_svryinfo['progid'] = df_svryinfo['targsrvy'] + df_svryinfo['targprog']
        df_svryinfo['catid'] = df_svryinfo['progid'] + df_svryinfo['targcat']
        return df_svryinfo

    @classmethod
    def read_fibretargets(cls, df_svryinfo, df_fibinfo):
        srvyinfo = CypherData(df_svryinfo)
        fibinfo = CypherData(df_fibinfo)
        with unwind(srvyinfo) as svryrow:
            with unwind(svryrow['targsrvy']) as surveyname:
                survey = Survey(name=surveyname)
            surveys = collect(survey)
            prog = Subprogramme(name=svryrow['targprog'], id=svryrow['progid'], surveys=surveys)
            cat = SurveyCatalogue(name=svryrow['targcat'], id=svryrow['catid'], subprogramme=prog)
        cat_collection = collect(cat)
        cats = groupby(cat_collection, 'name')
        with unwind(fibinfo) as fibrow:
            fibre = Fibre(id=fibrow['fibreid'])  #  must be up here for some reason otherwise, there will be duplicates
            cat = cats[fibrow['targcat']]
            weavetarget = WeaveTarget(cname=fibrow['cname'])
            surveytarget = SurveyTarget(survey_catalogue=cat, weave_target=weavetarget, tables=fibrow)
            fibtarget = FibreTarget(survey_target=surveytarget, fibre=fibre, tables=fibrow)
        return collect(fibtarget, fibrow)

    @classmethod
    def read_distinct_survey_info(cls, df_svryinfo):
        rows = CypherData(df_svryinfo['targsrvy'].drop_duplicates().values, 'surveynames')
        with unwind(rows) as survey_name:
            survey = Survey(name=survey_name)
        survey_list = collect(survey)
        survey_dict = groupby(survey_list, 'name')

        # each row is (subprogramme, [survey_name, ...])
        s = df_svryinfo.groupby('progid')[['targsrvy', 'targprog']].aggregate(lambda x: x.values.tolist())
        rows = CypherData(s, 'targprog_rows')
        with unwind(rows) as row:
            with unwind(row['targsrvy']) as survey_name:
                survey = survey_dict[survey_name]
            surveys = collect(survey)
            subprogramme = Subprogramme(surveys=surveys, name=row['targprog'][0], id=row['progid'])
        subprogramme_list = collect(subprogramme)
        subprogramme_dict = groupby(subprogramme_list, 'id')

        # catalogue has 1 programme
        # programme can have many catalogues
        rows = CypherData(df_svryinfo[['targcat', 'progid', 'catid']].drop_duplicates(), 'targcat_rows')
        with unwind(rows) as row:
            catalogue = SurveyCatalogue(subprogramme=subprogramme_dict[row['progid']], name=row['targcat'], id=row['catid'])
        catalogue_list = collect(catalogue)
        return survey_list, subprogramme_list, catalogue_list

    @classmethod
    def read_hierarchy(cls, header, df_svryinfo, fibretarget_collection):
        surveys, subprogrammes, catalogues = cls.read_distinct_survey_info(df_svryinfo)
        runid = int(header['RUN'])
        camera = str(header['CAMERA'].lower()[len('WEAVE'):])
        obstart = np.round(float(header['OBSTART']), 6)
        res = str(header['VPH']).rstrip('123').lower().replace('res', '')
        obtitle = str(header['OBTITLE'])
        xml = str(header['CAT-NAME']).replace('./', '') if 'xml' in header['CAT-NAME'] else str(header['INFILE'])  # stack files do this
        obid = float(header['OBID'])
        casu = CASU(id=header['CASUID'])

        progtemp = Progtemp.from_progtemp_code(header['PROGTEMP'])
        vph = int(progtemp_config[(progtemp_config['mode'] == progtemp.instrument_configuration.mode)
                                  & (progtemp_config['resolution'] == res.lower().replace('res', ''))][f'{camera}_vph'].iloc[0])
        arm = ArmConfig(vph=vph, resolution=res, camera=camera)  # must instantiate even if not used
        obstemp = Obstemp.from_header(header)
        obspec = OBSpec(xml=xml, title=obtitle, obstemp=obstemp, progtemp=progtemp, fibre_targets=fibretarget_collection,
                        survey_catalogues=catalogues, subprogrammes=subprogrammes, surveys=surveys)
        ob = OB(id=obid, mjd=obstart, obspec=obspec)
        exposure = Exposure.from_header(ob, header)
        adjunct_run = Run.find(anonymous_parents=[exposure], exclude=[Run.find(id=runid)])
        run = Run(id=runid, arm_config=arm, exposure=exposure, adjunct=adjunct_run)
        return {'ob': ob, 'obspec': obspec, 'arm_config': arm, 'exposure': exposure, 'run': run, 'adjunct_run': adjunct_run, 'casu': casu}

    @classmethod
    def read_schema(cls, path: Path, slc: slice = None):
        header = cls.read_header(path)
        fibinfo = cls.read_fibinfo_dataframe(path, slc)
        srvyinfo = cls.read_surveyinfo(fibinfo)
        fibretarget_collection, fibrows = cls.read_fibretargets(srvyinfo, fibinfo)
        hiers = cls.read_hierarchy(header, srvyinfo, fibretarget_collection)
        return hiers, header, fibinfo, fibretarget_collection, fibrows

    @classmethod
    def read_header(cls, path: Path, i=0):
        return fits.open(path)[i].header

    @classmethod
    def read_fibtable(cls, path: Path):
        return AstropyTable(fits.open(path)[cls.fibinfo_i].data)

    @classmethod
    def read(cls, directory: Path, fname: Path, slc: slice = None, part=None) -> 'File':
        raise NotImplementedError


class RawFile(HeaderFibinfoFile):
    match_pattern = 'r[0-9]+\.fit'
    hdus = {'primary': PrimaryHDU, 'counts1': BinaryHDU, 'counts2': BinaryHDU,
            'fibtable': TableHDU, 'guidinfo': TableHDU, 'metinfo': TableHDU}
    parents = [CASU, RawSpectrum]
    produces = [CASU]  # extra things which are not necessarily children of this object, cannot include parents
    children = [Optional('self', idname='adjunct')]

    @classmethod
    def fname_from_runid(cls, runid):
        return f'r{runid:07.0f}.fit'

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None):
        path = Path(directory) / Path(fname)
        hiers, header, fibinfo, fibretarget_collection, fibrow_collection = cls.read_schema(path, slc)
        adjunct_run = hiers['adjunct_run']
        adjunct_raw = RawSpectrum.find(anonymous_parents=[adjunct_run])
        adjunct_rawfile = RawFile.find(anonymous_children=[adjunct_raw])
        raw = RawSpectrum(run=hiers['run'], casu=hiers['casu'], adjunct=adjunct_raw)
        hdus, file, _ = cls.read_hdus(directory, fname, raw_spectrum=raw, casu=hiers['casu'], adjunct=adjunct_rawfile)
        where = {'counts1': 1, 'counts2': 2}
        for product in raw.products:
            raw.attach_product(product, hdus[where[product]])
        return file


class L1File(HeaderFibinfoFile):
    singular_name = 'l1file'
    is_template = True
    hdus = {'primary': PrimaryHDU, 'flux': BinaryHDU, 'ivar': BinaryHDU,
            'flux_noss': BinaryHDU, 'ivar_noss': BinaryHDU,
            'sensfunc': BinaryHDU, 'fibtable': TableHDU}
    children = [Optional('self', idname='adjunct')]
    parents = [WavelengthHolder, Multiple(L1Spectrum), CASU]
    produces = [CASU, NoSS]  # extra things which are not necessarily children of this object, cannot include parents

    @classmethod
    def wavelengths(cls, rootdir: Path, fname: Union[Path, str]):
        hdulist = fits.open(rootdir / fname)
        header = hdulist[1].header
        increment, zeropoint, size = header['cd1_1'], header['crval1'], header['naxis1']
        return WavelengthHolder(wvl=(np.arange(0, size) * increment) + zeropoint,
                                cd1_1=header['cd1_1'], crval1=header['crval1'], naxis1=header['naxis1'])

    @classmethod
    def read_hdus(cls, directory: Union[Path, str], fname: Union[Path, str],
                  **hierarchies: Union[Hierarchy, List[Hierarchy]]) -> Tuple[Dict[int, 'HDU'], 'File', List[_BaseHDU]]:
        return super().read_hdus(directory, fname, **hierarchies, wavelength_holder=cls.wavelengths(directory, fname))

    @classmethod
    def attach_products_to_spectrum(cls, spectrum, index, hdus, names):
        for product in spectrum.products:
            spectrum.attach_product(product, hdus[names[product]], index=index)


class L1SingleFile(L1File):
    singular_name = 'l1single_file'
    match_pattern = 'single_\d+\.fit'
    parents = [CASU, OneOf(RawFile, one2one=True), Multiple(L1SingleSpectrum), WavelengthHolder]
    children = [Optional('self', idname='adjunct')]
    version_on = ['raw_file']

    @classmethod
    def fname_from_runid(cls, runid):
        return f'single_{runid:07.0f}.fit'

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None):
        fname = Path(fname)
        directory = Path(directory)
        absolute_path = directory / fname
        hiers, header, fibinfo, fibretarget_collection, fibrow_collection = cls.read_schema(absolute_path, slc)
        casu = hiers['casu']
        inferred_raw_fname = fname.with_name(fname.name.replace('single_', 'r'))
        matched_files = list(directory.rglob(inferred_raw_fname.name))
        if not matched_files:
            logging.warning(f"{fname} does not have a matching raw file. "
                            f"The database will create the link but the rawspectra will not be available until the missing file is.")
            inferred_raw_fname = inferred_raw_fname.name
        elif len(matched_files) > 1:
            raise FileExistsError(f"Whilst searching for {inferred_raw_fname}, we found more than one match:"
                                  f"\n{matched_files}")
        else:
            inferred_raw_fname = str(matched_files[0].name)
        adjunct_run = hiers['adjunct_run']
        adjunct_raw = RawSpectrum.find(anonymous_parents=[adjunct_run])
        adjunct_raw_file = RawFile.find(anonymous_parents=[adjunct_raw])
        adjunct_file = cls.find(anonymous_parents=[adjunct_raw_file])
        raw = RawSpectrum(run=hiers['run'], casu=casu)
        rawfile = RawFile(fname=inferred_raw_fname, casu=casu, raw_spectrum=raw, adjunct=adjunct_raw_file, path='<MISSING>')  # merge this one instead of finding, then we can start from single or raw files
        wavelengths = cls.wavelengths(directory, fname)
        with unwind(fibretarget_collection, fibrow_collection) as (fibretarget, fibrow):
            adjunct = L1SingleSpectrum.find(raw_spectrum=adjunct_raw, fibre_target=fibretarget)
            single_spectrum = L1SingleSpectrum(raw_spectrum=raw, fibre_target=fibretarget,
                                               wavelength_holder=wavelengths, arm_config=hiers['arm_config'],
                                               tables=fibrow, adjunct=adjunct)
            adjunct_noss = NoSS.find(anonymous_parents=[adjunct])
            noss = NoSS(l1_spectrum=single_spectrum, adjunct=adjunct_noss)
        single_spectra, nosses, fibrows = collect(single_spectrum, noss, fibrow)
        hdus, file, _ = cls.read_hdus(directory, fname, raw_file=rawfile, adjunct=adjunct_file,
                                      l1single_spectra=single_spectra,
                                      casu=casu)
        with unwind(single_spectra, nosses, fibrows) as (single_spectrum, noss, fibrow):
            spec = L1SingleSpectrum.from_cypher_variable(single_spectrum)
            noss = NoSS.from_cypher_variable(noss)
            cls.attach_products_to_spectrum(spec, fibrow['spec_index'], hdus, {'flux': 1, 'ivar': 2, 'sensfunc': 5})
            cls.attach_products_to_spectrum(noss, fibrow['spec_index'], hdus, {'flux': 3, 'ivar': 4, 'sensfunc': 5})
        single_spectra = collect(single_spectrum)  # must collect at the end
        return file


class L1StackedFile(L1File):
    singular_name = 'l1stacked_file'
    is_template = True
    SpectrumType = None

    @classmethod
    def parent_runids(cls, path):
        header = cls.read_header(path, 0)
        runids = [int(v) for k, v in header.items() if k.startswith('RUNS0')]
        if len(runids) == 0:
            runids = [int(v.split('.')[0].split('_')[1]) for k, v in header.items() if k.startswith('PROV0') and 'formed' not in v]
        return runids

    @classmethod
    def fname_from_runid(cls, runid):
        return f'stack_{runid:07.0f}.fit'

    @classmethod
    def get_single_files_fnames(cls, directory: Path, fname: Path):
        runids = cls.parent_runids(directory / fname)
        fnames = [L1SingleFile.fname_from_runid(runid) for runid in runids]
        assert len(fnames) > 1, f'{fname} doesnt have more than one l1single runid'
        return fnames

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None):
        """
        L1Stack inherits everything from the lowest numbered single/raw files so we are missing data,
        therefore we require that all the referenced Runs are present before loading in
        """
        fname = Path(fname)
        directory = Path(directory)
        hiers, header, fibinfo, fibretarget_collection, fibrow_collection = cls.read_schema(directory / fname, slc)
        ob = hiers['ob']
        armconfig = hiers['arm_config']
        # unwind all single files that went into making this stack
        single_fnames = cls.get_single_files_fnames(directory, fname)
        with unwind(CypherData(single_fnames)) as single_fname:
            single_file = L1SingleFile.find(fname=single_fname)
            adjunct_single_file = L1SingleFile.find(anonymous_parents=[single_file], exclude=[single_file])
        single_files, adjunct_single_files = collect(single_file, adjunct_single_file)
        adjunct_file = cls.find(anonymous_parents=[adjunct_single_files])  # bit of a hack but ok
        wavelengths = cls.wavelengths(directory, fname)
        with unwind(fibretarget_collection, fibrow_collection) as (fibretarget, fibrow):
            adjunct = L1StackedSpectrum.find(anonymous_parents=[fibretarget], anonymous_children=[adjunct_file])
            with unwind(single_files) as single_file:
                single_spectrum = L1SingleSpectrum.find(anonymous_parents=[fibretarget], anonymous_children=[single_file])
            single_spectra = collect(single_spectrum)
            # use the generic "L1stackspectrum" to avoid writing out again for superstacks
            stack_spectrum = cls.SpectrumType(l1single_spectra=[single_spectra[i] for i, _ in enumerate(single_fnames)], ob=ob,
                                              arm_config=armconfig, fibre_target=fibretarget,
                                              tables=fibrow,
                                              adjunct=adjunct, wavelength_holder=wavelengths)
            adjunct_noss = NoSS.find(anonymous_parents=[adjunct])
            noss = NoSS(l1_spectrum=stack_spectrum, adjunct=adjunct_noss)
        stack_spectra, nosses, fibrows = collect(stack_spectrum, noss, fibrow)
        d = {cls.SpectrumType.plural_name: stack_spectra}
        hdus, file, _ = cls.read_hdus(directory, fname, l1single_files=single_files,
                                      adjunct=adjunct_file, **d, **hiers)
        with unwind(stack_spectra, nosses, fibrows) as (stack_spectrum, noss, fibrow):
            spec = cls.SpectrumType.from_cypher_variable(stack_spectrum)
            noss = NoSS.from_cypher_variable(noss)
            cls.attach_products_to_spectrum(spec, fibrow['spec_index'], hdus, {'flux': 1, 'ivar': 2, 'sensfunc': 5})
            cls.attach_products_to_spectrum(noss, fibrow['spec_index'], hdus, {'flux': 3, 'ivar': 4, 'sensfunc': 5})
        stack_spectra = collect(stack_spectrum)  # must collect at the end
        return file


class L1StackFile(L1StackedFile):
    singular_name = 'l1stack_file'
    match_pattern = 'stack_[0-9]+\.fit'
    parents = [CASU, Multiple(L1SingleFile, constrain=(OB, ArmConfig)), Multiple(L1StackSpectrum), WavelengthHolder]
    children = [Optional('self', idname='adjunct')]
    SpectrumType =  L1StackSpectrum

    @classmethod
    def read_hdus(cls, directory: Union[Path, str], fname: Union[Path, str], **hierarchies: Union[Hierarchy, List[Hierarchy]]) -> Tuple[Dict[int, 'HDU'], 'File', List[_BaseHDU]]:
        return super().read_hdus(directory, fname, casu=hierarchies['casu'], l1single_files=hierarchies['l1single_files'],
                                 ob=hierarchies['ob'], arm_config=hierarchies['arm_config'],
                                 l1stack_spectra=hierarchies['l1stack_spectra'], adjunct=hierarchies['adjunct'])


class L1SuperstackFile(L1StackedFile):
    singular_name = 'l1superstack_file'
    match_pattern = 'superstack_[0-9]+\.fit'
    parents = [Multiple(L1SingleFile, constrain=(OBSpec, ArmConfig)), CASU, Multiple(L1SuperstackSpectrum), WavelengthHolder]
    children = [Optional('self', idname='adjunct')]
    SpectrumType = L1SuperstackSpectrum

    @classmethod
    def read_hdus(cls, directory: Union[Path, str], fname: Union[Path, str], **hierarchies: Union[Hierarchy, List[Hierarchy]]) -> Tuple[Dict[int, 'HDU'], 'File', List[_BaseHDU]]:
        return super().read_hdus(directory, fname, casu=hierarchies['casu'], l1single_files=hierarchies['l1single_files'],
                                 obspec=hierarchies['obspec'], arm_config=hierarchies['arm_config'],
                                 l1stack_spectra=hierarchies['l1superstack_spectra'], adjunct=hierarchies['adjunct'])

    @classmethod
    def fname_from_runid(cls, runid):
        return f'superstack_{runid:07.0f}.fit'


class L1SupertargetFile(L1StackedFile):
    singular_name = 'l1supertarget_file'
    match_pattern = 'WVE_.+\.fit'
    parents = [Multiple(L1SingleFile, constrain=(WeaveTarget, ArmConfig)), CASU, L1SupertargetSpectrum, WavelengthHolder]
    children = [Optional('self', idname='adjunct')]
    SpectrumType = L1SupertargetSpectrum
    recommended_batchsize = None

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None):
        raise NotImplementedError


hierarchies = [i[-1] for i in inspect.getmembers(sys.modules[__name__], _predicate)]