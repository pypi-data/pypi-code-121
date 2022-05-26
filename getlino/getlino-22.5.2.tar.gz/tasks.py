from atelier.invlib import setup_from_tasks
ns = setup_from_tasks(
    globals(), 'getlino',
    languages=["en"],
    # tolerate_sphinx_warnings=True,
    # blogref_url="http://lino-framework.org",
    revision_control_system='git',
    cleanable_files=['docs/api/getlino.*'],
    prep_command="./prep.sh")
