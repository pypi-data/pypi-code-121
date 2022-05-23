"""
`eo_types`
=======================================================================
Module will hold the enum classes for EmbedOps Tools
* Author(s): Bailey Steinfadt
"""

from enum import Enum

GH_CI_CONFIG_FILE_PATH = ".github/workflows"
BB_CI_CONFIG_FILENAME = "bitbucket-pipelines.yml"
GL_CI_CONFIG_FILENAME = ".gitlab-ci.yml"
EO_CI_CONFIG_FILENAME = ".embedops-ci.yml"
SUPPORTED_CI_FILENAMES = [
    BB_CI_CONFIG_FILENAME,
    GL_CI_CONFIG_FILENAME,
    EO_CI_CONFIG_FILENAME,
]


class YamlType(Enum):
    """Types of Yaml Files EmbedOps Tools supports"""

    UNSUPPORTED = 0
    GITLAB = 1
    BITBUCKET = 2
    GITHUB = 3


class LocalRunContext:
    """Object to store the context for locally run CI jobs"""

    def __init__(
        self,
        job_name: str,
        docker_tag: str,
        script_lines: list = None,
        variables: dict = None,
    ):
        self._job_name = job_name.strip('"')
        self._docker_tag = docker_tag.strip('"')
        if script_lines is None:
            self._script = []
        else:
            self._script = script_lines
        if variables is None:
            self._variables = {}
        else:
            self._variables = variables

    @property
    def job_name(self):
        """String with the name of the job"""
        return self._job_name

    @property
    def docker_tag(self):
        """String for the Docker tag the job will be launched in"""
        return self._docker_tag

    @property
    def script(self):
        """List containing the job's script from the YAML file, if it exists"""
        return self._script

    @property
    def variables(self):
        """Dictionary with any variables defined in the YAML file"""
        return self._variables


##################################################################################################
########################################### EXCEPTIONS ###########################################
##################################################################################################


class EmbedOpsException(Exception):
    """Base class for all EmbedOps exceptions"""

    def __init__(
        self, message="EmbedOps encountered an internal error", fix_message=""
    ):
        self.message = message
        self.fix_message = fix_message
        super().__init__(self.message)


############################################## YAML ##############################################


class UnsupportedYamlTypeException(EmbedOpsException):
    """Raised when an Unsupported YAML type is input"""

    ERROR_MSG = "CI configuration YAML file is not one of the supported filenames\n"
    ERROR_FIX = (
        "Make sure one of the following CI configuration files is in the current directory:\n"
        "    " + "\n    ".join(SUPPORTED_CI_FILENAMES) + "\n"
        "\nNOTE: The GitHub CI configuration file should be in the .github/workflows directory"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NoYamlFileException(EmbedOpsException):
    """Raised when no YAML file is found"""

    ERROR_MSG = "CI configuration YAML file could not be found\n"
    ERROR_FIX = (
        "Either specify a filename with the --filename option or make sure\n"
        "one of the following CI configuration files is in the current directory:\n"
        "    " + "\n    ".join(SUPPORTED_CI_FILENAMES) + "\n"
        "\nNOTE: The GitHub CI configuration file should be in the .github/workflows directory"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class BadYamlFileException(EmbedOpsException):
    """Raised when a bad YAML file is found"""

    ERROR_MSG = "CI configuration YAML file could not be parsed\n"
    ERROR_FIX = (
        "Check your YAML for syntax errors. \n"
        "Email support@embedops.io if you have questions."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class MultipleYamlFilesException(EmbedOpsException):
    """Raised when multiple YAML files are found"""

    ERROR_MSG = "Multiple CI configuration files were found.\n"
    ERROR_FIX = (
        "Please specify the desired CI configuration file by using the --filename flag.\n\n"
        "Syntax: embedops-cli jobs --filename <PATH_TO_CI_CONFIG_FILE> run <JOB_NAME>"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


######################################### Authorization ##########################################


class UnauthorizedUserException(EmbedOpsException):
    """Raised when there is no Authorization Token found in the user's secrets file"""

    ERROR_MSG = "No EmbedOps credentials found\n"

    ERROR_FIX = (
        "EmbedOps CLI is even better with an account!\n"
        "If you do not have an account and would like to learn more about EmbedOps, "
        "contact support@embedops.io"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class LoginFailureException(EmbedOpsException):
    """Raised when logging into the Embedops backend fails"""

    ERROR_MSG = "A problem was encountered while logging into EmbedOps.\n"

    ERROR_FIX = (
        "Check your credentials on app.embedops.io and try again.\n"
        "If you encounter further issues, please contact support:\n"
        "support@embedops.io"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


############################################# Docker #############################################


class NoDockerContainerException(EmbedOpsException):
    """Raised when no Docker container is found in the CI configuration file"""

    ERROR_MSG = (
        "Docker container is not found in the job or in the CI configuration file.\n"
    )
    ERROR_FIX = (
        "A Docker container must be provided to run a job.\n\n"
        "For GitLab CI, use the `image` keyword.\n"
        "It can be used as part of a job, in the `default` section, or globally.\n\n"
        "For GitHub CI, use the `container` keyword.\n"
        "It can only be used as part of a job."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class InvalidDockerContainerException(EmbedOpsException):
    """Raised when an invalid Docker container is detected"""

    ERROR_MSG = "Docker container is invalid.\n"
    ERROR_FIX = (
        "If your Docker container is hosted on a private registry,\n"
        "do not include http:// in your Docker container link."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerNotRunningException(EmbedOpsException):
    """Raised when the Docker daemon is not running"""

    ERROR_MSG = "Docker is not running\n"
    ERROR_FIX = (
        "Start or restart Docker desktop. \n"
        "Look for the whale logo in your system status tray\n"
        'and check that it says "Docker Desktop running"'
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerRegistryException(EmbedOpsException):
    """Raised when a problem accessing the registry is encountered"""

    ERROR_MSG = (
        "We were unable to authenticate with the package registry, "
        "or the image name is not correct.\n"
    )
    ERROR_FIX = (
        "To access the required Docker images needed run this job,\n"
        "login to the EmbedOps Docker registry using this command:\n"
        "\n"
        "    docker login registry.embedops.com\n"
        "\n"
        "When prompted, login with your access token, found on app.embedops.io\n"
        "Check in registry that the image name exists."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class UnknownDockerException(EmbedOpsException):
    """Raised when an error with Docker is encountered that we haven't otherwise handled"""

    ERROR_MSG = (
        "No clue what happened, but Docker didn't run.\n  Here there be dragons. \n"
    )
    ERROR_FIX = (
        "Turn everything off and on again.\n"
        "Then, if it's still broken, file a bug report with Dojo Five:\n"
        "support@embedops.io"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)
