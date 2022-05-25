import subprocess

import jgo.util
import os
import pathlib
import sys

from paintera import version
from paintera.javafx_modules import javafx_args

_paintera                = '@Paintera'
_paintera_show_container = '@PainteraShowContainer'
_picocli_autocomplete    = 'picocli.AutoComplete'
_paintera_cli_args       = 'org.janelia.saalfeldlab.paintera.PainteraCommandLineArgs'
_groupId                 = 'org.janelia.saalfeldlab'
_artifactId              = 'paintera'

def _get_paintera_version(argv=None):
    import argparse
    argv = sys.argv[1:] if argv is None else argv
    if ('--' in argv):

        def version_from_string(string):
            split = string.split('.')
            try:
                major, minor, patch = [int(s) for s in split[:3]]
                tag = ''
            except:
                major, minor = [int(s) for s in split[:2]]
                patch = int(split[2].split('-')[0])
                tag = 'SNAPSHOT'
            return version._Version(major, minor, patch, tag)

        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS)
        parser.add_argument('--use-version', type=version_from_string)
        args, unknown = parser.parse_known_args(argv)
        return version._paintera_version if args.use_version is None else args.use_version, unknown

    else:
        return version._paintera_version, argv


def prepend_required_default_args(argv):
    # Start with the manual scaling args, to support HiDPI scaling on linus
    additional_args = manual_scaling_args()
    # Add args to ensure GPU is always used (and required)
    additional_args.append("-Dprism.forceGPU=true")
    # Add the javafx arguments, if not previously set
    if "--module-path" not in argv:
        additional_args.extend(javafx_args)
    # Append the arg separator if not present.
    if '--' not in argv:
        additional_args.append('--')
    return additional_args + argv

def launch_paintera():
    paintera_version, argv = _get_paintera_version(argv=sys.argv[1:])
    final_args = prepend_required_default_args(argv)
    return jgo.util.main_from_endpoint(
        argv=final_args,
        primary_endpoint=f'{_groupId}:{_artifactId}',
        primary_endpoint_version=paintera_version.maven_version(),
        primary_endpoint_main_class=_paintera)


def manual_scaling_args():
    """
    This determines and provides the appropriate scaling properties for javafx on hi-dpi monitors, when running linux.
    This will only impact scaling when using Mutter (default for GNOME 3 )

    :return: list additional javafx properties which override application scaling
    """
    if 'linux' in sys.platform:
        scale = dbus_request_mutter_screen_scale_factor()
        if (scale == None or len(scale) == 0):
            #  If there request doesn't work, don't attempt to override scaling. Paintera should work,
            #   though the resolution may not match the system's display configuration.
            return []
        return ["-Dprism.allowhidpi=true", f"-Dglass.gtk.uiScale={scale}"]
    else:
        return []


def dbus_request_mutter_screen_scale_factor():
    """
    Queries the Mutter DisplayConfig API via dbus to determine the current scale factor.

    :return: the current scale factor used by the Mutter display manager on linux
    """
    dbus_name = 'org.gnome.Mutter.DisplayConfig'
    message_name = f"{dbus_name}.GetCurrentState"
    dest_obj_path = '/org/gnome/Mutter/DisplayConfig'
    return subprocess.run(
        f"dbus-send --print-reply --dest={dbus_name} {dest_obj_path} {message_name} | grep -i scaling-factor -A 1 | grep int32 " + "| awk '{print $3}'",
        capture_output=True, text=True, shell=True).stdout.strip()


def generate_paintera_bash_completion():
    relative_path = os.path.join(
        'share',
        'bash-completion',
        'completions',
        'paintera')
    default_path = os.path.join('$PREFIX', relative_path)
    description=f'''Generate bash completion file for Paintera. This script uses picocli[1] to create a script file for bash-completion[2]. The default output location is {default_path} and can be modified with the --prefix option or overwritten entirely with the --output option.

[1] https://picocli.info
[2] https://github.com/scop/bash-completion
'''
    import argparse
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    default_prefix = os.getenv('PREFIX', os.path.abspath(os.path.join(os.sep, 'usr')))
    parser.add_argument('--prefix', required=False, default=default_prefix, help='Sets the PREFIX for the output location. Is ignored if --output is set.')
    parser.add_argument('--output', required=False, default=None, help='Specifies the output location explicitly (PREFIX and --prefix are ignored)')

    argv = sys.argv[1:]

    try:
        double_dash_index = argv.index('--')
    except ValueError:
        double_dash_index = -1

    if double_dash_index > 0 and double_dash_index < len(argv):
        jgo_argv = argv[:double_dash_index + 1]
        argv     = argv[double_dash_index + 1:]
    else:
        jgo_argv = []

    args = parser.parse_args(args=argv)

    output = os.path.join(args.prefix, relative_path) if args.output is None else args.output

    argv = [
        '-n', 'paintera',
        'org.janelia.saalfeldlab.paintera.PainteraCommandLineArgs',
        '-o', output]

    pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)

    return jgo.util.main_from_endpoint(
        primary_endpoint            = f'{_groupId}:{_artifactId}',
        argv                        = jgo_argv + argv,
        primary_endpoint_version    = version._paintera_version.maven_version(),
        primary_endpoint_main_class = _picocli_autocomplete)

if __name__ == '__main__':
    launch_paintera()