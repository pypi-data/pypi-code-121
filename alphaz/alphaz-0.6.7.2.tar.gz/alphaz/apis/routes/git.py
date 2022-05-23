from ...utils.api import route, Parameter

from core import core

api         = core.api
db          = core.db
log         = core.get_logger('api')

@route("/git",parameters=[])
def api_git():
    import git
    repo = git.Repo(search_parent_directories=True)
    return {
        'sha': repo.head.object.hexsha,
        'message': repo.head.object.message,
        'active_branch': repo.active_branch.name,
    }