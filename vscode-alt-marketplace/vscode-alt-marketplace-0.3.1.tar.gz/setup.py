from ast import arg
from pathlib import Path
import shutil, sys
from setuptools import setup as _setup, find_packages


root = Path(__file__).parent
PKG = root.name.replace("-", "_")
PKG_NAME = PKG.replace("_", "-")

src = root / "src"
dist = root / "dist"
dist.mkdir(exist_ok=True, parents=True)


def clean_dist():
    if PKG == "_":
        for path in (root / "dist").iterdir():
            shutil.rmtree(path)
    else:
        for path in dist.iterdir():
            path.unlink()


def clean():

    for path in src.iterdir():
        if path.suffix == ".egg-info":
            shutil.rmtree(path)
    for path in root.iterdir():
        if path.suffix == ".egg-info":
            shutil.rmtree(path)
    shutil.rmtree(root / "build", ignore_errors=True)


if sys.argv[1] == "clean-dist":
    clean_dist()
    exit()


pkgs = find_packages(str(src))
readme_file = next((f for f in root.iterdir() if f.stem == "README"), None)
if readme_file:
    readme = readme_file.read_text()

    if readme_file.suffix == ".rst":
        readme_type = f"text/x-rst"
    elif readme_file.suffix == ".md":
        readme_type = "text/markdown"
    else:
        readme_type = "text/plain"
else:
    readme = None
    readme_type = None
print(readme_type)

import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


pkgs = find_packages("src")


def setup(**kwargs):
    _setup(
        name=PKG_NAME,
        version=(root / "VERSION").read_text(),
        description=(root / "DESCRIPTION").read_text(),
        long_description=readme,
        long_description_content_type=readme_type
        if readme_type != "text/x-rst"
        else None,
        author="Jose A.",
        author_email="jose-pr@coqui.dev",
        url=f"https://github.com/jose-pr/{root.resolve().name}",
        package_dir={PKG: "src"},
        packages=[PKG, *[(PKG +"."+ pkg) for pkg in pkgs]],
        install_requires=(root / "requirements.txt").read_text().splitlines(),
        package_data={
            "": [
                *package_files("src/examples/templates"),
                *package_files("src/examples/static"),
            ],
        },
        **kwargs,
    )


clean()
if sys.argv[1] == "dist-build":
    clean_dist()
    sys.argv[1] = "bdist_wheel"
    setup()
    sys.argv[1] = "sdist"
    setup()
else:
    setup()

clean()
