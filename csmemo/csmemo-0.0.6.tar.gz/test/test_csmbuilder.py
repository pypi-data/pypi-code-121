import sys
import json
import os
import pandas as pd
from cobra.io import read_sbml_model
from cobra.io import load_model
from cobra.manipulation import remove_genes
from csmemo import csmbuilder



def test_tiny_model():
    model = load_model("textbook")

    gene_expression = {g.id:2 for g in  model.genes}
    gene_thresholds = {g.id:1 for g in  model.genes}

    # SUCOAS	[b0728 and b0729]
    gene_expression["b0729"] = 0

    # THD2	    [b1602 and b1603]
    gene_expression["b1603"] = 0

    # TALA	    [b2464 or b0008]
    gene_expression["b0008"] = 0
    
    # TKT1	    [b2935 or b2465]
    gene_expression["b2465"] = 0

    
    builder = csmbuilder.CSMBuilder(model, gene_expression, gene_thresholds, csm_id='toymodel', 
                                    global_lb_q_threshold=0.0, global_ub_q_threshold=1.0,  
                                    check_consistency=True, copy_model=True, debug_mode=True)

    builder.run_me_solver()
    cs_model = builder.build_csm()   

    cs_model.optimize()
    print(cs_model.summary())



def test_recon3d():
    
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    sbml_fname = os.path.join(data_dir, 'Recon3DModel_301_no_isoforms.xml.gz')
    model = read_sbml_model(sbml_fname, f_replace={})

    json_fname = os.path.join(data_dir,'MIAPACA2_PANCREAS_expression.json')
    with open(json_fname) as fh:
        gene_expression = json.load(fh)
        gene_expression = {f"G_{k}":v for k,v in gene_expression.items()}

    json_fname = os.path.join(data_dir,'expression_thresholds.json')
    with open(json_fname) as fh:
        gene_thresholds = json.load(fh)
        gene_thresholds = {f"G_{k}":v for k,v in gene_thresholds.items()}

    builder = csmbuilder.CSMBuilder(model, gene_expression, gene_thresholds, csm_id='miapaca', 
                                    global_ub_q_threshold=0.8, debug_mode=True, copy_model=False, 
                                    check_consistency=False)

    builder.run_me_solver()
    builder.build_csm()




def test_remove_gpr():
    model = read_sbml_model("data/textbook.xml.gz")
    print("=======================")
    print("Testing GPRs after removing genes")
    rxn_orig = model.reactions.ALCD2x
    print("Reaction:", rxn_orig.id)
    print(f"Genes associated to {rxn_orig.id}:", [g.id for g in rxn_orig.genes])
    print("Original reaction GPR:", rxn_orig.gene_reaction_rule)
    print("=======================")
    print("Coping model")
    model_copy = model.copy()
    print("Removing gene b1478 from model copy")
    remove_genes(model_copy, ["b1478"])
    rxn_copy = model_copy.reactions.ALCD2x
    print("=======================")
    print("Original reaction GPR (after removing copy):", rxn_orig.gene_reaction_rule)
    print("Genes associated to original reaction:", [g.id for g in rxn_orig.genes])
    print("=======================")
    print("Copied reaction GPR:", rxn_copy.gene_reaction_rule)
    print("Genes associated to original reaction:", [g.id for g in rxn_copy.genes])
    

def delete_gene_test():

    def _rename_rxns_ids(model, rxn_rename_dict):
        for r_id_old, r_id_new in rxn_rename_dict.items():
            if r_id_old not in model.reactions:
                continue
            rxn = model.reactions.get_by_id(r_id_old)
            rxn.id = r_id_new
        model.repair()
        return model

    gene_id = 'FOLR2'

    model = read_sbml_model("test/data/Recon3DModel_301_no_isoforms.xml.gz")
    try:
        remove_genes(model, [gene_id])
        print("worked (without renaming)")
    except:
        print("FAIL 1")

    model = read_sbml_model("test/data/Recon3DModel_301_no_isoforms.xml.gz")
    try:
        rxn_rename_dict = {'FOLR2': 'FIXED_FOLR2'}
        model = _rename_rxns_ids(model, rxn_rename_dict)
        remove_genes(model, [gene_id])
        print("worked (with renaming)")
    except:
        print("FAIL 2")

def main():
    # test_tiny_model()
    test_recon3d()
    # test_remove_gpr()
    # delete_gene_test()



main()