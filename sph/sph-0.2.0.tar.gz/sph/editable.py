import ast
import re
from pathlib import Path

import click
from git import Repo

from sph.utils import Editable


def create_editable_dependency(editable, editables):
    all_required_lib = []
    with open(editable.conan_path, 'r') as conanfile:
        conanfile_ast = ast.parse(conanfile.read())
        for node in ast.iter_child_nodes(conanfile_ast):
            if isinstance(node, ast.ClassDef):
                for class_node in ast.iter_child_nodes(node):
                    if isinstance(class_node, ast.Assign):
                        for target in class_node.targets:
                            if target.id == 'requires':
                                all_required_lib += [
                                    elt.value for elt in class_node.value.elts
                                ]
    for other_editable in [x for x in editables if x is not editable]:
        for dep in all_required_lib:
            if dep.split('/')[0] == other_editable.name:
                editable.required_lib.append(other_editable)


def create_editable_from_workspace(
        workspace_path: Path, workspace_data, github_client=None
):
    editables = list()

    workspace_base_path = workspace_path.parents[0]

    for name, path in workspace_data['editables'].items():
        project_conan_path = (workspace_base_path / path['path'])
        short_name = name.split('/')[0]
        repo = Repo(project_conan_path.parents[0].resolve())
        remote_url = list(repo.remote('origin').urls)[0]
        match = re.search(r'github.com:(.*)/(.*).git', remote_url)

        if match and github_client:
            org = match.group(1)
            gh_repo = match.group(2)
        elif github_client:
            raise click.Abort()

        editable = Editable(
            name,
            short_name,
            (project_conan_path / 'conanfile.py').resolve(),
            list(),
            repo,
            github_client.get_repo(f'{org}/{gh_repo}') if github_client else None
        )
        editables.append(editable)

    for ed in editables:
        create_editable_dependency(ed, editables)

    return editables
