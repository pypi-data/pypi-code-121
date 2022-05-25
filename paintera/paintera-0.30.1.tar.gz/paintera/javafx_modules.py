import os
import pathlib
import sys

from jgo import jgo

from paintera import version

_paintera_endpoint = f'org.janelia.saalfeldlab:paintera:{version._paintera_version.maven_version()}'

_classpath_separator = ':' if sys.platform != 'win32' else ';'
_javafx_platform_map = {
    "linux": "linux",
    "linux2": "linux",
    "win32": "win",
    "darwin": "mac"
}

_javafx_version = "16"
_modules_and_opens = {
    "javafx.base": [
        'javafx.util',
        'javafx.event',
        'javafx.beans.property',
        'com.sun.javafx.binding',
        'com.sun.javafx.event',
    ],
    "javafx.controls": [],
    "javafx.fxml": [],
    "javafx.media": [],
    "javafx.swing": [],
    "javafx.web": [],
    "javafx.graphics": [
        "javafx.scene",
        "javafx.stage",
        "javafx.geometry",
        "javafx.animation",
        "javafx.scene.input",
        "javafx.scene.image",
        "com.sun.prism",
        "com.sun.prism.paint",
        "com.sun.javafx.application",
        "com.sun.javafx.geom",
        "com.sun.javafx.image",
        "com.sun.javafx.scene",
        "com.sun.javafx.stage",
        "com.sun.javafx.perf",
        "com.sun.javafx.cursor",
        "com.sun.javafx.tk",
        "com.sun.javafx.scene.traversal",
        "com.sun.javafx.geom.transform",
        "com.sun.scenario.animation",
        "com.sun.scenario.animation.shared",
        "com.sun.scenario.effect",
        "com.sun.javafx.sg.prism",
    ]
}


def _get_jgo_cache_dir():
    config = jgo.default_config()
    if not '--ignore-jgorc' in sys.argv:
        config_file = pathlib.Path.home() / '.jgorc'
        config.read(config_file)

    if os.getenv(jgo.jgo_cache_dir_environment_variable()) is not None:
        cache_dir = os.getenv(jgo.jgo_cache_dir_environment_variable())
        config.set('settings', 'cacheDir', cache_dir)
    return config['settings'].get('cacheDir')


def _javafx_module_path():
    """
    We need to determine where jgo copies the jar dependencies to, then build out module-path from that.
    We grab the endpoint we pass to jgo, then call jgo's internal methods for determining the workspace.
    After that, we determine the javafx dependencies we need to add the module-path. For each dependency
     there is a "common" jar, as a well as a platform specific jar.

    :return: the module-path which points to the javafx module dependencies
    """
    # Determine the location of the jgo-discovered dependencies
    endpoints = jgo.endpoints_from_strings([_paintera_endpoint])
    coordinates = jgo.coordinates_from_endpoints(endpoints)
    cache_dir = _get_jgo_cache_dir()
    workspace = jgo.workspace_dir_from_coordinates(coordinates, cache_dir=cache_dir)
    relative_module_paths = []
    for module in _modules_and_opens.keys():
        # generate a list of the dependencies we should expect to find.
        module_path_name = module.replace(".", "-")
        shared_prefix = f"{module_path_name}-{_javafx_version}"
        common_module = f"{shared_prefix}.jar"
        platform_specific_module = f"{shared_prefix}-{_javafx_platform_map[sys.platform]}.jar"
        relative_module_paths.append(platform_specific_module),
        relative_module_paths.append(common_module)
    # create the module path
    absolute_module_paths = (f"{workspace}/{x}" for x in relative_module_paths)
    module_path = _classpath_separator.join(absolute_module_paths)
    return module_path


# Allow access to classes that are not exported (currently needed)
javafx_args = ["--illegal-access=permit"]

# for each class we use, open it to ALL-UNNAMED, which contains Paintera,
#   since it isn't utilizing the module system currently
for module_name, packages_to_open in _modules_and_opens.items():
    for package in packages_to_open:
        javafx_args.append(f"--add-opens={module_name}/{package}=ALL-UNNAMED")

# add the module path for the javafx modules
javafx_args.extend(["--module-path", _javafx_module_path()])
# specify which modules we actually use.
javafx_args.extend(["--add-modules", ",".join(_modules_and_opens.keys())])
