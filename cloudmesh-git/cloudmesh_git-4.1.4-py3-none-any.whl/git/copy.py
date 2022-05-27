import glob
import os
import textwrap

from cloudmesh.common.console import Console


# inspired from
# https://gist.githubusercontent.com/trongthanh/2779392/raw/6aa7ef47ed3c1a586fafd1c8b74adcf4216e52ce/gistfile1.sh


#
# cms git copy cloudmesh/cloudmesh-cloud cloudmesh/cloudmesh-admin cloudmesh/admin cloudmesh/check cloudmesh/management cloudmesh/source cloudmesh/start cloudmesh/stop
#

def copy_dir(original="cloudmesh/cloudmesh-cloud",
             destination=None,
             directories=None,
             move=None,
             branch=None):
    def _run(script):
        for command in script.splitlines():
            if command not in [""]:
                print(command)
                os.system(command)
            else:
                print()

    if None in [original, destination, directories]:
        Console.error("A parameter is missing")
        return ""
    move = move or "move"
    dir_original = os.path.basename(original)
    dir_destination = os.path.basename(destination)

    branch = branch or f"from-{dir_original}"
    cache = "cache"

    dirs = ' '.join(directories)

    script = "rm -rf tmp"
    if not os.path.isdir(f"{cache}"):
        script += textwrap.dedent(f"""
        rm -rf {cache}
        mkdir {cache}
        cd {cache}; git clone git@github.com:{original}.git
        cd {cache}; git clone git@github.com:{destination}.git
        """)
    script += textwrap.dedent(f"""
        cp -r {cache} tmp
        cd tmp/{dir_original}; mkdir {move}
    """)

    _run(script)

    script = ""
    #
    # collect directories to {move}
    #
    os.chdir(f"tmp/{dir_original}")

    move_dirs = set()
    for directory in directories:
        dirname = os.path.dirname(directory)
        move_dirs.add(f"{dirname}")

    for directory in move_dirs:
        script += "git remote rm origin\n"
        script += f"mkdir -p {move}/{directory}\n"
        script += f"git add  {move}/{directory}\n"

    for directory in directories:
        script += f"git mv {directory} move/{directory}\n"

    entries = glob.glob("**")
    print(entries)
    entries.remove(f"{move}")

    for entry in entries:
        script += f"rm -rf {entry}\n"

    script += textwrap.dedent(f"""
    git filter-branch --subdirectory-filter --prune-empty {move} -- -- all 
    git commit -m "Directories moved: {dirs}" .
    git gc --aggressive
    git prune
    git clean -df
    """)

    _run(script)

    #
    # Prepare the destination
    #
    os.chdir(f"../{dir_destination}")

    script = textwrap.dedent(f"""
    git remote add {branch} ../{dir_original}
    git fetch {branch}
    git branch {branch} remotes/{branch}/main
    git merge {branch} --allow-unrelated-histories

    git remote rm {branch}
    git branch -d {branch}

    pwd

    ls 

    """)

    _run(script)

    print("Now do:")
    print()
    print(f"cd tmp/{dir_destination}; git push origin main")
    print()
