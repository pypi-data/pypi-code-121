# params.py
import os, yaml
import boakboak.src.settings as sts


class Params:
    def __init__(self):
        # if the yml file is found inside the app folder appDefault == True else False
        self.appDefault = False
        self.params = {}
        self.extParams = {}

    def get_params(
        self,
        apps: list,
        *args,
        appsParamsDir: str = sts.appsParamsDir,
        **kwargs,
    ) -> dict:
        # getting runtime parameters and returning them
        # takes apps name and returns a list of dictionaries
        try:
            for app in apps:
                appsParamsDir, fileName = self.find_params(app, appsParamsDir)
                with open(os.path.join(appsParamsDir, fileName)) as f:
                    self.params.update({app: yaml.safe_load(f)})
                if self.appDefault:
                    self.params = self.get_ext_cmds(appsParamsDir, app)
                self.params[app].update({"appsParamsDir": appsParamsDir})
                self.params[app].update({"app": app})
                if self.params[app]["appPath"] in sts.appPathAliass:
                    self.params[app]["appPath"] = appsParamsDir
        except Exception as e:
            print(f"{sts.exceptionMsg}, {e = }")
            exit()
        return self.params

    def get_ext_cmds(self, appsParamsDir: str, app: str) -> dict[dict, str]:
        """
        boakboak can take cmds from another file i.e. .gitlab-ci.yml
        this will read the external params path from the cmds key in .yml
        p[0] will be the fileName p[1] ... is the path to cmds
        see also README.md
        """
        cmds = self.params[app].get("cmds")
        if type(cmds) == str:
            p = cmds.replace(" ", "").split(",")
            with open(os.path.join(appsParamsDir, f"{p[0]}{sts.paramsFileExt}")) as f:
                self.extParams.update({app: yaml.safe_load(f)})
            self.params[app]["cmds"] = self.extParams[app].get(p[1]).get(p[2])[0].split()
        return self.params

    def find_params(self, app: str, appsParamsDir) -> str:
        """
        takes a param directory and checks if the fileName exsits as a file within
        the directory, if it exsits it returns both the directory and the fileName
        if fileName is not found, it tries to fine the fileName within the app itself
        this should look like: ./appName/appName.yml
        """
        fileName = f"{app}{sts.paramsFileExt}"
        filePath = os.path.join(appsParamsDir, fileName)
        if not os.path.isfile(filePath):
            appsParamsDir, app = self.find_app_path(app)
            self.appDefault = True
            fileName = f"{app}{sts.paramsFileExt}"
        return appsParamsDir, fileName

    def find_app_path(self, app: str, *args, **kwargs) -> tuple[str]:
        """
        searches for the params file within the file structure of the target app itself
        the app could be at any location wihtin the target apps main directory
        this should look like: ./appName/appName.yml
        """
        for _dir, dirs, files in os.walk(os.getcwd()):
            paramsFile = os.path.join(_dir, f"{app}{sts.paramsFileExt}")
            if (os.path.basename(_dir) == app) and os.path.isfile(paramsFile):
                return _dir, sts.defaultName
            elif app in dirs:
                paramsPath = sts.os_sep(os.path.join(_dir, app))
                prramsFile = os.path.join(paramsPath, f"{sts.defaultName}{sts.paramsFileExt}")
                if os.path.isfile(paramsFile):
                    return paramsPath, sts.defaultName
        else:
            raise Exception(f"\n{app} was not found in {os.getcwd()}")

    def get_all_apps(
        self, app: str, *args, appsParamsDir: str = sts.appsParamsDir, **kwargs
    ) -> list[str]:
        """
        when the user provides * instead of app name,
        all apps are loaded from apps directory
        """
        if app == sts.allApps:
            apps = [f[:-4] for f in os.listdir(appsParamsDir) if f.endswith(sts.paramsFileExt)]
            assert apps, f"apps not found: {app}"
        else:
            apps = [f"{app}"]
        return apps
