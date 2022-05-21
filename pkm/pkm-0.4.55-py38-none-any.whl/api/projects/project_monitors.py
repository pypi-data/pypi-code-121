# from typing import Iterable, TYPE_CHECKING
#
# from pkm.api.repositories.repository import Repository
# from pkm.utils.monitors import no_monitor, Monitor
#
# if TYPE_CHECKING:
#     from pkm.api.dependencies.dependency import Dependency
#     from pkm.api.projects.project import Project
#     from pkm.api.projects.project_group import ProjectGroup
#
#
# # noinspection PyMethodMayBeStatic,PyUnusedLocal
# class ProjectOperationsMonitor():
#     def on_environment_modification(self, project: "Project") -> EnvironmentOperationsMonitor:
#         return no_monitor()
#
#     def on_dependencies_modified(self, project: "Project", old_deps: Iterable["Dependency"],
#                                  new_deps: Iterable["Dependency"]):
#         ...
#
#     def on_lock_modified(self):
#         ...
#
#     def on_pyproject_modified(self):
#         ...
#
#     def on_publish(self, repo: Repository) -> Monitor:
#         return no_monitor()
#
#
# # noinspection PyMethodMayBeStatic,PyUnusedLocal
# class ProjectGroupOperationsMonitor(Monitor):
#     def on_access_child_project(self, group: "ProjectGroup", child_project: "Project") -> ProjectOperationsMonitor:
#         return no_monitor()
#
#     def on_access_child_group(
#             self, group: "ProjectGroup", child_group: "ProjectGroup") -> "ProjectGroupOperationsMonitor":
#         return no_monitor()
#
#     def on_build_all(self, group: "ProjectGroup") -> Monitor:
#         return no_monitor()
#
#     def on_install_all(self, group: "ProjectGroup") -> Monitor:
#         return no_monitor()
#
#     def on_publish_all(self, group: "ProjectGroup") -> Monitor:
#         return no_monitor()
