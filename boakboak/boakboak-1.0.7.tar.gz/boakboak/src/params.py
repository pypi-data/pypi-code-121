# params.py
import os, yaml
import boakboak.src.settings as sts


class Params:
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
            params = {}
            for app in apps:
                appsParamsDir, fileName = self.find_params(app, appsParamsDir)
                with open(os.path.join(appsParamsDir, fileName)) as f:
                    params.update({app: yaml.safe_load(f)})
                params[app].update({"appsParamsDir": appsParamsDir})
                params[app].update({"app": app})
                if params[app]["appPath"] in sts.appPathAliass:
                    params[app]["appPath"] = appsParamsDir
        except Exception as e:
            print(f"{sts.exceptionMsg}, {e = }")
            exit()
        return params

    def find_params(self, app: str, appsParamsDir) -> str:
        fileName = f"{app}{sts.paramsFileExt}"
        filePath = os.path.join(appsParamsDir, fileName)
        if not os.path.isfile(filePath):
            appsParamsDir, app = self.find_app_path(app)
            fileName = f"{app}{sts.paramsFileExt}"
        return appsParamsDir, fileName

    def find_app_path(self, app: str, *args, **kwargs) -> tuple[str]:
        """
        if app is not found, it the app directory is searched for
        """
        for _dir, dirs, files in os.walk(os.getcwd()):
            paramsFile = os.path.join(_dir, f"{sts.defaultName}{sts.paramsFileExt}")
            if (os.path.basename(_dir) == app) and os.path.isfile(paramsFile):
                return _dir, sts.defaultName
            elif app in dirs:
                paramsPath = sts.os_sep_adj(os.path.join(_dir, app))
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
