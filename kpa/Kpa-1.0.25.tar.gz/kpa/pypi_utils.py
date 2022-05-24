from pathlib import Path
import urllib.request
import subprocess, json, sys


def upload_package(package_name:str, current_version:str) -> None:
    # TODO: look into `class UploadCommand(setuptools.Command)` from <https://github.com/kennethreitz/setup.py/blob/master/setup.py#L49>
    package_name = package_name.lower()

    # Make sure there's no unstaged changes
    git_workdir_returncode = subprocess.run('git diff-files --quiet'.split()).returncode
    assert git_workdir_returncode in [0,1]
    if git_workdir_returncode == 1:
        print('=> git workdir has changes')
        print('=> please either revert or stage them')
        sys.exit(1)

    # If the local version is the same as the PyPI version, increment it.
    pypi_url = f'https://pypi.python.org/pypi/{package_name}/json'
    latest_version = json.loads(urllib.request.urlopen(pypi_url).read())['info']['version']
    # Note: it takes pypi a minute to update the API, so this can be wrong.
    if latest_version == current_version:
        new_version = next_version(current_version)
        print(f'=> autoincrementing version {current_version} -> {new_version}')
        Path(f'{package_name}/version.py').write_text(f"version = '{new_version}'\n")
        current_version = new_version
        subprocess.run(['git','stage',f'{package_name}/version.py'], check=True)

    # Commit any staged changes
    git_index_returncode = subprocess.run('git diff-index --quiet --cached HEAD'.split()).returncode
    assert git_index_returncode in [0,1]
    if git_index_returncode == 1:
        print('=> git index has changes; committing them')
        subprocess.run(['git','commit','-m',current_version], check=True)

    # Clean and repopulate ./dist/*
    if Path('dist').exists() and list(Path('dist').iterdir()):
        # Double check that we are where we think we are
        setuppy = Path('dist').absolute().parent / 'setup.py'
        assert setuppy.is_file() and package_name in setuppy.read_text().lower()
        for child in Path('dist').absolute().iterdir():
            assert child.name.lower().startswith(f'{package_name}-'), child
            print('=> unlinking', child)
            child.unlink()
    subprocess.run('python3 setup.py sdist bdist_wheel'.split(), check=True)

    # Upload
    if not Path('~/.pypirc').expanduser().exists():
        print('=> warning: you need a ~/.pypirc')
    try: subprocess.run(['twine','--version'], check=True)
    except Exception: print('Run `pip3 install twine` and try again'); sys.exit(1)
    subprocess.run('twine upload dist/*'.split(), check=True)

    if git_index_returncode == 1:
        print('=> Now do `git push`.')

def next_version(version:str) -> str:
    new_version_parts = version.split('.')
    new_version_parts[2] = str(1+int(new_version_parts[2]))
    return '.'.join(new_version_parts)
assert next_version('1.1.5') == '1.1.6'
