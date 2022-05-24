import os

from ._util import ensure_path


class PathContextManager:
    """
    Context manager class which changes the cwd to a new
    path. If a relative path is given, it is considered
    relative to the current cwd.
    """
    def __init__(self, path: str, ensure: bool = False):
        self.cwd: str = ""  # The cwd before changing to the given path; gets set on entry
        self.path: str = path  # The path to change to
        self.ensure: bool = ensure  # Whether to ensure the path exists by creating it if needed

    def __enter__(self):
        # Save the cwd
        self.cwd = os.path.abspath(os.getcwd())

        # Optionally ensure the path exists
        if self.ensure:
            ensure_path(self.path)

        # Calculate the new path
        new_path = os.path.join(self.cwd, self.path) if not os.path.isabs(self.path) else self.path

        # Change to the new path
        os.chdir(new_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Change back to the previous cwd
        os.chdir(self.cwd)

        # Re-raise any exceptions
        return False


# Sugar definition
offset_cwd = PathContextManager
