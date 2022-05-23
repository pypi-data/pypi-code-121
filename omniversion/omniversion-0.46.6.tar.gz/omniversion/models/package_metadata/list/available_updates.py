"""Result of a versions match, i.e. a list of installations with corresponding versions"""
from collections import UserList


class AvailableUpdates(UserList):
    """List of packages for which a newer version is available"""

    def __repr__(self):
        num_updates = len([item for item in self if item.current is not None])
        num_not_installed = len([item for item in self if item.current is None])
        components = []
        if num_updates == 1:
            components.append("1 outdated package")
        if num_updates > 1:
            components.append(f"{num_updates} outdated packages")
        if num_not_installed == 1:
            components.append("1 package not installed")
        if num_not_installed > 1:
            components.append(f"{num_not_installed} packages not installed")
        if len(components) > 0:
            return ", ".join(components).capitalize()
        return "All packages up-to-date"
