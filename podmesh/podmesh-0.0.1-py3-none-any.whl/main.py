import pluggy
from podmesh import hookspecs, PodMesh
from podmesh.plugins import podman as podmesh_podman
from time import sleep
import argparse


def main(args):
    if args.debugging:
        import debugpy
        # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
        debugpy.listen(5678)
        print("Waiting for debugger attach")
        debugpy.wait_for_client()
        print("Attached")

    plugin_manager = get_plugin_manager()
    plugin_manager.register(podmesh_podman)
    podmesh = PodMesh(plugin_manager.hook)

    podmesh.ready()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting")

    podmesh.exit()


def get_plugin_manager():
    plugin_manager = pluggy.PluginManager("podmesh")
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints("podmesh")
    return plugin_manager


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debugging", action="store_true")
    args = parser.parse_args()
    main(args)
