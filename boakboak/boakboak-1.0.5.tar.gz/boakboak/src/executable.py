import errno, inspect, os, sys, yaml
import boakboak.src.settings as sts


class Executable:
    def __init__(self, alias, *args, appPath, executable: str = None, **kwargs):
        self.alias = alias
        self.executable = executable
        self.osSepAdj = lambda x: x.replace("/", os.sep)
        self.appPath = appPath

    def get_executable(self, *args, **kwargs):
        """
        gets the executable from a project or package and returns it
        also checks if project is a package or not (packages are then called differently)
        """
        # simple modules are called from inside the project, packages from one level above
        self.isPackage = os.path.isfile(
            os.path.join(self.appPath, sts.packageIndicator)
        )
        if self.executable is None or not os.path.isfile(self.executable):
            activatorPath = self.find_venv(self.appPath, **kwargs)
            # if a .venv file is found use executable form that file
            if activatorPath.endswith(sts.activators[0]):
                self.executable = self.exec_from_dot_venv(
                    activatorPath, *args, **kwargs
                )
            # if a Pipfile is found, trace executable location by name
            elif activatorPath.endswith(sts.activators[1]):
                self.executable = self.exec_from_pipfile(
                    activatorPath, self.appPath, *args, **kwargs
                )
            # check if valid executable was found
            self.executable = self.osSepAdj(self.executable)
            if not self.executable.endswith(
                self.osSepAdj(sts.venvsPaths[os.name][1])
            ):
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), self.executable
                )
            self.exec_write_to_yaml(*args, **kwargs)
        return self.executable, self.isPackage

    def exec_write_to_yaml(
        self,
        *args,
        app: str,
        paramsFileExt: str = ".yml",
        appsParamsDir: str = sts.appsParamsDir,
        **kwargs
    ):
        appsParamsPath = os.path.join(appsParamsDir, self.alias + paramsFileExt)
        with open(appsParamsPath, "r") as f:
            params = yaml.safe_load(f)
        params["executable"] = self.executable
        # file extension is .yml
        with open(appsParamsPath, "w") as f:
            f.write(yaml.dump(params))

    def exec_from_dot_venv(self, activatorPath, *args, **kwargs):
        # pipenv uses .venv files which hold path to executable. This returns that path.
        if os.path.isfile(activatorPath):
            with open(activatorPath, "r") as f:
                venvPath = f.read().strip()
        else:
            venvPath = os.path.join(activatorPath)
        if not venvPath.endswith(sts.venvsPaths[os.name][1][-10:]):
            venvPath = os.path.join(venvPath, sts.venvsPaths[os.name][1])
        return venvPath

    def exec_from_pipfile(self, activatorPath, *args, **kwargs):
        # if a Pipfile is found, then there should be a similarily named environment
        # the path to the executable from that environment is returned
        venvsPath = os.path.join(
            os.path.expanduser("~"), sts.venvsPaths[os.name][0]
        )
        # pipenvs directories start with the name of the folder in which they where created
        projectName = os.path.split(self.appPath)[-1]
        venvDirs = [
            d for d in os.listdir(venvsPath) if d.startswith(projectName)
        ]
        if venvDirs:
            # if a matching direcory exists, then return the executable from the path
            return os.path.join(
                venvsPath, venvDirs[0], sts.venvsPaths[os.name][1]
            )
        else:
            return "not found"

    def find_venv(self, *args, **kwargs):
        """
        walks throu all folders of a project until it finds a .venv or Pipflie
        returns the path to .venv or Pipfile
        this can then be used to find the executable for the project
        """
        for activator in sts.activators:
            for d, ds, fs in os.walk(self.appPath):
                for f in fs:
                    if f == activator:
                        activatorPath = os.path.join(d, f)
                        return activatorPath
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), sts.activators
            )
