import urllib
import gzip
import os
import shutil
import numpy as np
import pandas as pd
import anndata as ad
from collections import defaultdict
from itertools import product
from pathlib import Path
import pickle

PKG_PATH = Path(__file__).parent

# Load existing network data. 
def load_network(species, benchmark):
    return np.genfromtxt(
        PKG_PATH / 'data' / ('{}_{}.tsv'.format(species, benchmark)), 
        dtype=str)

# General util functions to download raw data from GEO. 
def get_geo_url(gse_id, file_name):
    geo_url = 'https://www.ncbi.nlm.nih.gov/geo/download/?'
    param = {'acc': gse_id, 'format':'file', 'file': file_name}
    return geo_url + urllib.parse.urlencode(param, quote_via=urllib.parse.quote)

def download_geo(dir_path, gse_id, file_name):
    print('Downloading file from ' + gse_id, '...')
    download_url = get_geo_url(gse_id, file_name)
    local_gz_path = os.path.join(dir_path, file_name)
    local_file_path = os.path.join(dir_path, file_name.rstrip('.gz'))
                                   
    urllib.request.urlretrieve(download_url, local_gz_path)
    
    with gzip.open(local_gz_path, 'rb') as f_in:
        with open(local_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            
    return local_file_path

def build_initial_ground_truth(g2g, species, bm):
    original_bm_links = load_network(species, bm)
    links = []
    for link in original_bm_links:
        if link[0] in g2g and link[1] in g2g:
            for gene_id_pair in product(g2g[link[0]], g2g[link[1]]):
                    links.append(gene_id_pair)
    return links


def update_gene_meta(dt):
    if len(dt.uns['gene_dict']) != dt.n_vars:
        dt.uns['gene_dict'] = {
            k: dt.uns['gene_dict'][k] for k in dt.var_names}
        update_gene_name2id(dt)

def update_gene_name2id(dt):
    name2id = defaultdict(list)
    for gene_id in dt.uns['gene_dict']:
        name2id[dt.uns['gene_dict'][gene_id]['gene_name']].append(gene_id)
    dt.uns['gene_name2id'] = name2id

def get_ground_truth(dt, bm):
    update_gene_meta(dt)
    updated_links = []
    g2g = dt.uns['gene_name2id']
    for link in dt.uns[bm]:
        if link[0] in g2g and link[1] in g2g:
            for gene_id_pair in product(g2g[link[0]], g2g[link[1]]):
                updated_links.append(gene_id_pair)
    return updated_links

# load benchmarks
def load_gse_70499(dir_path='', force_reload=False):
    gse_id = 'GSE70499'
    file_name = 'GSE70499_FINAL_master_list_of_genes_counts_MIN.sense.George_WT_v_KO_timecourse.txt.gz'
    dir_path = os.path.join(dir_path, gse_id)
    processed_file_path = os.path.join(dir_path, gse_id+'.pkl')
    
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        
    if os.path.exists(processed_file_path) and force_reload==False:
        print('Loading from processed file...')
        with open(processed_file_path, 'rb') as f:
            dt = pickle.load(f)
        return dt
    
    raw_file = download_geo(dir_path, gse_id, file_name)
    
    print('Processing...')
    raw = pd.read_csv(raw_file, sep='\t')
    
    raw.id = raw.id.str.replace('gene:', '')
    raw.geneSymbol = raw.geneSymbol.str.upper()

    gene_dict = {}
    for i in range(raw.shape[0]):
        gene_dict[raw.id[i]] = {
            'gene_name': raw.geneSymbol[i],
            'geneCoordinate': raw.geneCoordinate[i],
        }

    del raw['geneSymbol']
    del raw['geneCoordinate']

    dt = raw.set_index('id').transpose().reset_index()
    dt_meta_ids = dt['index']
    dt_meta = dt_meta_ids.str.split('_', expand=True)
    del dt['index']
    dt_array = dt.to_numpy()

    ad_dt = ad.AnnData(dt_array, dtype=int)
    ad_dt.var_names = np.array(dt.columns, dtype=str)
    ad_dt.obs_names = dt_meta[2].to_numpy()
    ad_dt.obs['genotype'] = pd.Categorical(dt_meta[0])
    ad_dt.obs['timepoint'] = pd.Categorical(
        dt_meta[1].str.replace('ZT', '').to_numpy(dtype=int)
    )
    ad_dt.uns['gene_dict'] = gene_dict
    update_gene_name2id(ad_dt)
    
    print('Adding benchmarks...')
    ad_dt.uns['benchmark_RN'] = build_initial_ground_truth(
        ad_dt.uns['gene_name2id'], 'mouse', 'RN'
    )
    ad_dt.uns['benchmark_TRRUST'] = build_initial_ground_truth(
        ad_dt.uns['gene_name2id'], 'mouse', 'TRRUST'
    )
    ad_dt.uns['benchmark_BEELINE'] = build_initial_ground_truth(
        ad_dt.uns['gene_name2id'], 'mouse', 'BEELINE'
    )
    ad_dt.uns['benchmark_STRING'] = build_initial_ground_truth(
        ad_dt.uns['gene_name2id'], 'mouse', 'STRING'
    )

    with open(processed_file_path, 'wb') as f:
        pickle.dump(ad_dt, f)
    
    print('Complete!')
    return ad_dt