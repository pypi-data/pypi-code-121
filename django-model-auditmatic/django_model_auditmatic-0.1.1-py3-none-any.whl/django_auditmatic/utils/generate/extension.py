"""
    generate sql to install hstore extension
"""


def generate_install_hstore():
    """returns sql to install hstore extension"""
    return """CREATE EXTENSION IF NOT EXISTS hstore"""
