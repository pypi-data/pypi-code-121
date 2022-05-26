from os import path
from cobra.io import read_sbml_model
from cobra.manipulation import remove_genes
 
 
def rename_rxns_ids(model, rxn_rename_dict):
    for r_id_old, r_id_new in rxn_rename_dict.items():
        if r_id_old not in model.reactions:
            continue
        rxn = model.reactions.get_by_id(r_id_old)
        rxn.id = r_id_new
    model.repair()
    return model




data_dir = path.join(path.abspath(path.curdir), 'data')
sbml_fname = path.join(data_dir, 'Recon3DModel_301_no_isoforms.xml.gz')
model = read_sbml_model(sbml_fname, f_replace={})


gene_id = 'G_FOLR2'

# remove_genes(model, [gene_id])
# print("worked without renaming")



# model = read_sbml_model("Recon3DModel_301_no_isoforms.xml.gz")
rxn_rename_dict = {'FOLR2': 'FIXED_FOLR2'}
# model = rename_rxns_ids(model, rxn_rename_dict)
remove_genes(model, [gene_id])
print("worked with renaming")