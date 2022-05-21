from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from struct import Struct
from typing import Iterator, Tuple, List, Optional, Dict, IO, Callable

from pkm.api.versions.version import StandardVersion
from pkm.config.configuration import Configuration
from pkm.utils.files import temp_dir
from pkm.utils.properties import cached_property
from pkm.utils.sequences import index_of_or_none
from pkm.utils.types import HasLessThan, Comparable

_INTROSPECTION_CODE = """
import sys
import sysconfig
import json
import importlib.machinery
import platform
import os
import site
import struct

if hasattr(sys, 'implementation'):
    sys_implementation = {'name': sys.implementation.name, 'version': sys.implementation.version}
else:
    sys_implementation = {'name': platform.python_implementation().lower()}

result = {
    'sysconfig': {
        'paths': sysconfig.get_paths(),
        'paths_by_scheme': {s:sysconfig.get_paths(s) for s in sysconfig.get_scheme_names()},
        'vars': sysconfig.get_config_vars(),
        'platform': sysconfig.get_platform(),
        'is_python_build': sysconfig.is_python_build(True)
    },

    'sys': {
        'implementation': sys_implementation,
         'version_info': sys.version_info,
         'has_totalrefcount': hasattr(sys,'gettotalrefcount'),
         'maxunicode': sys.maxunicode,
         'maxsize': sys.maxsize,
         'executable': sys.executable,
         'platform': sys.platform
    },

    'importlib': {
        'machinery': {
            'EXTENSION_SUFFIXES': importlib.machinery.EXTENSION_SUFFIXES
        }
    },

    'platform': {
        'system': platform.system(),
        'mac_ver': platform.mac_ver(),
        'machine': platform.machine(),
        'python_implementation': platform.python_implementation(),
        'release': platform.release(),
        'version': platform.version(),
        'python_version_tuple': platform.python_version_tuple(),
        'python_version': platform.python_version()
    },

    'os': {
        'conf': {cname: os.confstr(cname) for cname in getattr(os,'confstr_names',[])},
        'name': os.name,
        'bits': struct.calcsize('P') * 8 
    },
    
    'site': {
        'packages': site.getsitepackages()
    }
}

print(json.dumps(result))
"""

_USER_SCHEME_BY_PLATFORM = {
    "Linux": "posix_user",
    "Windows": "nt_user",
    "Darwin": "osx_framework_user"
}


# noinspection PyRedundantParentheses
class EnvironmentIntrospection(Configuration):

    @property
    def paths(self) -> Dict[str, str]:
        return self._data['sysconfig']['paths']

    def is_windows_env(self) -> bool:
        return self['sys']['platform'] == 'win32'

    def user_paths(self) -> Optional[Dict[str, str]]:
        scheme = _USER_SCHEME_BY_PLATFORM.get(self._data["platform"]["system"])
        if not scheme:
            return None

        return self._data["sysconfig"]["paths_by_scheme"].get(scheme)

    def compute_markers(self) -> Dict[str, str]:
        """
        :return: pep508 environment markers
        """

        def _compute_implementation_version():
            if info := self._data['sys']['implementation'].get('version'):
                version = '.'.join(str(it) for it in info[:3])
                kind = info[3]
                if kind != 'final':
                    version += kind[0] + str(info[4])

                return version
            return "0"

        return {
            "os_name": self._data['os']['name'],
            "sys_platform": self._data['sys']['platform'],
            "platform_machine": self._data['platform']['machine'],
            "platform_python_implementation": self._data['platform']['python_implementation'],
            "platform_release": self._data['platform']['release'],
            "platform_system": self._data['platform']['system'],
            "platform_version": self._data['platform']['version'],
            "python_version": '.'.join(self._data['platform']['python_version_tuple'][:2]),
            "python_full_version": self._data['platform']['python_version'],
            "implementation_name": self._data['sys']['implementation']['name'],
            "implementation_version": _compute_implementation_version()
        }

    def compatibility_score(self, tag: str) -> Optional[Comparable]:
        """
        compute the compatibility score for the given pep425 compatibility tag
        :param tag: the pep425 compatibility tag
        :return: an opaque score object that support __le__ and __eq__ operations (read: comparable)
                 which can be treated as a score (read: higher is better)
        """
        try:
            max_score = None
            interpreters, abis, platforms = tag.split("-")
            for interpreter in interpreters.split("."):
                for abi in abis.split("."):
                    for platform_ in platforms.split("."):
                        score = self._compatibility_tag_scorer(interpreter, abi, platform_)

                        if score is not None and (max_score is None or max_score < score):
                            max_score = score
            return max_score
        except:  # noqa
            import traceback
            traceback.print_exc()
            return None

    @property
    def interpreter_name(self) -> str:
        """
        :return: the name of the interpreter as given in `sys.implementation.name`
        """
        iname = self._data['sys']['implementation']['name']
        return INTERPRETER_SHORT_NAMES.get(iname, iname)

    @property
    def interpreter_path(self) -> str:
        return self._data['sys']['executable']

    @property
    def interpreter_version(self) -> List[int]:
        return self._data['sys']['version_info']

    def _compute_generic_abis(self) -> Iterator[str]:
        if abi := self._data['sysconfig']['vars'].get("SOABI"):
            yield _normalize_string(abi)

    @property
    def is_32bit_interpreter(self):
        return self._data['sys']['maxsize'] <= 2 ** 32

    @cached_property
    def _glibc_version(self) -> Optional[StandardVersion]:
        # this is correct that the pkm's os and the actual os that will execute this
        # script should be the same but this is a future proofing for venvs in dockers
        # which is a use case pkm might end up supporting
        version_string = self._data['os']['conf'].get('CS_GNU_LIBC_VERSION')
        if not version_string:
            return None

        try:
            # os.confstr("CS_GNU_LIBC_VERSION") returns a string like "glibc 2.17".
            return StandardVersion.parse(version_string.split()[1])
        except ValueError:
            return None

    def _compute_cpython_abis(self, py_version: Tuple[int, ...]) -> List[str]:
        abis = []
        version = ''.join(str(v) for v in py_version)
        debug = pymalloc = ucs4 = ""
        with_debug = self._data['sysconfig']['vars'].get("Py_DEBUG")
        has_refcount = self._data['sys']['has_totalrefcount']
        # Windows doesn't set Py_DEBUG, so checking for support of debug-compiled
        # extension modules is the best option.
        # https://github.com/pypa/pip/issues/3383#issuecomment-173267692
        has_ext = "_d.pyd" in self._data['importlib']['machinery']['EXTENSION_SUFFIXES']
        if with_debug or (with_debug is None and (has_refcount or has_ext)):
            debug = "d"
        if py_version < (3, 8):
            with_pymalloc = self._data['sysconfig']['vars'].get("WITH_PYMALLOC")
            if with_pymalloc or with_pymalloc is None:
                pymalloc = "m"
            if py_version < (3, 3):
                unicode_size = self._data['sysconfig']['vars'].get("Py_UNICODE_SIZE")
                if unicode_size == 4 or (
                        unicode_size is None and self._data['sys']['maxunicode'] == 0x10FFFF
                ):
                    ucs4 = "u"
        elif debug:
            # Debug builds can also load "normal" extension modules.
            # We can also assume no UCS-4 or pymalloc requirement.
            abis.append(f"cp{version}")
        abis.insert(0, f"cp{version}{debug}{pymalloc}{ucs4}", )
        return abis

    @cached_property
    def _compatibility_tag_scorer(self) -> Callable[[str, str, str], Optional[HasLessThan]]:

        # some of the code for compatibility tags scoring is based on `packaging::tags` module
        # but instead of output list of tags which requires us to know external information about the version history of
        # gcc, mac, musl, etc. it creates a score function that given a tag will score it so that
        # the user can sort given this score and choose the preferable distribution

        # first we will precompute anything possible:

        my_ipt = self.interpreter_name
        version_rx = re.compile("[\\d_]+")
        my_ipt_version = tuple(self.interpreter_version[:2])
        if len(my_ipt_version) < 2:
            my_ipt_version += (0,)

        if my_ipt == 'cp':
            my_abis = self._compute_cpython_abis(my_ipt_version) if len(my_ipt_version) > 1 else []
            if _abi3_applies(my_ipt_version):
                my_abis.append('abi3')
        else:
            my_abis = list(self._compute_generic_abis())
        my_abis.append('none')
        my_abis.reverse()

        my_platform_type = self._data['platform']['system']
        my_platform = _normalize_string(self._data['sysconfig']['platform'])

        if my_platform_type == "Darwin":
            my_plat_version_str, _, my_cpu_arch = self._data['platform']['mac_ver']
            my_plat_version = tuple(int(it) for it in my_plat_version_str.split("."))[:2]
            my_arch = _mac_arch(my_cpu_arch, self.is_32bit_interpreter)
            my_plat_supported_binary_formats = _mac_binary_formats(my_plat_version, my_arch)
            if my_plat_version[0] >= 11 and my_arch != "x86_64":
                my_plat_supported_binary_formats.append('universal2')
            my_plat_supported_binary_formats.reverse()

            def darwin_score(plt: str) -> Optional[Tuple]:
                plt_components = plt.split('_', 3)
                if plt_components[0] != 'macosx':
                    return None
                _, vmajor_str, vminor_str, binary_format = plt_components
                plat_version = (int(vmajor_str), int(vminor_str))
                if plat_version > my_plat_version:
                    return None
                if (binary_format_index := index_of_or_none(my_plat_supported_binary_formats, binary_format)) is None:
                    return None
                return (binary_format_index + 1, *vdscore(my_plat_version, plat_version))

        elif my_platform_type == "Linux":
            my_linux = my_platform
            if self.is_32bit_interpreter:
                if my_platform == "linux_x86_64":
                    my_linux = "linux_i686"
                elif my_platform == "linux_aarch64":
                    my_linux = "linux_armv7l"

            _, my_arch = my_linux.split("_", 1)

            my_glibc_version = None
            my_musl_version = None
            if (elf := _ElfData.read(Path(self.interpreter_path))) and elf.have_compatible_abi(my_arch):
                my_glibc_version = self._glibc_version.release[:2]
                my_musl_version = elf.compute_musl_version()

            def linux_score(plt: str) -> Optional[Tuple]:
                plt_no_arch = plt[:-(len(my_arch) + 1)]

                if plt == my_linux:
                    return (1, 0, 0)

                if not plt.endswith(f"_{my_arch}"):
                    return None

                if plt_no_arch.startswith("manylinux"):
                    if my_glibc_version is not None:
                        legacy_glibc_version = _LEGACY_MANYLINUX_MAP.get(plt_no_arch)
                        glibc_version = legacy_glibc_version or tuple(int(it) for it in plt_no_arch.split("_")[1:3])
                        if len(glibc_version) != 2 or my_glibc_version < glibc_version:
                            return None
                        return (1, *vdscore(glibc_version, my_glibc_version))
                    return None

                if my_musl_version is not None and plt_no_arch.startswith("musllinux_"):
                    musl_ver = tuple(int(it) for it in plt_no_arch.split("_"))[1:3]
                    if len(musl_ver) != 2 or musl_ver[0] != my_musl_version[0] or musl_ver[1] > my_musl_version[1]:
                        return None
                    return (1, *vdscore(my_musl_version, musl_ver))

                return None

        def vdscore(v1: Tuple, v2: Tuple) -> Tuple:
            if v1[0] == v2[0]:
                return 1, 1 / (1 + abs(v1[1] - v2[1]))
            return 1 / (1 + abs(v1[0] - v2[0])), 0

        # precomputation done. now for creating the scorer

        def scorer(ipt: str, abi: str, plt: str) -> Optional[HasLessThan]:
            score_components = []

            # check abi compatibility
            if (abi_index := index_of_or_none(my_abis, abi)) is None:
                return None
            score_components.append(abi_index)

            # check platform
            # platform scores looks like:
            # (binary_format or os score , identifying_component_major_score, identifying_component_minor_score)
            if plt == 'any':
                score_components.extend((0, 0, 0))
            elif plt == my_platform:
                score_components.extend((1, 0, 0))
            elif my_platform_type == "Darwin":
                if (dscore := darwin_score(plt)) is None:
                    return None
                score_components.extend(dscore)
            elif my_platform_type == "Linux":
                if (lscore := linux_score(plt)) is None:
                    return None
                score_components.extend(lscore)
            else:
                return None

            # check compatible interpreter name
            if ipt.startswith('py') and version_rx.fullmatch(ipt[2:]):
                ipt_version_nodot_str = ipt[2:]
                score_components.append(0)
            elif ipt.startswith(my_ipt) and version_rx.fullmatch(ipt[len(my_ipt):]):
                ipt_version_nodot_str = ipt[len(my_ipt):]
                score_components.append(1)
            else:
                return None

            # check compatible interpreter version
            if len(ipt_version_nodot_str) == 1:
                ipt_version = (int(ipt_version_nodot_str), my_ipt_version[1])
            elif '_' in ipt_version_nodot_str:
                ipt_version = tuple(int(p) for p in ipt_version_nodot_str.split("_"))[:2]
            else:
                ipt_version = (int(ipt_version_nodot_str[0]), int(ipt_version_nodot_str[1:]))

            if my_ipt_version[0] != ipt_version[0] or my_ipt_version[1] < ipt_version[1]:
                return None

            score_components.append(vdscore(my_ipt_version, ipt_version)[1])

            return tuple(score_components)

        return scorer

    @classmethod
    def compute(cls, interpreter_path: Path) -> "EnvironmentIntrospection":
        with temp_dir() as tdir:
            intospection_script_path = tdir / 'introspect.py'
            intospection_script_path.write_text(_INTROSPECTION_CODE)

            proc_result = subprocess.run([str(interpreter_path.absolute()), str(intospection_script_path.absolute())],
                                         capture_output=True)
            proc_result.check_returncode()
            output = proc_result.stdout.decode()
            return cls(data=json.loads(output))

    @classmethod
    def load_or_compute(
            cls, path: Path, interpreter_path: Path,
            save_if_recomputed: bool = True) -> "EnvironmentIntrospection":

        data = json.loads(path.read_text()) if path.exists() else {}
        current_introspection_sentinal = hash((_INTROSPECTION_CODE, str(interpreter_path.absolute())))
        if (introspection_sentinal := data.get('introspection')) \
                and introspection_sentinal == current_introspection_sentinal:
            return cls(data=data)

        result = cls.compute(interpreter_path)
        if save_if_recomputed:
            data = result._data
            data['introspection'] = current_introspection_sentinal
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(json.dumps(data))

        return result


def _mac_arch(arch: str, is_32bit: bool) -> str:
    if not is_32bit:
        return arch

    if arch.startswith("ppc"):
        return "ppc"

    return "i386"


INTERPRETER_SHORT_NAMES = {
    "python": "py", "cpython": "cp", "pypy": "pp",
    "ironpython": "ip", "jython": "jy",
}


def _mac_binary_formats(version: Tuple[int, ...], cpu_arch: str) -> List[str]:
    formats = [cpu_arch]
    if cpu_arch == "x86_64":
        if version < (10, 4):
            return []
        formats.extend(["intel", "fat64", "fat32"])

    elif cpu_arch == "i386":
        if version < (10, 4):
            return []
        formats.extend(["intel", "fat32", "fat"])

    elif cpu_arch == "ppc64":
        if version > (10, 5) or version < (10, 4):
            return []
        formats.append("fat64")

    elif cpu_arch == "ppc":
        if version > (10, 6):
            return []
        formats.extend(["fat32", "fat"])

    if cpu_arch in {"arm64", "x86_64"}:
        formats.append("universal2")

    if cpu_arch in {"x86_64", "i386", "ppc64", "ppc", "intel"}:
        formats.append("universal")

    return formats


def _abi3_applies(python_version: Tuple) -> bool:
    return len(python_version) > 1 and python_version >= (3, 2)


def _normalize_string(string: str) -> str:
    return string.replace(".", "_").replace("-", "_")


_EM_ARM = 40
_EM_386 = 3
_EF_ARM_ABIMASK = 0xFF000000
_EF_ARM_ABI_VER5 = 0x05000000
_EF_ARM_ABI_FLOAT_HARD = 0x00000400
_PT_INTERP = 3
_elf_header_prefix_struct = Struct("4s5B7x")


class _ElfStructs:
    # noinspection PyPep8Naming
    def __init__(self, is_32_bit: bool, is_little_endian: bool):
        L = "L" if is_32_bit else "Q"
        e = "<" if is_little_endian else ">"

        self.header_suffix = Struct(f"{e}2HI3{L}I6H")
        self.program_header = Struct(f"{e}2I4{L}")


def _unpack(fd: IO, struct: Struct) -> Tuple:
    return struct.unpack(fd.read(struct.size))


@dataclass
class _ElfData:
    is_32_bit: bool
    is_little_endian: bool
    machine: int
    flags: int
    interpreter: Optional[str]

    def __str__(self):
        return f"ELF(is_32_bit={self.is_32_bit}, is_little_endian={self.is_little_endian}, " \
               f"machine={self.machine:x}, flags={self.flags:b}, " \
               f"interpreter={self.interpreter})"

    def _is_linux_armhf(self) -> bool:
        result = self.is_32_bit & self.is_little_endian and self.machine == _EM_ARM
        result &= (self.flags & _EF_ARM_ABIMASK) == _EF_ARM_ABI_VER5
        result &= (self.flags & _EF_ARM_ABI_FLOAT_HARD) == _EF_ARM_ABI_FLOAT_HARD
        return result

    def _is_linux_i686(self) -> bool:
        return self.is_32_bit and self.is_little_endian and self.machine == _EM_386

    def compute_musl_version(self) -> Optional[Tuple[int, ...]]:
        if not self.interpreter:
            return None

        proc = subprocess.run([self.interpreter], stderr=subprocess.PIPE, universal_newlines=True)
        lines = [n for n in (n.strip() for n in proc.stderr.splitlines()) if n]
        if len(lines) >= 2 and lines[0].startswith('musl'):
            try:
                return tuple(int(it) for it in lines[1].split()[1].split("."))[:2]
            except:  # noqa
                return None

    def have_compatible_abi(self, arch: str) -> bool:
        if arch == "armv7l":
            return self._is_linux_armhf()
        if arch == "i686":
            return self._is_linux_i686()
        return arch in {"x86_64", "aarch64", "ppc64", "ppc64le", "s390x"}

    @classmethod
    def read(cls, file: Path) -> Optional["_ElfData"]:
        with file.open('rb') as fd:
            uprefix = _unpack(fd, _elf_header_prefix_struct)

            if uprefix[0] != b'\x7fELF':
                return None

            is_32_bit, is_little_endian = (uprefix[1] == 1), (uprefix[2] == 1)
            structs = _ElfStructs(is_32_bit, is_little_endian)

            usuffix = _unpack(fd, structs.header_suffix)
            machine, flags = usuffix[1], usuffix[6]
            ph_offset, n_ph, ph_size = usuffix[4], usuffix[9], usuffix[8]

            interpreter = None
            for i in range(n_ph):
                fd.seek(ph_offset + i * ph_size)
                header = _unpack(fd, structs.program_header)
                if header[0] == _PT_INTERP:
                    sz = header[5]
                    fd.seek(header[2])
                    interpreter = os.fsdecode(fd.read(sz)).strip("\0")
                    break

            return _ElfData(is_32_bit, is_little_endian, machine, flags, interpreter)


_LEGACY_MANYLINUX_MAP: Dict[str, Tuple[int, ...]] = {
    "manylinux2014": (2, 17),
    "manylinux2010": (2, 12),
    "manylinux1": (2, 5),
}
