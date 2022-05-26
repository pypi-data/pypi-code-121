from cobra.io import load_model
from csmemo.reachability import ReachabilityTester



def test_tiny_model():
    model = load_model("textbook")

    biomass = [r for r in model.reactions if r.objective_coefficient==1][0]

    target_products = [m.id for m in biomass.reactants]
    print(target_products)
    tester = ReachabilityTester(model, target_products)
    result = tester.single_gene_reachability()
    result.to_csv('reachability_frame.tsv', sep='\t')



test_tiny_model()