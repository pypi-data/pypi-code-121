import os
import shutil
import logging

logger = logging.getLogger("app")


class OutputHandler(object):
    """
    How should output be handled?
    """

    def __init__(self, transform, config):
        self.transform = transform
        self.config = config

    def process(self, tempfile):
        raise Exception("Not Implemented")


class FileOutputHandler(OutputHandler):
    """
    Config in this case is a simple path.
    """

    def exists(self, params):
        output = self.config
        output = self.transform.get_file(output, abspath=False, extra=params)
        return os.path.exists(output)

    def process(self, tempfile, params):

        output = self.config
        output = self.transform.get_file(output, abspath=False, extra=params)

        # Move
        try:
            os.makedirs(os.path.dirname(output))
        except:
            pass
        shutil.move(tempfile, output)
        logger.debug(
            "Handled output",
            extra={
                "transform": self.transform.name,
                "data": "From: {}\nTo: {}".format(tempfile, output),
            },
        )


def get_mysql_config(cred):
    mapping = {
        "host": ["HOST", "host", "hostname"],
        "user": ["USER", "user", "username"],
        "port": ["port", "PORT"],
        "password": ["PASSWORD", "PASSWD", "password", "passwd", "pwd"],
        "db": ["db", "database", "NAME", "name"],
        "options": ["OPTIONS", "options"],
    }

    config = {}
    for k, alternatives in mapping.items():
        for alt in alternatives:
            if alt in cred:
                config[k] = cred[alt]
                break

    options = config.get("options", {})
    config.update(options)
    return config
