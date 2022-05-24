import subprocess
from atelier.invlib import setup_from_tasks

def fixtures_updater(ctx):
    # print("20210721", ctx.languages)
    from lino_xl.lib.countries.wikidata import get_human_settlements
    for iso_code in ['be', 'ee', 'bd']:
        get_human_settlements(iso_code, languages=ctx.languages, force_update=True)
    # from lino_xl.lib.countries.wikidata import get_cities
    # get_cities(["be", "ee", "bd"], ctx.languages)
    # cmd = "python lino_xl/lib/countries/wikidata/get_cities.py --languages"
    # cp = subprocess.run(cmd, **kw)
    #             if cp.returncode != 0:


ns = setup_from_tasks(
    globals(), "lino_xl",
    languages="en de fr et nl pt-br es zh-hant bn".split(),
    fixtures_updater=fixtures_updater,
    tolerate_sphinx_warnings=False,
    doc_trees=[],
    blogref_url='https://luc.lino-framework.org',
    revision_control_system = 'git',
    locale_dir='lino_xl/lib/xl/locale')
