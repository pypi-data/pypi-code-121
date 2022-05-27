_R='Mosquitto'
_Q='cd %s; git checkout %s; ./bootstrap -DREGRESS_CHECKS=OFF; cd build; make; make install'
_P='cd /tmp; git clone https://github.com/timescale/timescaledb.git'
_O='2.0.0-rc4'
_N='timescaledb'
_M='mysqld'
_L='MariaDB'
_K='PostgreSQL'
_J='plpython3'
_I='postgres11'
_H='Error while installing package %s.'
_G='mosquitto'
_F='redis-server'
_E='install'
_D='/tmp/timescaledb'
_C='gcc'
_B=True
_A=None
import logging,os,threading
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
POSTGRES_RPM_REPOSITORY='https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm'
LOG=logging.getLogger(__name__)
@lru_cache()
def is_redhat():return'rhel'in common.load_file('/etc/os-release','')
class PackageInstallationException(Exception):0
class SystemNotSupportedException(PackageInstallationException):0
class PackageInstaller(ABC):
	def __init__(A,log_package_name):
		B=log_package_name;A.log_package_name=B;A.logger=logging.getLogger(f"{__name__}.{B}")
		if B is _A:A.logger.setLevel(logging.CRITICAL+1)
	def install(A,raise_on_error=_B):
		try:
			if not A._check_if_available():
				try:A.logger.debug('Preparing the installation of %s.',A.log_package_name);A._prepare_installation();A.logger.debug('Starting to install %s.',A.log_package_name);A._install_package();A.logger.debug('Executing post-processing of %s.',A.log_package_name);A._post_process()
				except Exception as B:
					if isinstance(B,PackageInstallationException):raise
					else:C=f" ({A.log_package_name})."if A.log_package_name is not _A else'.';raise PackageInstallationException(f"The installation failed{C}") from B
				A._verify_installation();A.logger.debug('Successfully installed %s.',A.log_package_name)
			else:A.logger.debug('%s is already available.',A.log_package_name)
		except PackageInstallationException as B:
			if raise_on_error:raise
			elif A.logger.isEnabledFor(logging.DEBUG):A.logger.exception(_H,A.log_package_name)
			else:A.logger.error(B)
	def _check_if_available(A):raise NotImplementedError
	def _prepare_installation(A):0
	def _install_package(A):raise NotImplementedError
	def _post_process(A):0
	def _verify_installation(A):
		if not A._check_if_available():B=f" of {A.log_package_name}"if A.log_package_name is not _A else'';raise PackageInstallationException(f"The installation{B} failed (verification failed).")
class MultiPackageInstaller(PackageInstaller):
	def __init__(B,log_package_name,package_installers):A=package_installers;super(MultiPackageInstaller,B).__init__(log_package_name=log_package_name);B.package_installers=A if isinstance(A,List)else[A]
	def install(A,raise_on_error=_B):
		for B in A.package_installers:B.install(raise_on_error=raise_on_error)
class OSSpecificPackageInstaller(MultiPackageInstaller):
	def __init__(B,debian_installers,redhat_installers):
		A=[]
		if is_debian():A=debian_installers
		elif is_redhat():A=redhat_installers
		super(OSSpecificPackageInstaller,B).__init__(log_package_name=B.__class__.__name__,package_installers=A)
	def install(A,raise_on_error=_B):
		B=raise_on_error
		try:
			if not in_docker():raise SystemNotSupportedException('OS level packages are only installed within docker containers.')
			elif not is_debian()and not is_redhat():raise SystemNotSupportedException('The current operating system is currently not supported.')
			else:super(OSSpecificPackageInstaller,A).install(raise_on_error=B)
		except PackageInstallationException as C:
			if B:raise
			elif A.logger.isEnabledFor(logging.DEBUG):A.logger.exception(_H,A.log_package_name)
			else:A.logger.error(C)
class DebianPackageInstaller(PackageInstaller,ABC):
	def __init__(A,package_name):super(DebianPackageInstaller,A).__init__(log_package_name=package_name)
	def _install_os_packages(B,packages):
		A=packages;A=A if isinstance(A,List)else[A]
		with INSTALL_LOCK:C=B._download_os_packages(A);D=B.cmd_prefix(C)+[_E]+A;run(D)
	def _download_os_packages(C,packages):
		A=packages;A=ensure_list(A)
		with INSTALL_LOCK:
			D='--'.join(A);B=C.get_download_path(D);mkdir(B);run(['apt-get','update']);LOG.debug('Downloading packages %s to folder: %s',A,B)
			try:E=C.cmd_prefix(B)+['-d',_E]+A;run(E)
			except Exception as F:LOG.info('Unable to download packages %s: %s',A,F);rm_rf(B)
			return B
	def cmd_prefix(B,cache_dir):A=cache_dir;return['apt',f"-o=dir::cache={A}",f"-o=dir::cache::archives={A}",'-y']
	def get_download_path(A,package):return os.path.join(config.dirs.var_libs,'apt-libs',package)
class RedHatPackageInstaller(PackageInstaller,ABC):
	def __init__(A,package_name):super(RedHatPackageInstaller,A).__init__(log_package_name=package_name)
	def _install_os_packages(B,packages):
		A=packages;A=A if isinstance(A,List)else[A]
		with INSTALL_LOCK:run(['dnf',_E,'-y']+A)
DEBIAN_POSTGRES_LIB_FOLDER='/usr/lib/postgresql/11/lib'
REDHAT_POSTGRES_LIB_FOLDER='/usr/pgsql-11/lib'
class DebianPostgres11Installer(DebianPackageInstaller):
	def __init__(A):super(DebianPostgres11Installer,A).__init__(_I)
	def _check_if_available(A):return is_command_available('psql')
	def _install_package(A):A._install_os_packages('postgresql-11')
class RedHatPostgres11Installer(RedHatPackageInstaller):
	def __init__(A):super(RedHatPostgres11Installer,A).__init__(_I)
	def _check_if_available(A):return is_command_available('psql')
	def _prepare_installation(A):A._install_os_packages(POSTGRES_RPM_REPOSITORY)
	def _install_package(A):A._install_os_packages(['postgresql11-devel','postgresql11-server'])
	def _post_process(A):run('ln -s /usr/pgsql-11/bin/pg_config /usr/bin/pg_config')
class DebianPlPythonInstaller(DebianPackageInstaller):
	def __init__(A):super(DebianPlPythonInstaller,A).__init__(_J)
	def _check_if_available(A):return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/plpython3.so")
	def _install_package(A):A._install_os_packages('postgresql-plpython3-11')
class RedHatPlPythonInstaller(RedHatPackageInstaller):
	def __init__(A):super(RedHatPlPythonInstaller,A).__init__(_J)
	def _check_if_available(A):return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/plpython3.so")
	def _install_package(A):A._install_os_packages('postgresql11-plpython3')
postgres_installer=OSSpecificPackageInstaller(debian_installers=MultiPackageInstaller(_K,[DebianPostgres11Installer(),DebianPlPythonInstaller()]),redhat_installers=MultiPackageInstaller(_K,[RedHatPostgres11Installer(),RedHatPlPythonInstaller()]))
class DebianMariaDBInstaller(DebianPackageInstaller):
	def __init__(A):super(DebianMariaDBInstaller,A).__init__(_L)
	def _check_if_available(A):return is_command_available(_M)
	def _install_package(A):A._install_os_packages(['mariadb-server','mariadb-client'])
class RedHatMariaDBInstaller(RedHatPackageInstaller):
	def __init__(A):super(RedHatMariaDBInstaller,A).__init__(_L)
	def _check_if_available(A):return is_command_available(_M)
	def _install_package(A):raise PackageInstallationException('MariaDB currently cannot be installed on RedHat')
mariadb_installer=OSSpecificPackageInstaller(debian_installers=DebianMariaDBInstaller(),redhat_installers=RedHatMariaDBInstaller())
class DebianTimescaleDBInstaller(DebianPackageInstaller):
	def __init__(A):super(DebianTimescaleDBInstaller,A).__init__(_N)
	def _check_if_available(A):return os.path.exists(f"{DEBIAN_POSTGRES_LIB_FOLDER}/timescaledb.so")
	def _install_package(A):A._install_os_packages([_C,'cmake',_C,'git']);B=_D;C=_O;run(_P);run(_Q%(B,C));rm_rf(_D)
class RedHatTimescaleDBInstaller(RedHatPackageInstaller):
	def __init__(A):super(RedHatTimescaleDBInstaller,A).__init__(_N)
	def _check_if_available(A):return os.path.exists(f"{REDHAT_POSTGRES_LIB_FOLDER}/timescaledb.so")
	def _install_package(A):A._install_os_packages([_C,'cmake',_C,'git','redhat-rpm-config']);B=_D;C=_O;run(_P);run(_Q%(B,C));rm_rf(_D)
timescaledb_installer=OSSpecificPackageInstaller(debian_installers=DebianTimescaleDBInstaller(),redhat_installers=RedHatTimescaleDBInstaller())
class DebianRedisInstaller(DebianPackageInstaller):
	def __init__(A):super(DebianRedisInstaller,A).__init__('Redis')
	def _check_if_available(A):return is_command_available(_F)
	def _install_package(A):A._install_os_packages(_F)
class RedHatRedisInstaller(RedHatPackageInstaller):
	def __init__(A):super(RedHatRedisInstaller,A).__init__('Redis')
	def _check_if_available(A):return is_command_available(_F)
	def _install_package(A):raise PackageInstallationException('Redis currently cannot be installed on RedHat')
redis_installer=OSSpecificPackageInstaller(debian_installers=DebianRedisInstaller(),redhat_installers=RedHatRedisInstaller())
class DebianMosquittoInstaller(DebianPackageInstaller):
	def __init__(A):super(DebianMosquittoInstaller,A).__init__(_R)
	def _check_if_available(A):return is_command_available(_G)
	def _install_package(A):A._install_os_packages(_G)
class RedHatMosquittoInstaller(RedHatPackageInstaller):
	def __init__(A):super(RedHatMosquittoInstaller,A).__init__(_R)
	def _check_if_available(A):return is_command_available(_G)
	def _install_package(A):raise PackageInstallationException('Mosquitto currently cannot be installed on RedHat')
mosquitto_installer=OSSpecificPackageInstaller(debian_installers=DebianMosquittoInstaller(),redhat_installers=RedHatMosquittoInstaller())
class ArchiveDownloadInstaller(PackageInstaller):
	def __init__(A,archive_url,target_dir,cache_archive=_A,extract_single_directory=_B):
		C=cache_archive;B=archive_url;super(ArchiveDownloadInstaller,A).__init__(log_package_name=A.__class__.__name__);A.archive_url=B;A.target_dir=target_dir;A.extract_single_directory=extract_single_directory;A.cache_archive=C
		if not C:D=urlparse(B).path.split('.');E=D[-1]if len(D)>1 else'zip';A.cache_archive=f"{A.target_dir.rstrip(os.sep)}.{E}"
	def _check_if_available(A):return os.path.exists(A.target_dir)and bool(os.listdir(A.target_dir))
	def _install_package(A):
		with INSTALL_LOCK:
			A.logger.debug('Downloading and installing archive: %s',A.archive_url);download_and_extract_with_retry(A.archive_url,A.cache_archive,A.target_dir)
			if A.extract_single_directory:
				B=os.listdir(A.target_dir)
				if len(B)!=1:return
				C=os.path.join(A.target_dir,B[0])
				if not os.path.isdir(C):return
				os.rename(C,f"{A.target_dir}.bk");rm_rf(A.target_dir);os.rename(f"{A.target_dir}.bk",A.target_dir)