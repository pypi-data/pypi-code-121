import logging
import os
import threading
from abc import ABC
from functools import lru_cache
from typing import List,Optional,Union
from urllib.parse import urlparse
from localstack import config
from localstack.services.install import download_and_extract_with_retry
from localstack.utils import common
from localstack.utils.collections import ensure_list
from localstack.utils.common import in_docker,is_command_available,is_debian,rm_rf,run
from localstack.utils.files import mkdir
INSTALL_LOCK=threading.RLock()
POSTGRES_RPM_REPOSITORY="https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
LOG=logging.getLogger(__name__)
@lru_cache()
def is_redhat()->bool:
 return "rhel" in common.load_file("/etc/os-release","")
class PackageInstallationException(Exception):
 pass
class SystemNotSupportedException(PackageInstallationException):
 pass
class PackageInstaller(ABC):
 def __init__(self,log_package_name:Optional[str]):
  self.log_package_name=log_package_name
  self.logger=logging.getLogger(f"{__name__}.{log_package_name}")
  if log_package_name is None:
   self.logger.setLevel(logging.CRITICAL+1)
 def install(self,raise_on_error:bool=True)->None:
  try:
   if not self._check_if_available():
    try:
     self.logger.debug("Preparing the installation of %s.",self.log_package_name)
     self._prepare_installation()
     self.logger.debug("Starting to install %s.",self.log_package_name)
     self._install_package()
     self.logger.debug("Executing post-processing of %s.",self.log_package_name)
     self._post_process()
    except Exception as e:
     if isinstance(e,PackageInstallationException):
      raise
     else:
      suffix=(f" ({self.log_package_name})." if self.log_package_name is not None else ".")
      raise PackageInstallationException(f"The installation failed{suffix}")from e
    self._verify_installation()
    self.logger.debug("Successfully installed %s.",self.log_package_name)
   else:
    self.logger.debug("%s is already available.",self.log_package_name)
  except PackageInstallationException as e:
   if raise_on_error:
    raise
   else:
    if self.logger.isEnabledFor(logging.DEBUG):
     self.logger.exception("Error while installing package %s.",self.log_package_name)
    else:
     self.logger.error(e)
 def _check_if_available(self)->bool:
  raise NotImplementedError
 def _prepare_installation(self)->None:
  pass
 def _install_package(self)->None:
  raise NotImplementedError
 def _post_process(self)->None:
  pass
 def _verify_installation(self)->None:
  if not self._check_if_available():
   package_info=(f" of {self.log_package_name}" if self.log_package_name is not None else "")
   raise PackageInstallationException(f"The installation{package_info} failed (verification failed).")
class MultiPackageInstaller(PackageInstaller):
 def __init__(self,log_package_name:Optional[str],package_installers:Union[PackageInstaller,List[PackageInstaller]]):
  super(MultiPackageInstaller,self).__init__(log_package_name=log_package_name)
  self.package_installers=(package_installers if isinstance(package_installers,List)else[package_installers])
 def install(self,raise_on_error:bool=True):
  for package_installer in self.package_installers:
   package_installer.install(raise_on_error=raise_on_error)
class OSSpecificPackageInstaller(MultiPackageInstaller):
 def __init__(self,debian_installers:PackageInstaller,redhat_installers:PackageInstaller):
  package_installers=[]
  if is_debian():
   package_installers=debian_installers
  elif is_redhat():
   package_installers=redhat_installers
  super(OSSpecificPackageInstaller,self).__init__(log_package_name=self.__class__.__name__,package_installers=package_installers)
 def install(self,raise_on_error:bool=True):
  try:
   if not in_docker():
    raise SystemNotSupportedException("OS level packages are only installed within docker containers.")
   elif not is_debian()and not is_redhat():
    raise SystemNotSupportedException("The current operating system is currently not supported.")
   else:
    super(OSSpecificPackageInstaller,self).install(raise_on_error=raise_on_error)
  except PackageInstallationException as e:
   if raise_on_error:
    raise
   else:
    if self.logger.isEnabledFor(logging.DEBUG):
     self.logger.exception("Error while installing package %s.",self.log_package_name)
    else:
     self.logger.error(e)
class DebianPackageInstaller(PackageInstaller,ABC):
 def __init__(self,package_name:str):
  super(DebianPackageInstaller,self).__init__(log_package_name=package_name)
 def _install_os_packages(self,packages:Union[str,List[str]]):
  packages=packages if isinstance(packages,List)else[packages]
  with INSTALL_LOCK:
   download_path=self._download_os_packages(packages)
   cmd=self.cmd_prefix(download_path)+["install"]+packages
   run(cmd)
 def _download_os_packages(self,packages:Union[str,List[str]]):
  packages=ensure_list(packages)
  with INSTALL_LOCK:
   package_dir_name="--".join(packages)
   download_path=self.get_download_path(package_dir_name)
   mkdir(download_path)
   run(["apt-get","update"])
   LOG.debug("Downloading packages %s to folder: %s",packages,download_path)
   try:
    cmd=self.cmd_prefix(download_path)+["-d","install"]+packages
    run(cmd)
   except Exception as e:
    LOG.info("Unable to download packages %s: %s",packages,e)
    rm_rf(download_path)
   return download_path
 def cmd_prefix(self,cache_dir:str)->List[str]:
  return["apt",f"-o=dir::cache={cache_dir}",f"-o=dir::cache::archives={cache_dir}","-y"]
 def get_download_path(self,package:str)->str:
  return os.path.join(config.dirs.var_libs,"apt-libs",package)
class RedHatPackageInstaller(PackageInstaller,ABC):
 def __init__(self,package_name:str):
  super(RedHatPackageInstaller,self).__init__(log_package_name=package_name)
 def _install_os_packages(self,packages:Union[str,List[str]]):
  packages=packages if isinstance(packages,List)else[packages]
  with INSTALL_LOCK:
   run(["dnf","install","-y"]+packages)
DEBIAN_POSTGRES_LIB_FOLDER="/usr/lib/postgresql/11/lib"
REDHAT_POSTGRES_LIB_FOLDER="/usr/pgsql-11/lib"
class DebianPostgres11Installer(DebianPackageInstaller):
 def __init__(self):
  super(DebianPostgres11Installer,self).__init__("postgres11")
 def _check_if_available(self)->bool:
  return is_command_available("psql")
 def _install_package(self)->None:
  self._install_os_packages("postgresql-11")
class RedHatPostgres11Installer(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatPostgres11Installer,self).__init__("postgres11")
 def _check_if_available(self)->bool:
  return is_command_available("psql")
 def _prepare_installation(self)->None:
  self._install_os_packages(POSTGRES_RPM_REPOSITORY)
 def _install_package(self)->None:
  self._install_os_packages(["postgresql11-devel","postgresql11-server"])
 def _post_process(self)->None:
  run("ln -s /usr/pgsql-11/bin/pg_config /usr/bin/pg_config")
class DebianPlPythonInstaller(DebianPackageInstaller):
 def __init__(self):
  super(DebianPlPythonInstaller,self).__init__("plpython3")
 def _check_if_available(self)->bool:
  return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/plpython3.so")
 def _install_package(self)->None:
  self._install_os_packages("postgresql-plpython3-11")
class RedHatPlPythonInstaller(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatPlPythonInstaller,self).__init__("plpython3")
 def _check_if_available(self)->bool:
  return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/plpython3.so")
 def _install_package(self)->None:
  self._install_os_packages("postgresql11-plpython3")
postgres_installer=OSSpecificPackageInstaller(debian_installers=MultiPackageInstaller("PostgreSQL",[DebianPostgres11Installer(),DebianPlPythonInstaller()]),redhat_installers=MultiPackageInstaller("PostgreSQL",[RedHatPostgres11Installer(),RedHatPlPythonInstaller()]))
class DebianMariaDBInstaller(DebianPackageInstaller):
 def __init__(self):
  super(DebianMariaDBInstaller,self).__init__("MariaDB")
 def _check_if_available(self)->bool:
  return is_command_available("mysqld")
 def _install_package(self)->None:
  self._install_os_packages(["mariadb-server","mariadb-client"])
class RedHatMariaDBInstaller(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatMariaDBInstaller,self).__init__("MariaDB")
 def _check_if_available(self)->bool:
  return is_command_available("mysqld")
 def _install_package(self)->None:
  raise PackageInstallationException("MariaDB currently cannot be installed on RedHat")
mariadb_installer=OSSpecificPackageInstaller(debian_installers=DebianMariaDBInstaller(),redhat_installers=RedHatMariaDBInstaller())
class DebianTimescaleDBInstaller(DebianPackageInstaller):
 def __init__(self):
  super(DebianTimescaleDBInstaller,self).__init__("timescaledb")
 def _check_if_available(self)->bool:
  return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/timescaledb.so")
 def _install_package(self)->None:
  self._install_os_packages(["gcc","cmake","gcc","git"])
  ts_dir="/tmp/timescaledb"
  tag="2.0.0-rc4"
  run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
  run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
  rm_rf("/tmp/timescaledb")
class RedHatTimescaleDBInstaller(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatTimescaleDBInstaller,self).__init__("timescaledb")
 def _check_if_available(self)->bool:
  return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/timescaledb.so")
 def _install_package(self)->None:
  self._install_os_packages(["gcc","cmake","gcc","git","redhat-rpm-config"])
  ts_dir="/tmp/timescaledb"
  tag="2.0.0-rc4"
  run("cd /tmp; git clone https://github.com/timescale/timescaledb.git")
  run("cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install"%(ts_dir,tag))
  rm_rf("/tmp/timescaledb")
timescaledb_installer=OSSpecificPackageInstaller(debian_installers=DebianTimescaleDBInstaller(),redhat_installers=RedHatTimescaleDBInstaller())
class DebianRedisInstaller(DebianPackageInstaller):
 def __init__(self):
  super(DebianRedisInstaller,self).__init__("Redis")
 def _check_if_available(self)->bool:
  return is_command_available("redis-server")
 def _install_package(self)->None:
  self._install_os_packages("redis-server")
class RedHatRedisInstaller(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatRedisInstaller,self).__init__("Redis")
 def _check_if_available(self)->bool:
  return is_command_available("redis-server")
 def _install_package(self)->None:
  raise PackageInstallationException("Redis currently cannot be installed on RedHat")
redis_installer=OSSpecificPackageInstaller(debian_installers=DebianRedisInstaller(),redhat_installers=RedHatRedisInstaller())
class DebianMosquittoInstaller(DebianPackageInstaller):
 def __init__(self):
  super(DebianMosquittoInstaller,self).__init__("Mosquitto")
 def _check_if_available(self)->bool:
  return is_command_available("mosquitto")
 def _install_package(self)->None:
  self._install_os_packages("mosquitto")
class RedHatMosquittoInstaller(RedHatPackageInstaller):
 def __init__(self):
  super(RedHatMosquittoInstaller,self).__init__("Mosquitto")
 def _check_if_available(self)->bool:
  return is_command_available("mosquitto")
 def _install_package(self)->None:
  raise PackageInstallationException("Mosquitto currently cannot be installed on RedHat")
mosquitto_installer=OSSpecificPackageInstaller(debian_installers=DebianMosquittoInstaller(),redhat_installers=RedHatMosquittoInstaller())
class ArchiveDownloadInstaller(PackageInstaller):
 def __init__(self,archive_url:str,target_dir:str,cache_archive:Optional[str]=None,extract_single_directory:bool=True):
  super(ArchiveDownloadInstaller,self).__init__(log_package_name=self.__class__.__name__)
  self.archive_url=archive_url
  self.target_dir=target_dir
  self.extract_single_directory=extract_single_directory
  self.cache_archive=cache_archive
  if not cache_archive:
   filename_parts=urlparse(archive_url).path.split(".")
   extension=filename_parts[-1]if len(filename_parts)>1 else "zip"
   self.cache_archive=f"{self.target_dir.rstrip(os.sep)}.{extension}"
 def _check_if_available(self)->bool:
  return os.path.exists(self.target_dir)and bool(os.listdir(self.target_dir))
 def _install_package(self):
  with INSTALL_LOCK:
   self.logger.debug("Downloading and installing archive: %s",self.archive_url)
   download_and_extract_with_retry(self.archive_url,self.cache_archive,self.target_dir)
   if self.extract_single_directory:
    dir_contents=os.listdir(self.target_dir)
    if len(dir_contents)!=1:
     return
    target_subdir=os.path.join(self.target_dir,dir_contents[0])
    if not os.path.isdir(target_subdir):
     return
    os.rename(target_subdir,f"{self.target_dir}.bk")
    rm_rf(self.target_dir)
    os.rename(f"{self.target_dir}.bk",self.target_dir)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
