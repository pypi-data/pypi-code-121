import os

import logging
from .cross_language.java_bridge import JavaBridge
from typing import Union

log = logging.getLogger(__name__)

def _inspect_java(java_ver: Union[str,int], output=None):
    from packaging import version
    import subprocess
    if isinstance(java_ver, int):
      major = java_ver
    else:
      java_ver = java_ver.split('.')
      major = int(java_ver[0])
      if major == 1:
        major = int(java_ver[1])

    if output is None:
      cmd = "java -version"
      child = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
      stdout, stderr = child.communicate()
      exit_code = child.wait()
      if exit_code != 0:
          return False
      output = stdout.decode('utf-8')+ stderr.decode('utf-8')
    try:
      ver = output.split("\n")[0].split('"')[1]
    except IndexError:
      ver = [x for x in output.split("\n") if 'version' in x][0].split('"')[1]
    vobj = version.parse(ver)
    if isinstance(vobj, version.LegacyVersion):
        ver = ver.split('_')[0]
        vobj = version.parse(ver)
    if vobj.major > 1:
        return vobj.major >= major
    else:
        return vobj.major == 1 and vobj.minor >= major

def get_or_create():
    if TSContext._active == None:
        import os
        java_ver = os.environ.get('autoai_ts_libs.deps.tspy_JAVA_VERSION', 8)

        if _inspect_java(java_ver) is False:
            msg = f"Please make sure Java {java_ver} is available"
            log.error(msg)
            raise EnvironmentError(msg)

        return TSContext()
    else:
        return TSContext._active


class TSContext(object):
    """the context object should be created only via :func:`.get_or_create()` API


    A default object is available via `autoai_ts_libs.deps.tspy.ts_context` object. From any where else, this object should be retrieved using `autoai_ts_libs.deps.tspy._get_context` API
    """
    _active = None

    def __init__(self, java_bridge: JavaBridge=None):

        # choose the default cross language utility
        if java_bridge is None:
            from autoai_ts_libs.deps.tspy.data_structures.cross_language.jpype_java_bridge import JPypeJavaBridge
            self._java_bridge = JPypeJavaBridge(self)
        else:
            # user specified their own cross language utility
            self._java_bridge = java_bridge
            # NOTE: don't call _tsc._utils directly, call
            # _tsc.java_bridge instead
            # this ensure data encapsulation and proper initialization of JVM
        TSContext._active = self
        self._is_jvm_active = False

    @property
    def java_bridge(self):
      if self.is_jvm_active is False:
        self._launch_jvm()
      return self._java_bridge

    @property
    def is_jvm_active(self):
        return self._is_jvm_active

    def _launch_jvm(self):
        if self._is_jvm_active is False:
          if os.environ.get('TS_HOME') is None:
              import pkg_resources
              import autoai_ts_libs.deps.tspy
              version = autoai_ts_libs.deps.tspy.__version__
              classpath = pkg_resources.resource_filename("autoai_ts_libs.deps.tspy",
                                                          f'deps/jars/time-series-assembly-python-{version}-jar-with-dependencies-small.jar')
          else:
              classpath = os.environ['TS_HOME']

          from os.path import exists

          if not exists(classpath):
            msg = f"Please check to ensure the file exists (and restart the kernel after updating): {classpath}"
            log.warn(msg)

          if os.environ.get('autoai_ts_libs.deps.tspy_ALLOW_INTERRUPT') is None:
              interrupt = False
          else:
              interrupt = os.getenv('autoai_ts_libs.deps.tspy_ALLOW_INTERRUPT', 'False').lower() == "true"
          self._java_bridge.startJVM(classpath=classpath, interrupt=interrupt)
          self._is_jvm_active = True

    def stop(self):
        self._java_bridge.stopJVM()
        TSContext._active = None
        self._is_jvm_active = False

    @property
    def packages(self):
        return self.java_bridge.package_root
