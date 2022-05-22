import os


class DatabaseUtils:

    @classmethod
    def load_script_file(cls, file: str) -> str:
        """Loads commands from a file"""

        if not os.path.isfile(file):
            raise FileNotFoundError("Script file ({}) not found".format(file))

        with open(file) as f:
            lines = f.readlines()

        return "".join(lines)
