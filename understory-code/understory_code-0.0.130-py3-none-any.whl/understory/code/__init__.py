"""
Host code in the understory.

- Supports [PEP 503 -- Simple Repository API][0] managing Python packages.

[0]: https://www.python.org/dev/peps/pep-0503/

"""

# TODO PEP 592 -- Adding "Yank" Support to the Simple API
# TODO PEP 658 -- Serve Distribution Metadata in the Simple Repository API

import re
import subprocess
from pathlib import Path

import warez
import web

app = web.application(
    __name__,
    prefix="code",
    args={
        "project": r"[a-z0-9.-]+",
        "release": r"((\d+\.)?\d+\.)?\d+",
        "filename": r"[\w./\-]+",
        "package": r"[\w.-]+",
    },
    model={
        "projects": {
            "name": "TEXT UNIQUE",
            "pypi": "TEXT UNIQUE",
        },
        "packages": {
            "project_id": "INTEGER",
            "filename": "TEXT",
            "author": "TEXT",
            "author_email": "TEXT",
            "classifiers": "JSON",
            "home_page": "TEXT",
            "keywords": "JSON",
            "license": "TEXT",
            "project_urls": "JSON",
            "requires_dist": "JSON",
            "requires_python": "TEXT",
            "sha256_digest": "TEXT",
            "summary": "TEXT",
            "version": "TEXT",
        },
    },
)

code_dir = Path("code")


@app.query
def create_project(db, name):
    """Create a project."""
    return db.insert("projects", name=name, pypi=name)


@app.query
def get_projects(db):
    """Return a list of project names."""
    return [r["name"] for r in db.select("projects", what="name", order="name")]


@app.query
def get_project_from_pypi(db, pypi_name):
    """Return the project associated with `pypi_name`."""
    return db.select("projects", what="name", where="pypi = ?", vals=[pypi_name])[0][
        "name"
    ]


@app.query
def create_package(db, form):
    """Create a project."""
    project_id = db.select(
        "projects", what="rowid, name", where="name = ?", vals=[form.name]
    )[0]["rowid"]
    return db.insert(
        "packages",
        project_id=project_id,
        filename=form.content.fileobj.filename,
        author=form.author,
        author_email=form.author_email,
        # classifiers=form.classifiers,
        home_page=form.home_page,
        # keywords=form.keywords.split(","),
        license=form.license,
        # project_urls=form.project_urls if "project_urls" in form else [],
        # requires_dist=form.requires_dist,
        requires_python=form.requires_python,
        sha256_digest=form.sha256_digest,
        summary=form.summary,
        version=form.version,
    )


@app.query
def get_packages(db, project):
    """Return a list of packages for given project."""
    return db.select(
        "packages",
        join="""projects ON packages.project_id = projects.rowid""",
        where="projects.name = ?",
        vals=[project],
    )


@app.query
def get_package_versions(db, project):
    """Return a list of packages for given project."""
    return [
        r["version"]
        for r in db.select(
            "packages",
            what="DISTINCT version",
            join="""projects ON packages.project_id = projects.rowid""",
            where="projects.name = ?",
            vals=[project],
            order="version",
        )
    ]


@app.control("")
class Code:
    """Code index."""

    owner_only = ["post"]

    def get(self):
        """Return a list of projects."""
        return app.view.index(app.model.get_projects())

    def post(self):
        """Create a project."""
        project = web.form("project").project
        app.model.create_project(project)
        project_dir = code_dir / project
        bare_repo = project_dir / "source.git"
        working_repo = project_dir / "working"
        repo = warez.Repo(bare_repo, init=True, bare=True)
        repo.update_server_info()
        repo.config("http.receivepack", "true")
        warez.clone_repo(bare_repo, working_repo)  # TODO shallow clone?
        post_receive_hook = bare_repo / "hooks/post-receive"
        with post_receive_hook.open("w") as fp:
            fp.write("#!/bin/sh\n\ngit -C $PWD/../working --git-dir=.git pull --rebase")
        subprocess.run(["chmod", "775", post_receive_hook])
        subprocess.run(["chgrp", "www-data", bare_repo, working_repo, "-R"])
        subprocess.run(["chmod", "g+w", bare_repo, working_repo, "-R"])
        return web.Created(app.view.project_created(project), f"/{project}")


@app.control("{project}")
class Project:
    """Project index."""

    def get(self, project):
        """Return details about the project."""
        return app.view.project(
            project,
            warez.Repo(code_dir / project / "working"),
            app.model.get_package_versions(project),
        )


@app.control("{project}.git")
class ProjectRedirect:
    """Project .git redirect."""

    def get(self, project):
        """Redirect to main project index."""
        raise web.SeeOther(project)


@app.control("{project}/releases/{release}")
class ProjectRelease:
    """A project's release."""

    def get(self, project, release):
        """Return the package file."""
        files = sorted((code_dir / project / "releases" / release).iterdir())
        return app.view.project_release(project, release, files)


@app.control("{project}/releases/{release}/files/{filename}")
class ProjectReleaseFile:
    """A file in a project's release."""

    def get(self, project, release, filename):
        """Return the release's file."""
        filepath = code_dir / project / "releases" / release / filename
        try:
            with filepath.open() as fp:
                content = fp.read()
        except IsADirectoryError:
            content = filepath.iterdir()
        return app.view.project_release_file(project, release, filename, content)


@app.control("{project}/releases/{package}")
class ProjectReleasePackage:
    """A project's release package."""

    def get(self, project, package):
        """Return the package file."""
        name, release = split_release(package)
        return code_dir / project / "releases" / release


def split_release(release):
    return re.match(r"([\w-]+)\-(\d+\.\d+\.\d+.*)", release).groups()


@app.control("_pypi")
class PyPIIndex:
    """PyPI repository in Simple Repository format."""

    # TODO owner_only = ["post"]

    def get(self):
        """Return a simplified list of the repository's projects."""
        return app.view.pypi_index(app.model.get_projects())

    def post(self):
        """Accept PyPI package upload."""
        form = web.form(":action")
        if form[":action"] != "file_upload":
            raise web.BadRequest(f"Provided `:action={form[':action']}` not supported.")
        release_file = form.content.save(file_dir="/tmp")
        release_name, release_remaining = split_release(release_file.name)
        project = app.model.get_project_from_pypi(release_name)
        releases_dir = code_dir / project / "releases"
        releases_dir.mkdir(exist_ok=True)
        release_file = release_file.replace(releases_dir / release_remaining)
        if release_file.suffix == ".gz":
            release_version = release_file.stem[:-4]
            release_dir = f"{release_name}-{release_version}"
            subprocess.run(
                [
                    "tar",
                    "xf",
                    release_file.name,
                ],
                cwd=releases_dir,
            )
            (releases_dir / release_dir).replace(releases_dir / release_version)
        app.model.create_package(form)
        raise web.Created(
            "Package has been uploaded.",
            "/{form.name}/packages/{form.content.fileobj.filename}",
        )


@app.control("_pypi/{project}")
class PyPIProject:
    """PyPI project in Simple Repository format."""

    def get(self, project):
        """Return a simplified list of the project's packages."""
        if packages := app.model.get_packages(project):
            return app.view.pypi_project(project, packages)
        raise web.SeeOther(f"https://pypi.org/simple/{project}")
