"""
Manage environment variables for both Windows and Linux render nodes.
"""

class PackageEnvironment(object):


    def __init__(self, env_list=None, platform=None):
        """
        Create a list of environment variables.

        Typically, one would initialize a PackageEnvironment with a package, and then modify by
        adding more packages or lists of variables. Extra variables can be added by the customer, or
        programmatically such as during asset scraping.

        Keyword Arguments:

        * **`env_list`** -- Either a Package that contains an "environment" property, or a list of
          environment objects. -- Defaults to `None`.
        * **`platform`** -- If env_list is not a package, then the platform must be provided. --
          Defaults to `None`.

        On instantiation, delegete args to the [extend()](#extend) method.

        """
        self.platform = None
        self._env = {}
       
        self.extend(env_list, platform)


    def extend(self, env_list, platform=None):
        """
        Extend the Package environment with the given variable specifications.

        Arguments:

        * **`env_list`** --  Either:
        1. A list of dictionaries with properties: `name`, `value`, and `merge_policy`.
        2. An object with an `environment` key that contains a list of the dictionaries described
           above. The latter is the structure of a package. Therefore we can initialize or extend a
           PackageEnvironment with a package.


        Keyword Arguments:

        * **`platform`** -- Defaults to `None`.
            If env_list is a package, then the platform is taken from the package and the `platform`
            keyword is ignored. If env_list is a list, then if this is the first add, a platform
            should be specified, otherwise it willl default to linux.
        
        The first time data is added to a PackageEnvironment, the platform is set in stone.
        Subsequent `adds` that try to change the platform are considered an error.

        Each variable to be added specifies a merge_policy: `append` or `exclusive`. Once an
        individual variable has been initialized with a merge policy, it can't be changed. This
        means: 1. It's not possible to overwrite variables that have been set as append. 2.
        Exclusive variables are always overwritten by subsequent adds.

        Raises:

        * **`ValueError`** -- Attempt to change the platform once initialized.
        * **`ValueError`** -- Unknown merge policy
        .

        ???+ example
            ``` python

            from ciocore import api_client, package_tree, package_environment
            packages = api_client.request_software_packages()
            pt = package_tree.PackageTree(packages, product="cinema4d")
            one_dcc_name = pt.supported_host_names()[0]
            # 'cinema4d 21.209.RB305619 linux'
            pkg = pt.find_by_name(one_dcc_name)
            pe = package_environment.PackageEnvironment(pkg)
            print(dict(pe))

            # Result:
            # {
            # "PATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin",
            # "g_licenseServerRLM": "conductor-rlm:6112",
            # "LD_LIBRARY_PATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/lib64:/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/python/libs/linux64/python.linux64.framework/lib64:/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/embree.module/libs/linux64",
            # "PYTHONPATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/python/libs/linux64/python.linux64.framework/lib64/python2.7/lib-dynload",
            # }

            extra_env = [
                {"name":"PATH", "value": "/my/custom/scripts", "merge_policy":"append"},
                {"name":"DEBUG_MODE", "value": "1", "merge_policy":"exclusive"}
            ]

            pe.extend(extra_env)
            print(dict(pe))

            # Result:
            # {
            #     "PATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin:/my/custom/scripts",
            #     "g_licenseServerRLM": "conductor-rlm:6112",
            #     "LD_LIBRARY_PATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/lib64:/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/python/libs/linux64/python.linux64.framework/lib64:/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/embree.module/libs/linux64",
            #     "PYTHONPATH": "/opt/maxon/cinema4d/21/cinema4d21.209vRB305619/bin/resource/modules/python/libs/linux64/python.linux64.framework/lib64/python2.7/lib-dynload",
            #     "DEBUG_MODE": "1",
            # }
            ```
        """

        if not env_list:
            return

        try:
            others = env_list["environment"]
            requested_platform = env_list.get("platform")
        except TypeError:
            others = env_list
            requested_platform = platform

        if not self.platform:
            self.platform = requested_platform or "linux"
        elif requested_platform and requested_platform != self.platform:
            raise ValueError("Can't change platform once initialized.")

        for var in others:
            name = var["name"]
            value = var["value"]
            policy = var["merge_policy"]
            if policy not in ["append", "exclusive"]:
                raise ValueError("Unexpected merge policy: %s" % policy)

            if policy == "append":
                self._append(name, value)
            else:
                self._set(name, value)


    def _set(self, name, value):
        """Set the value of an exclusive variable.

        Can be overwritten by subsequent adds.

        It is an error if the variable has already been declared with policy=append.
        """
        if self._env.get(name) and isinstance(self._env[name], list):
            raise ValueError(
                "Can't change merge policy for '{}' from 'append' to 'exclusive'.".format(name)
            )
        self._env[name] = value

    def _append(self, name, value):
        """Set the value of an append variable.

        Can be appended to with subsequent adds.

        It is an error if the variable has already been declared with policy=exclusive.
        """
        if self._env.get(name):
            if not isinstance(self._env[name], list):
                raise ValueError(
                    "Can't change merge policy for '{}' from 'exclusive' to 'append'.".format(name)
                )
        else:
            self._env[name] = []
        self._env[name].append(value)

    def __iter__(self):
        """Cast the object as a dict."""
        sep = ";" if self.platform == "windows" else ":"
        for key in self._env:
            var = self._env[key]
            if isinstance(var, list):
                yield key, sep.join(var)
            else:
                yield key, var

    def __getitem__(self, key):
        """Allow access by key."""
        sep = ";" if self.platform == "windows" else ":"
        var = self._env.__getitem__(key)
        if isinstance(var, list):
            return sep.join(var)
        return var
