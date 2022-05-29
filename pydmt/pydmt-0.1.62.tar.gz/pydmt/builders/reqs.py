"""
This module build python virtual envrionments
"""


from pydmt.api.one_source_one_target import OneSourceOneTarget
from pydmt.utils.subprocess import check_call
from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.python import collect_reqs, collect_bootstrap_reqs, get_install_args


class BuilderReqs(OneSourceOneTarget):
    """
    This is a review of how to build a python virtual environment:
    # create the virtualenv
    virtualenv [folder]
    # activate it
    source [folder]/bin/activate
    # install packages from file
    pip install -r requirements.txt
    # OR
    python -m pip install -r requirements.txt
    # OR if you want to install a list of packages:
    pip install -r [list of packages]
    # OR
    python -m pip install [list of packages]
    """
    def build(self) -> None:
        args = get_install_args()
        packs = collect_bootstrap_reqs()
        if packs:
            args.extend(packs)
            check_call(args)
        args = get_install_args()
        packs = collect_reqs()
        if packs:
            args.extend(packs)
            check_call(args)
        mkdir_touch(self.target)
