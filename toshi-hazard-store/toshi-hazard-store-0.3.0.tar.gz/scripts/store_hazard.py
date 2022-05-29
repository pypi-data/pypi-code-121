"""Script to export an openquake calculation and save it with toshi-hazard-store."""

import argparse
import datetime as dt
import re
from collections import namedtuple

import h5py
import numpy as np
import pandas as pd
from dateutil.tz import tzutc
from openquake.baselib.general import BASE183
from openquake.calculators.export.hazard import extract, get_sites

# new imports
from openquake.commonlib import datastore

from toshi_hazard_store import model, query

CustomLocation = namedtuple("CustomLocation", "site_code lon lat")
CustomHazardCurve = namedtuple("CustomHazardCurve", "loc poes")


def parse_logic_tree_branches(file_id):

    with h5py.File(file_id) as hf:

        # read and prepare the source model logic tree for documentation
        ### full_lt is a key that contains subkeys for each type of logic tree
        ### here we read the contents of source_model_lt into a dataframe
        source_lt = pd.DataFrame(hf['full_lt']['source_model_lt'][:])
        for col in source_lt.columns[:-1]:
            source_lt.loc[:, col] = source_lt[col].str.decode('ascii')

        # identify the source labels used in the realizations table
        source_lt.loc[:, 'branch_code'] = [x for x in BASE183[0 : len(source_lt)]]
        source_lt.set_index('branch_code', inplace=True)

        # read and prepare the gsim logic tree for documentation
        ### full_lt is a key that contains subkeys for each type of logic tree
        ### here we read the contents of gsim_lt into a dataframe
        gsim_lt = pd.DataFrame(hf['full_lt']['gsim_lt'][:])
        for col in gsim_lt.columns[:-1]:
            gsim_lt.loc[:, col] = gsim_lt.loc[:, col].str.decode('ascii')

        # break up the gsim df into tectonic regions (one df per column of gsims in realization labels. e.g. A~AAA)
        # the order of the dictionary is consistent with the order of the columns
        gsim_lt_dict = {}
        for i, trt in enumerate(np.unique(gsim_lt['trt'])):
            df = gsim_lt[gsim_lt['trt'] == trt]
            df.loc[:, 'branch_code'] = [x[1] for x in df['branch']]
            df.set_index('branch_code', inplace=True)
            ### the branch code used to be a user specified string from the gsim logic tree .xml
            ### now the only way to identify which regionalization is used is to extract it manually
            for j, x in zip(df.index, df['uncertainty']):
                tags = re.split('\\[|\\]|\nregion = \"|\"', x)
                if len(tags) > 4:
                    df.loc[j, 'model name'] = f'{tags[1]}_{tags[3]}'
                else:
                    df.loc[j, 'model name'] = tags[1]
            gsim_lt_dict[i] = df

    # read and prep the realization record for documentation
    ### this one can be read into a df directly from the dstore's full_lt
    ### the column titled 'ordinal' is dropped, as it will be the same as the 0-n index
    dstore = datastore.read(file_id)
    rlz_lt = pd.DataFrame(dstore['full_lt'].rlzs).drop('ordinal', axis=1)

    # add to the rlt_lt to note which source models and which gsims were used for each branch
    for i_rlz in rlz_lt.index:
        # rlz name is in the form A~AAA, with a single source identifier followed by characters for each trt region
        srm_code, gsim_codes = rlz_lt.loc[i_rlz, 'branch_path'].split('~')

        # copy over the source label
        rlz_lt.loc[i_rlz, 'source combination'] = source_lt.loc[srm_code, 'branch']

        # loop through the characters for the trt region and add the corresponding gsim name
        for i, gsim_code in enumerate(gsim_codes):
            trt, gsim = gsim_lt_dict[i].loc[gsim_code, ['trt', 'model name']]
            rlz_lt.loc[i_rlz, trt] = gsim

    return source_lt, gsim_lt, rlz_lt


def get_data(dstore, im, kind):
    sitemesh = get_sites(dstore['sitecol'])
    key = 'hcurves?kind=%s&imt=%s' % (kind, im)
    hcurves = extract(dstore, key)[kind]  # shape (N, 1, L1)

    # Local helper classes, the oq classes aren't helping
    return [CustomHazardCurve(CustomLocation(*site), poes[0]) for site, poes in zip(sitemesh, hcurves)]


def export_stats(dstore, toshi_id, kind):
    oq = dstore['oqparam']
    curves = []
    for im in oq.imtls:
        for hazcurve in get_data(dstore, im, kind):
            # build the model objects....
            lvps = [
                model.LevelValuePairAttribute(lvl=float(x), val=float(y)) for (x, y) in zip(oq.imtls[im], hazcurve.poes)
            ]
            obj = model.ToshiOpenquakeHazardCurveStats(
                loc=hazcurve.loc.site_code.decode(), imt=im, agg=kind, values=lvps
            )
            curves.append(obj)
            if len(curves) >= 50:
                query.batch_save_hcurve_stats(toshi_id, models=curves)
                curves = []

        # finally
        if len(curves):
            query.batch_save_hcurve_stats(toshi_id, models=curves)


def export_rlzs(dstore, toshi_id, kind):
    oq = dstore['oqparam']
    curves = []
    for im in oq.imtls:

        for hazcurve in get_data(dstore, im, kind):
            # build the model objects....
            lvps = [
                model.LevelValuePairAttribute(lvl=float(x), val=float(y)) for (x, y) in zip(oq.imtls[im], hazcurve.poes)
            ]
            obj = model.ToshiOpenquakeHazardCurveRlzs(
                loc=hazcurve.loc.site_code.decode(), imt=im, rlz=kind, values=lvps
            )
            curves.append(obj)
            if len(curves) >= 50:
                query.batch_save_hcurve_rlzs(toshi_id, models=curves)
                curves = []

        # finally
        if len(curves):
            query.batch_save_hcurve_rlzs(toshi_id, models=curves)


def export_meta(toshi_id, dstore):
    """Extract and same the meta data."""
    oq = dstore['oqparam']
    sitemesh = get_sites(dstore['sitecol'])
    source_lt, gsim_lt, rlz_lt = parse_logic_tree_branches(dstore.filename)

    obj = model.ToshiOpenquakeHazardMeta(
        partition_key="ToshiOpenquakeHazardMeta",
        updated=dt.datetime.now(tzutc()),
        vs30=oq.reference_vs30_value,  # vs30 value
        haz_sol_id=toshi_id,
        imts=list(oq.imtls.keys()),  # list of IMTs
        locs=[tup[0].decode() for tup in sitemesh.tolist()],  # list of Location codes
        src_lt=source_lt.to_json(),  # sources meta as DataFrame JSON
        gsim_lt=gsim_lt.to_json(),  # gmpe meta as DataFrame JSON
        rlz_lt=rlz_lt.to_json(),  # realization meta as DataFrame JSON
    )
    obj.hazsol_vs30_rk = f"{obj.haz_sol_id}:{obj.vs30}"
    obj.save()


def extract_and_save(calc_id, toshi_id):
    """Do the work"""

    dstore = datastore.read(calc_id)
    oq = dstore['oqparam']

    R = len(dstore['full_lt'].get_realizations())

    # Metadata
    export_meta(toshi_id, dstore)

    # Hazard curves
    for kind in reversed(list(oq.get_kinds('', R))):  # do the stats curves first
        if kind.startswith('rlz-'):
            export_rlzs(dstore, toshi_id, kind)
        else:
            export_stats(dstore, toshi_id, kind)

    dstore.close()


def parse_args():
    parser = argparse.ArgumentParser(description='deluge_dls.py (dls)  - list deluge FS contents')
    parser.add_argument('calc_id', help='openquake calc id.')
    parser.add_argument('toshi_id', help='openquake_hazard_solution id.')
    # parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    # parser.add_argument("-s", "--summary", help="summarise output", action="store_true")
    parser.add_argument('-D', '--debug', action="store_true", help="print debug statements")
    args = parser.parse_args()
    return args


def handle_args(args):
    if args.debug:
        print(f"Args: {args}")

    ## model.drop_tables() #DANGERMOUSE
    ## model.migrate() #ensure model Table(s) exist (check env REGION, DEPLOYMENT_STAGE, etc

    extract_and_save(int(args.calc_id), args.toshi_id)


def main():
    handle_args(parse_args())


if __name__ == '__main__':
    main()  # pragma: no cover
