import sys
from collections import namedtuple, defaultdict
from pathlib import Path
from typing import Union, List, Dict, Type, Set, Tuple, Optional

import inspect

import numpy as np
from astropy.io import fits
from astropy.io.fits.hdu.base import _BaseHDU
from astropy.table import Table, Column

from weaveio.file import File, PrimaryHDU, TableHDU
from weaveio.graph import Graph
from weaveio.hierarchy import Multiple, unwind, collect, Hierarchy, find_branch
from weaveio.opr3.hierarchy import APS, OB, OBSpec, Exposure, WeaveTarget, _predicate, Run, ArmConfig, FibreTarget, Fibre
from weaveio.opr3.l1 import L1Spectrum, L1SingleSpectrum, L1StackSpectrum, L1SupertargetSpectrum
from weaveio.opr3.l2 import L2, L2Single, L2Stack, L2Superstack, L2Supertarget, IngestedSpectrum, Fit, ModelSpectrum, Redrock, \
    RVSpecfit, Ferre, PPXF, Gandalf, GandalfModelSpectrum, CombinedIngestedSpectrum, CombinedModelSpectrum, Template, RedshiftArray, IvarIngestedSpectrum, IvarCombinedIngestedSpectrum, MaskedCombinedIngestedSpectrum, GandalfEmissionModelSpectrum, GandalfCleanModelSpectrum, \
    GandalfCleanIngestedSpectrum, L2Product, gandalf_line_names, gandalf_index_names
from weaveio.opr3.l1files import L1File, L1SuperstackFile, L1StackFile, L1SingleFile, L1SupertargetFile
from weaveio.writequery import CypherData, CypherVariable
from weaveio.writequery.actions import string_append
from weaveio.writequery.base import CypherAppendStr


MAX_REDSHIFT_GRID_LENGTH = 5000

class MissingDataError(Exception):
    pass


def column_name_acronym_replacements(columns:List[str], *acronyms: str) -> Dict[str, str]:
    replacements = {}
    for column in columns:
        for a in acronyms:
            for aa in [f'_{a}', f'_{a}_', f'{a}_']:
                if aa in column:
                    replacements[column.replace(aa.lower(), '')] = column
    return replacements


def filter_products_from_table(table: Table, maxlength: int) -> Table:
    columns = []
    for i in table.colnames:
        value = table[i]
        if len(value.shape) == 2:
            if value.shape[1] > maxlength:
                continue
        columns.append(i)
    t = table[columns]
    for col in table.colnames:
        t.rename_column(col, col.lower())
    return t


def extract_lines_names(expected_line_names, colnames):
    """
    returns dictionary of required factor names and values that can be take from the hdu
    """
    actual_line_names = sorted([i[len('FLUX') + 1:] for i in colnames if i.startswith('FLUX')], key=lambda x: float(x.split('_')[1]))
    d = {}
    for name in actual_line_names:
        if name in expected_line_names:
            name = name.lower()
            d[f"{name}_aon"] = f'aon_{name}'
            d[f"{name}_ebmv"] = f'ebv_{name}'
            d[f"{name}_flux"] = f'flux_{name}'
            d[f"{name}_flux_error"] = f'err_flux_{name}'
            d[f"{name}_amp_error"] = f'err_ampl_{name}'
            d[f"{name}_redshift"] = f'z_{name}'
            d[f"{name}_redshift_error"] = f'err_z_{name}'
            d[f"{name}_sigma"] = f'sigma_{name}'
            d[f"{name}_sigma_error"] = f'err_sigma_{name}'
    return d


def extract_indices_names(expected_index_names, colnames):
    d = {}
    for name in expected_index_names:
        if name in colnames:
            name = name.lower()
            d[f'{name}'] = name
            d[f'{name}_error'] = f'err_{name}'
    return d

FitSpecs = namedtuple('FitSpecs', ['individuals', 'individual_models', 'combined', 'combined_model', 'colour_codes', 'nrow'])
GandalfSpecs = namedtuple('GandalfSpecs', ['model', 'ingested', 'emission', 'clean_model', 'clean_ingested', 'nrow'])


class L2File(File):
    singular_name = 'l2file'
    is_template = True
    match_pattern = '.*APS.fits'
    antimatch_pattern = '.*cube.*'
    L2 = L2Product
    L1 = L1Spectrum
    parents = [Multiple(L1File, 2, 3), APS, Multiple(L2)]
    children = []
    parts = ['RR', 'RVS', 'FR', 'GAND', 'PPXF']
    hdus = {
        'primary': PrimaryHDU,
        'class_table': TableHDU,
        'stellar_table': TableHDU,
        'galaxy_table': TableHDU,
        'class_spectra': TableHDU,
        'stellar_spectra': TableHDU,
        'galaxy_spectra': TableHDU,
            }

    @classmethod
    def length(cls, path, part=None):
        hdus = fits.open(path)
        if part is None:
            return len(hdus[1].data)
        d = {'RR': 1, 'RVS': 2, 'FR':2, 'GAND': 3, 'PPXF': 3}
        return len(hdus[d[part]].data)

    @classmethod
    def make_l2(cls, spectra, aps, nspec, **hiers):
        return cls.L2(**{cls.L1.plural_name: [spectra[i] for i in range(nspec)], 'aps': aps}, **hiers)

    @classmethod
    def decide_filetype(cls, l1filetypes: List[Type[File]]) -> Type[File]:
        l1precedence = [L1SingleFile, L1StackFile, L1SuperstackFile, L1SupertargetFile]
        l2precedence = [L2SingleFile, L2StackFile, L2SuperstackFile, L2SupertargetFile]
        highest = max(l1precedence.index(l1filetype) for l1filetype in l1filetypes)
        return l2precedence[highest]

    @classmethod
    def match_file(cls, directory: Union[Path, str], fname: Union[Path, str], graph: Graph):
        """
        L2 files can be formed from any combination of L1 files and so the shared hierarchy level can be
        either exposure, OB, OBSpec, or WeaveTarget.
        L2 files are distinguished by the shared hierarchy level of their formative L1 files.
        Therefore, we assign an L2 file to the highest hierarchy level.
        e.g.
        L1Single+L1Single -> L2Single
        L1Stack+L1Single -> L2Stack
        L1SuperStack+L1Stack -> L2SuperStack
        """
        fname = Path(fname)
        directory = Path(directory)
        path = directory / fname
        if not super().match_file(directory, fname, graph):
            return False
        header = cls.read_header_and_aps(path)[0]
        ftypes, _ = zip(*cls.parse_fname(header, fname, instantiate=False))
        return cls.decide_filetype(ftypes) is cls

    @classmethod
    def parser_ftypes_runids(cls, header):
        header_info = [header.get(f'L1_REF_{i}', '.').split('.')[0].split('_') for i in range(4)]
        ftypes_header, runids_header = zip(*[i for i in header_info if len(i) > 1])
        return ftypes_header, list(map(int, runids_header))

    @classmethod
    def parse_fname(cls, header, fname, instantiate=True) -> List[L1File]:
        """
        Return the L1File type and the expected filename that formed this l2 file
        """
        ftype_dict = {
            'single': L1SingleFile,
            'stacked': L1StackFile, 'stack': L1StackFile,
            'superstack': L1SuperstackFile, 'superstacked': L1SuperstackFile
        }
        split = fname.name.lower().replace('aps.fits', '').replace('aps.fit', '').strip('_.').split('__')
        runids = []
        ftypes = []
        for i in split:
            ftype, runid = i.split('_')
            runids.append(int(runid))
            ftypes.append(str(ftype))
        if len(ftypes) == 1:
            ftypes = [ftypes[0]] * len(runids)  # they all have the same type if there is only one mentioned
        assert len(ftypes) == len(runids), "error parsing runids/types from fname"
        ftypes_header, runids_header = cls.parser_ftypes_runids(header)
        if not all(map(lambda x: x[0] == x[1], zip(runids, runids_header))):
            raise ValueError(f"There is a mismatch between runids in the filename and in in the header")
        if not all(map(lambda x: x[0] == x[1], zip(ftypes, ftypes_header))):
            raise ValueError(f"There is a mismatch between stack/single filetype in the filename and in in the header")
        files = []
        for ftype, runid in zip(ftypes, runids):
            ftype_cls = ftype_dict[ftype]
            fname = ftype_cls.fname_from_runid(runid)
            if instantiate:
                files.append(ftype_cls.find(fname=fname))
            else:
                files.append((ftype_cls, fname))
        return files

    @classmethod
    def find_shared_hierarchy(cls, path: Path) -> Dict:
        raise NotImplementedError

    @classmethod
    def read_header_and_aps(cls, path):
        return fits.open(path)[0].header, fits.open(path)[1].header['APS_V'].strip()

    @classmethod
    def read_hdus(cls, directory: Union[Path, str], fname: Union[Path, str], l1files: List[L1File],
                  **hierarchies: Union[Hierarchy, List[Hierarchy]]) -> Tuple[Dict[int, 'HDU'], 'File', List[_BaseHDU]]:
        fdict = {p.plural_name: [] for p in cls.parents if isinstance(p, Multiple) and issubclass(p.node, L1File)} # parse the 1lfile types separately
        for f in l1files:
            fdict[f.plural_name].append(f)
        hierarchies.update(fdict)
        hierarchies[cls.L2.plural_name] = hierarchies['l2']
        del hierarchies['l2']
        return super().read_hdus(directory, fname, **hierarchies)

    @classmethod
    def get_l1_filenames(cls, header):
        return [v for k, v in header.items() if 'APS_REF' in k]

    @classmethod
    def get_all_fibreids(cls, path):
        aps_ids = set()
        for hdu in fits.open(path)[1:]:
            try:
                aps_ids |= set(hdu.data['APS_ID'].tolist())
            except KeyError:
                pass
        return sorted(aps_ids)

    @classmethod
    def attach_products_to_spectra(cls, specs: FitSpecs, formatter, hdu, names: Dict[str, str], types, combined_suffix='_C'):
        IngestedSpectrum, CombinedIngestedSpectrum, ModelSpectrum, CombinedModelSpectrum = types
        # this is less complicated than it looks
        # `specs` is a namedtuple containing ingested and model spectra collections ([fibre1_spectrum, fibre2_spectrum, ...])
        # in the case of `individual_models` and `individuals`, they are a collection of collections:
        #    [[fibre1_red_spectrum, fibre2_red_spectrum], [fibre1_blue_spectrum, fibre2_blue_spectrum], ...]
        # so we unwind those ones twice
        if specs.individual_models is not None:
            with unwind(specs.individual_models, specs.colour_codes, specs.nrow) as (spectra, colour_codes, nrow):
                with unwind(spectra, colour_codes) as (spectrum, colour_code):
                    column_name = string_append(f'MODEL_{formatter}_'.upper(), colour_code)
                    spectrum = ModelSpectrum.from_cypher_variable(spectrum)
                    spectrum.attach_product('flux', hdu, column_name=column_name, index=nrow)
                collect(spectrum)  # collect to avoid duplication of effort later
            collect(nrow)  # collect to avoid duplication of effort later
        if specs.individuals is not None:
            with unwind(specs.individuals, specs.colour_codes, specs.nrow) as (spectra, colour_codes, nrow):
                with unwind(spectra, colour_codes) as (spectrum, colour_code):
                    spectrum = IngestedSpectrum.from_cypher_variable(spectrum)
                    for product in spectrum.products:
                        column_name = string_append(f'{names.get(product, product)}_{formatter}_'.upper(), colour_code)
                        spectrum.attach_product(product, hdu, column_name=column_name, index=nrow)
                collect(spectrum)  # collect to avoid duplication of effort later
            collect(nrow)  # collect to avoid duplication of effort later
        if specs.combined_model is not None:
            with unwind(specs.combined_model, specs.nrow) as (combined_model, nrow):
                spectrum = CombinedModelSpectrum.from_cypher_variable(combined_model)
                column_name = f'model_{formatter}{combined_suffix}'.upper()
                spectrum.attach_product('flux', hdu, column_name=column_name, index=nrow)
            collect(spectrum)  # collect to avoid duplication of effort later
        if specs.combined is not None:
            with unwind(specs.combined, specs.nrow) as (combined, nrow):
                spectrum = CombinedIngestedSpectrum.from_cypher_variable(combined)
                for product in spectrum.products:
                    column_name = f'{names.get(product, product)}_{formatter}{combined_suffix}'.upper()
                    spectrum.attach_product(product, hdu, column_name=column_name, index=nrow)
            collect(spectrum)  # collect to avoid duplication of effort later

    @classmethod
    def attach_products_to_gandalf_extra_spectra(cls, specs: GandalfSpecs, hdu):
        with unwind(specs.emission, specs.clean_model, specs.clean_ingested, specs.nrow) as (emission, clean_model, clean_ingested, nrow):
            emission = GandalfEmissionModelSpectrum.from_cypher_variable(emission)
            clean_model = GandalfCleanModelSpectrum.from_cypher_variable(clean_model)
            clean_ingested = GandalfCleanIngestedSpectrum.from_cypher_variable(clean_ingested)
            emission.attach_product('flux', hdu, column_name=f'EMISSION_GAND', index=nrow)
            clean_model.attach_product('flux', hdu, column_name=f'MODEL_CLEAN_GAND', index=nrow)
            clean_ingested.attach_product('flux', hdu, column_name=f'FLUX_CLEAN_GAND', index=nrow)
        collect(nrow)  # collect to avoid duplication of effort later

    @classmethod
    def make_redrock_fit(cls, specs, zs, row, nl1specs, replacements):
        templates = {}
        unrolled = [specs.individual_models[i] for i in range(nl1specs)]
        for template_name in Redrock.template_names:
            chi2s = row[f'CZZ_CHI2_{template_name}'.lower()]
            template = Template(model_spectra=unrolled, combined_model_spectrum=specs.combined_model,
                                redshift_array=zs[template_name], name=template_name, chi2_array=chi2s)
            templates[template_name] = template
        return Redrock(model_spectra=unrolled, combined_model_spectrum=specs.combined_model, tables=row, tables_replace=replacements, **templates)

    @classmethod
    def make_gandalf_structure(cls, specs, row, this_fname, nrow, replacements):
        model, ingested = specs.combined_model, specs.combined
        emission = GandalfEmissionModelSpectrum(gandalf_model_spectrum=model)
        clean_model = GandalfCleanModelSpectrum(gandalf_model_spectrum=model)
        clean_ingested = GandalfCleanIngestedSpectrum(combined_ingested_spectrum=ingested)
        gandalf = Gandalf(gandalf_model_spectrum=specs.combined_model, tables=row, tables_replace=replacements)
        return gandalf, GandalfSpecs(model=model, ingested=ingested, emission=emission, clean_model=clean_model,
                                     clean_ingested=clean_ingested, nrow=specs.nrow)

    @classmethod
    def read_l2product_table(cls, this_fname, spectrum_hdu, row: CypherVariable, nrow,
                             parent_l1filenames,
                             IngestedSpectrumClass: Optional[Type[IngestedSpectrum]],
                             CombinedIngestedSpectrumClass: Optional[Type[CombinedIngestedSpectrum]],
                             ModelSpectrumClass: Optional[Type[ModelSpectrum]],
                             CombinedModelSpectrumClass: Optional[Type[CombinedModelSpectrum]],
                             uses_disjoint_spectra: bool,
                             uses_combined_spectrum: Optional[bool],
                             formatter: str,
                             aps):
        # if the joint spectrum is not available, we dont read it, obvs
        if uses_combined_spectrum is None:
            uses_combined_spectrum = any('_C' in i for i in spectrum_hdu.data.names)
        fibre = Fibre.find(id=row['aps_id'])
        with unwind(CypherData(parent_l1filenames)) as l1_fname:  # for each parent l1 file
            l1file = L1File.find(fname=l1_fname)
            _, fibretarget, l1spectrum, _ = find_branch(fibre, FibreTarget, L1Spectrum, l1file)  # get the fibre target and l1 spectrum for this fibre and file
            colour_code = ArmConfig.find(anonymous_children=[l1spectrum])['colour_code']
            if uses_disjoint_spectra:
                individual = IngestedSpectrumClass(l1_spectrum=l1spectrum, aps=aps)
                individual_model = ModelSpectrumClass(ingested_spectrum=individual)
        # now collect spec and models relative to the fibretarget
        if uses_disjoint_spectra:
            l1files, l1spectra, fibretargets, colour_codes, individuals, individual_models = collect(l1file, l1spectrum, fibretarget,
                                                                                    colour_code, individual, individual_model)
        else:
            l1files, l1spectra, fibretargets, colour_codes = collect(l1file, l1spectrum, fibretarget,  colour_code)
            individuals, individual_models = None, None
        if uses_combined_spectrum:
            combined = CombinedIngestedSpectrumClass(l1_spectra=[l1spectra[i] for i in range(len(parent_l1filenames))], aps=aps)
            combined_model = CombinedModelSpectrumClass(combined_ingested_spectrum=combined)
        else:
            combined, combined_model = None, None
        return FitSpecs(individuals, individual_models, combined, combined_model, colour_codes, nrow), l1spectra, fibretargets

    @classmethod
    def read_redrock(cls, this_fname, spectrum_hdu, colnames, safe_table: CypherVariable, parent_l1filenames, aps, zs, **hiers):
        if len(spectrum_hdu.data) == 0:
            return
        replacements = column_name_acronym_replacements(colnames, 'rr')
        with unwind(safe_table, enumerated=True) as (row, nrow):
            specs, l1spectra, fibretargets = cls.read_l2product_table(this_fname, spectrum_hdu, row, nrow,
                                                          parent_l1filenames, IvarIngestedSpectrum,
                                                          IvarCombinedIngestedSpectrum,
                                                          ModelSpectrum, CombinedModelSpectrum,
                                                          True, None, 'RR', aps)
            redrock = cls.make_redrock_fit(specs, zs, row, len(parent_l1filenames), replacements)
            l2 = cls.make_l2(l1spectra, nspec=len(parent_l1filenames), aps=aps, fibre_target=fibretargets[0], **hiers)
            l2.attach_optionals(redrock=redrock)
        l2, redrocks, *r = collect(l2, redrock, *specs)
        return l2, redrocks, FitSpecs(*r), IvarIngestedSpectrum, IvarCombinedIngestedSpectrum, ModelSpectrum, CombinedModelSpectrum

    @classmethod
    def read_rvspecfit(cls, this_fname, spectrum_hdu, colnames, safe_table: CypherVariable, parent_l1filenames, aps, **hiers):
        if len(spectrum_hdu.data) == 0:
            return
        replacements = column_name_acronym_replacements(colnames, 'rvs')
        with unwind(safe_table, enumerated=True) as (row, nrow):
            rvs_specs, l1spectra, fibretargets = cls.read_l2product_table(this_fname, spectrum_hdu, row, nrow,
                                                      parent_l1filenames, IngestedSpectrum,
                                                      CombinedIngestedSpectrum,
                                                      ModelSpectrum, CombinedModelSpectrum,
                                                      True, None, 'RVS', aps)
            rvspecfit = RVSpecfit(model_spectra=[rvs_specs.individual_models[i] for i in range(len(parent_l1filenames))],
                                  combined_model_spectrum=rvs_specs.combined_model, tables=row, tables_replace=replacements)
            l2 = cls.make_l2(l1spectra, nspec=len(parent_l1filenames), aps=aps, fibre_target=fibretargets[0], **hiers)
            l2.attach_optionals(rvspecfit=rvspecfit)
        l2, rvspecfits, *r = collect(l2, rvspecfit, *rvs_specs)
        return l2, rvspecfits, FitSpecs(*r), IngestedSpectrum, CombinedIngestedSpectrum, ModelSpectrum, CombinedModelSpectrum

    @classmethod
    def read_ferre(cls, this_fname, spectrum_hdu, colnames, safe_table: CypherVariable, parent_l1filenames, aps, **hiers):
        if len(spectrum_hdu.data) == 0:
            return
        replacements = column_name_acronym_replacements(colnames, 'fr')
        with unwind(safe_table, enumerated=True) as (row, nrow):
            ferre_specs, l1spectra, fibretargets = cls.read_l2product_table(this_fname, spectrum_hdu, row, nrow,
                                                        parent_l1filenames, IngestedSpectrum,
                                                        CombinedIngestedSpectrum,
                                                        ModelSpectrum, CombinedModelSpectrum,
                                                        True, None, 'FR', aps)
            ferre = Ferre(model_spectra=[ferre_specs.individual_models[i] for i in range(len(parent_l1filenames))],
                          combined_model_spectrum=ferre_specs.combined_model, tables=row, tables_replace=replacements)
            l2 = cls.make_l2(l1spectra, nspec=len(parent_l1filenames), aps=aps, fibre_target=fibretargets[0], **hiers)
            l2.attach_optionals(ferre=ferre)
        l2, ferres, *r = collect(l2, ferre, *ferre_specs)
        return l2, ferres, FitSpecs(*r), IngestedSpectrum, CombinedIngestedSpectrum, ModelSpectrum, CombinedModelSpectrum

    @classmethod
    def read_ppxf(cls, this_fname, spectrum_hdu, colnames, safe_table: CypherVariable, parent_l1filenames, aps, **hiers):
        if len(spectrum_hdu.data) == 0:
            return
        replacements = column_name_acronym_replacements(colnames, 'ppxf')
        with unwind(safe_table, enumerated=True) as (row, nrow):
            ppxf_specs, l1spectra, fibretargets = cls.read_l2product_table(this_fname, spectrum_hdu, row, nrow,
                                                         parent_l1filenames, None,
                                                         MaskedCombinedIngestedSpectrum,
                                                         None, CombinedModelSpectrum,
                                                         False, True, 'PPXF', aps)
            ppxf = PPXF(combined_model_spectrum=ppxf_specs.combined_model, tables=row, tables_replace=replacements)
            l2 = cls.make_l2(l1spectra, nspec=len(parent_l1filenames), aps=aps, fibre_target=fibretargets[0], **hiers)
            l2.attach_optionals(ppxf=ppxf)
        l2, ppxfs, *r = collect(l2, ppxf, *ppxf_specs)
        return l2, ppxfs, FitSpecs(*r), None, MaskedCombinedIngestedSpectrum, None, CombinedModelSpectrum

    @classmethod
    def read_gandalf(cls, this_fname, spectrum_hdu, colnames, safe_table: CypherVariable, parent_l1filenames, aps, **hiers):
        if len(spectrum_hdu.data) == 0:
            return
        replacements = column_name_acronym_replacements(colnames, 'gand')
        replacements.update(extract_lines_names(gandalf_line_names, colnames))
        replacements.update(extract_indices_names(gandalf_index_names, colnames))
        with unwind(safe_table, enumerated=True) as (row, nrow):
            gandalf_specs, l1spectra, fibretargets = cls.read_l2product_table(this_fname, spectrum_hdu, row, nrow,
                                                                              parent_l1filenames, None,
                                                                              MaskedCombinedIngestedSpectrum,
                                                                              None, GandalfModelSpectrum,
                                                                              False, True, 'GAND', aps)
            gandalf, gandalf_extra_specs = cls.make_gandalf_structure(gandalf_specs, row, this_fname, nrow, replacements)
            l2 = cls.make_l2(l1spectra, nspec=len(parent_l1filenames), aps=aps, fibre_target=fibretargets[0], **hiers)
            l2.attach_optionals(gandalf=gandalf)
        l2, gandalfs, *r = collect(l2, gandalf, *gandalf_specs, *gandalf_extra_specs)
        return l2, gandalfs, FitSpecs(*r[:len(gandalf_specs)]), GandalfSpecs(*r[len(gandalf_specs):]), None, MaskedCombinedIngestedSpectrum, None, GandalfModelSpectrum

    @classmethod
    def make_redshift_arrays(cls, tbl: Table):
        templates = {col[4:] for col in tbl.colnames if 'czz_' in col and 'chi2' not in col}
        row = tbl[0]
        d = {}
        for template_name in templates:
            zs = row[f'czz_{template_name}']
            array = RedshiftArray(value=CypherData(zs), start=zs[0], end=zs[1], step=zs[1] - zs[0])
            d[template_name] = array
        return d

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None):
        if part is None:
            raise RuntimeError(f"{cls.__name__}.read() requires a part argument otherwise py2neo will crash")
        if part not in cls.parts:
            raise ValueError(f"Unrecognised part {part}. Only {cls.parts} are allowed")
        fname = Path(fname)
        directory = Path(directory)
        path = directory / fname
        header, aps = cls.read_header_and_aps(path)
        l1files = cls.parse_fname(header, fname)
        aps = APS(version=aps)
        hierarchies = cls.find_shared_hierarchy(path)
        astropy_hdus = fits.open(path)
        fnames = [l1.fname for l1 in l1files]
        assert len(fnames) > 1, f"{fname} has only one L1 file"
        safe_tables = {}
        safe_cypher_tables = {}
        for i, hdu in enumerate(astropy_hdus[1:4], 1):
            safe_tables[i] = filter_products_from_table(Table(hdu.data)[slc], MAX_REDSHIFT_GRID_LENGTH)
            cols = [col for col in safe_tables[i].colnames if not ('chi2' not in col and 'czz_' in col)]
            safe_cypher_tables[i] =  CypherData(safe_tables[i][cols])
        if part == 'RVS':
            l2, specfits, specs, *types = cls.read_rvspecfit(path, astropy_hdus[5], astropy_hdus[2].data.names,
                                                 safe_cypher_tables[2], fnames, aps, **hierarchies)
            hdu_node = 5
        elif part == 'FR':
            l2, specfits, specs, *types = cls.read_ferre(path, astropy_hdus[5], astropy_hdus[2].data.names,
                                             safe_cypher_tables[2], fnames, aps, **hierarchies)
            hdu_node = 5
        elif part == 'PPXF':
            l2, specfits, specs, *types = cls.read_ppxf(path, astropy_hdus[6], astropy_hdus[3].data.names,
                                            safe_cypher_tables[3], fnames, aps, **hierarchies)
            hdu_node = 6
        elif part == 'RR':
            zs = cls.make_redshift_arrays(safe_tables[1])
            l2, specfits, specs, *types = cls.read_redrock(path, astropy_hdus[4], astropy_hdus[1].data.names,
                                               safe_cypher_tables[1], fnames, aps, zs, **hierarchies)
            hdu_node = 4
        elif part == 'GAND':
            l2, specfits, specs, extra_specs, *types = cls.read_gandalf(path, astropy_hdus[6], astropy_hdus[3].data.names,
                             safe_cypher_tables[3], fnames, aps, **hierarchies)
            hdu_node = 6
        else:
            raise ValueError(f"{part} is not a valid part")
        hdu_nodes, file, _ = cls.read_hdus(directory, fname, l2=l2, l1files=l1files, aps=aps, **hierarchies)
        hdu = hdu_nodes[hdu_node]
        names = {'logwvl': 'loglam', 'wvl': 'lambda'}
        if specs is not None:
            suffix = '' if part in ['PPXF', 'GAND'] else '_C'
            cls.attach_products_to_spectra(specs, part, hdu, names, types, suffix)
        if part == 'GAND':
            cls.attach_products_to_gandalf_extra_spectra(extra_specs, hdu)


class L2SingleFile(L2File):
    singular_name = 'l2single_file'
    children = []
    parents = [Multiple(L1SingleFile, 2, 3, constrain=(Exposure,)), APS, Multiple(L2Single)]
    L2 = L2Single
    L1 = L1SingleSpectrum


    @classmethod
    def find_shared_hierarchy(cls, path) -> Dict:
        header = cls.read_header_and_aps(path)[0]
        runids = cls.parser_ftypes_runids(header)[1]
        run = Run.find(id=runids[0])
        return {'exposure': Exposure.find(anonymous_children=[run])}


class L2StackFile(L2File):
    singular_name = 'l2stack_file'
    children = []
    parents = [Multiple(L1StackFile, 1, 3, constrain=(OB,)), APS, Multiple(L2Stack)]
    L2 = L2Stack
    L1 = L1StackSpectrum

    @classmethod
    def find_shared_hierarchy(cls, path) -> Dict:
        header = cls.read_header_and_aps(path)[0]
        return {'ob': OB.find(id=int(header['OBID']))}


class L2SuperstackFile(L2File):
    singular_name = 'l2superstack_file'
    children = []
    parents = [Multiple(L1SingleFile, 0, 3, constrain=(OBSpec,)),
               Multiple(L1StackFile, 0, 3, constrain=(OBSpec,)),
               Multiple(L1SuperstackFile, 0, 3, constrain=(OBSpec,)),
               APS, Multiple(L2Superstack)]
    L2 = L2Superstack
    L1 = L1Spectrum

    @classmethod
    def find_shared_hierarchy(cls, path) -> Dict:
        header = cls.read_header_and_aps(path)[0]
        return {'obspec': OBSpec.find(xml=str(header['cat-name']))}


class L2SupertargetFile(L2File):
    singular_name = 'l2supertarget_file'
    match_pattern = 'WVE_*aps.fits'
    children = []
    parents = [Multiple(L1SupertargetFile, 2, 3, constrain=(WeaveTarget,)), APS, L2Supertarget]
    L2 = L2Supertarget
    L1 = L1SupertargetSpectrum

    @classmethod
    def parse_fname(cls, header, fname, instantiate=True) -> List[L1File]:
        raise NotImplementedError

    @classmethod
    def find_shared_hierarchy(cls, path: Path) -> Dict:
        hdus = fits.open(path)
        names = [i.name for i in hdus]
        cname = hdus[names.index('CLASS_TABLE')].data['CNAME'][0]
        return {'weavetarget': WeaveTarget.find(cname=cname)}


hierarchies = [i[-1] for i in inspect.getmembers(sys.modules[__name__], _predicate)]