class BuildPack:
    def __init__(
        self,
        type,
        ignorePatterns,
        docker,
        dependency=None,
        preBuildScript=None,
        local=None,
        **kwargs,
    ):
        self.type = type
        self.ignore_patterns = ignorePatterns
        self.docker = Docker(**docker)
        if dependency:
            self.dependency = Dependency(**dependency)
        self.pre_build_script = preBuildScript
        if local:
            self.local = Local(**local)


class Local:
    def __init__(self, requirementFiles, runCommand, **kwargs):
        self.run_command = runCommand
        self.requirement_files = requirementFiles


class Dependency:
    def __init__(self, autoUpdate, **kwargs):
        self.auto_update = autoUpdate


class Docker:
    def __init__(self, fileName, overwrite, dockerFileContent=None, **kwargs):
        self.docker_file_content = dockerFileContent
        self.file_name = fileName
        self.overwrite = overwrite
