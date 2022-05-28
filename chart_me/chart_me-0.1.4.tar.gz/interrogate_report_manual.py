# %%
# Third party imports
from interrogate import coverage

cov = coverage.InterrogateCoverage(paths=["src"])
results = cov.get_coverage()
cov.print_results(results, None, 1)
# %%
cov.print_results(results, None, 2)
# %%
