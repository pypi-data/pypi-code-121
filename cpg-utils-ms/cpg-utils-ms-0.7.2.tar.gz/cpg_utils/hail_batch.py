"""Convenience functions related to Hail."""

import asyncio
import inspect
import os
import pathlib
import textwrap
from typing import Optional, Union, List
from abc import ABC, abstractmethod

import hail as hl
import hailtop.batch as hb
from cloudpathlib import CloudPath
from cloudpathlib.anypath import to_anypath

from cpg_utils.config import get_config


# template commands strings
GCLOUD_AUTH_COMMAND = (
    'gcloud -q auth activate-service-account --key-file=/gsa-key/key.json'
)
BASE_CMD = """
import logging
logger = logging.getLogger(__file__)
logging.basicConfig(format='%(levelname)s (%(name)s %(lineno)s): %(message)s')
logger.setLevel(logging.INFO)
"""
HAIL_STARTUP = """
import asyncio
import hail as hl
asyncio.get_event_loop().run_until_complete(
    hl.init_batch(
        default_reference='{default_reference}',
        billing_project='{hail_billing_project}',
        remote_tmpdir='{hail_bucket}',
    )
)
"""
CMD_MODULE = """
{source_module}
{func_name}{func_args}
"""
CMD_SCRIPT = """
set -o pipefail
set -ex
{gcloud_auth}

{packages}

cat << EOT >> script.py
{command}
EOT
python3 script.py
"""


# The AnyPath class https://cloudpathlib.drivendata.org/stable/anypath-polymorphism/
# is very handy to parse a string that can be either a cloud URL or a local posix path.
# However, AnyPath can't be used for type hinting, because neither CloudPath nor
# pathlib.Path derive from it. The AnyPath's constructor method doesn't actually return
# an instance of AnyPath class, but rather Union[CloudPath, pathlib.Path], and it's
# designed to dynamically pick a specific CloudPath or pathlib.Path subclass.
# Here we create an alias for such union to allow using simple "Path" in type hints:
Path = Union[CloudPath, pathlib.Path]

# We would still need to call AnyPath() to parse a string, which might be confusing.
# Something like to_path() would look better, so we are aliasing a handy method
# to_anypath to to_path, which returns exactly the Union type we are looking for:
to_path = to_anypath


def init_batch(**kwargs):
    """
    Initializes the Hail Query Service from within Hail Batch.
    Requires the `hail/billing_project` and `hail/bucket` config variables to be set.

    Parameters
    ----------
    kwargs : keyword arguments
        Forwarded directly to `hl.init_batch`.
    """
    return asyncio.get_event_loop().run_until_complete(
        hl.init_batch(
            default_reference='GRCh38',
            billing_project=get_config()['hail']['billing_project'],
            remote_tmpdir=remote_tmpdir(),
            **kwargs,
        )
    )


def copy_common_env(job: hb.batch.job.Job) -> None:
    """Copies common environment variables that we use to run Hail jobs.

    These variables are typically set up in the analysis-runner driver, but need to be
    passed through for "batch-in-batch" use cases.

    The environment variable values are extracted from the current process and
    copied to the environment dictionary of the given Hail Batch job.
    """
    # If possible, please don't add new environment variables here, but instead add
    # config variables.
    for key in ('CPG_CONFIG_PATH',):
        val = os.getenv(key)
        if val:
            job.env(key, val)


def remote_tmpdir(hail_bucket: Optional[str] = None) -> str:
    """Returns the remote_tmpdir to use for Hail initialization.

    If `hail_bucket` is not specified explicitly, requires the `hail/bucket` config variable to be set.
    """
    bucket = hail_bucket or get_config().get('hail', {}).get('bucket')
    assert bucket, f'hail_bucket was not set by argument or configuration'
    return f'gs://{bucket}/batch-tmp'


class PathScheme(ABC):
    """
    Cloud storage path scheme. Constructs full paths to buckets and files.
    """

    @abstractmethod
    def path_prefix(self, dataset: str, category: str) -> str:
        """Build path prefix used in dataset_path"""

    @abstractmethod
    def full_path(self, prefix: str, suffix: str) -> str:
        """Build full path from prefix and suffix"""

    @staticmethod
    def parse(val: str) -> 'PathScheme':
        """Parse subclass name from string"""
        match val:
            case 'gs':
                return GSPathScheme()
            case 'hail-az':
                return AzurePathScheme()
            case _:
                raise ValueError(f'Unsupported path format: {val}. Available: gs, hail-az')


class GSPathScheme(PathScheme):
    """
    Google Cloud Storage path scheme.
    """

    def __init__(self):
        self.scheme = 'gs'
        self.prefix = 'cpg'

    def path_prefix(self, dataset: str, category: str) -> str:
        """Build path prefix used in dataset_path"""
        return f'{self.prefix}-{dataset}-{category}'

    def full_path(self, prefix: str, suffix: str) -> str:
        """Build full path from prefix and suffix"""
        return os.path.join(f'{self.scheme}://', prefix, suffix)


class AzurePathScheme(PathScheme):
    """
    Azure Blob Storage path scheme, following the Hail Batch hail-az format.
    """

    def __init__(self, account: Optional[str] = 'cpg'):
        config = get_config()
        self.scheme = 'hail-az'
        self.account = config['workflow'].get('azure_account', account)

    def path_prefix(self, dataset: str, category: str) -> str:
        """Build path prefix used in dataset_path"""
        return f'{self.account}/{dataset}-{category}'

    def full_path(self, prefix: str, suffix: str) -> str:
        """Build full path from prefix and suffix"""
        return os.path.join(f'{self.scheme}://', prefix, suffix)


def dataset_path(
    suffix: str,
    category: Optional[str] = None,
    dataset: Optional[str] = None,
    access_level: Optional[str] = None,
    path_scheme: Optional[str] = None,
) -> str:
    """
    Returns a full path for the current dataset, given a category and path suffix.

    This is useful for specifying input files, as in contrast to the output_path
    function, dataset_path does _not_ take the `workflow/output_prefix` config variable
    into account.

    Examples
    --------
    Assuming that the analysis-runner has been invoked with
    `--dataset fewgenomes --access-level test --output 1kg_pca/v42`:

    >>> from cpg_utils.hail_batch import dataset_path
    >>> dataset_path('1kg_densified/combined.mt')
    'gs://cpg-fewgenomes-test/1kg_densified/combined.mt'
    >>> dataset_path('1kg_densified/report.html', 'web')
    'gs://cpg-fewgenomes-test-web/1kg_densified/report.html'
    >>> dataset_path('1kg_densified/report.html', path_scheme='hail-az')
    'hail-az://cpg/fewgenomes-test/1kg_densified/report.html'

    Notes
    -----
    Requires either the
    * `workflow/dataset` and `workflow/access_level` config variables, or the
    * `workflow/dataset_path` config variable
    to be set, where the former takes precedence.

    Parameters
    ----------
    suffix : str
        A path suffix to append to the bucket.
    category : str, optional
        A category like "upload", "tmp", "web". If omitted, defaults to the "main" and
        "test" buckets based on the access level. See
        https://github.com/populationgenomics/team-docs/tree/main/storage_policies
        for a full list of categories and their use cases.
    dataset : str, optional
        Dataset name, takes precedence over the `workflow/dataset` config variable
    access_level : str, optional
        Access level, takes precedence over the `workflow/access_level` config variable
    path_scheme: str, optional
        Cloud storage path scheme, takes precedence over the `workflow/path_scheme`
        config variable

    Returns
    -------
    str
    """
    config = get_config()
    dataset = dataset or config['workflow'].get('dataset')
    access_level = access_level or config['workflow'].get('access_level')
    path_scheme = path_scheme or config['workflow'].get('path_scheme', 'gs')

    if dataset and access_level:
        namespace = 'test' if access_level == 'test' else 'main'
        if category is None:
            category = namespace
        elif category not in ('archive', 'upload'):
            category = f'{namespace}-{category}'
        prefix = PathScheme.parse(path_scheme).path_prefix(dataset, category)
    else:
        prefix = config['workflow']['dataset_path']

    return PathScheme.parse(path_scheme).full_path(prefix, suffix)


def web_url(
    suffix: str,
    dataset: Optional[str] = None,
    access_level: Optional[str] = None,
) -> str:
    """Returns URL corresponding to a dataset path of category 'web',
    assuming other arguments are the same.
    """
    config = get_config()
    dataset = dataset or config['workflow'].get('dataset')
    access_level = access_level or config['workflow'].get('access_level')
    namespace = 'test' if access_level == 'test' else 'main'
    web_url_template = config['workflow'].get('web_url_template')
    try:
        url = web_url_template.format(dataset=dataset, namespace=namespace)
    except KeyError as e:
        raise ValueError(
            f'`workflow/web_url_template` should be parametrised by "dataset" and '
            f'"namespace" in curly braces, for example: '
            f'https://{{namespace}}-web.populationgenomics.org.au/{{dataset}}. '
            f'Got: {web_url_template}'
        ) from e
    return os.path.join(url, suffix)


def output_path(suffix: str, category: Optional[str] = None) -> str:
    """Returns a full path for the given category and path suffix.

    In contrast to the dataset_path function, output_path takes the `workflow/output_prefix`
    config variable into account.

    Examples
    --------
    If using the analysis-runner, the `workflow/output_prefix` would be set to the argument
    provided using the --output argument, e.g.
    `--dataset fewgenomes --access-level test --output 1kg_pca/v42`:
    will use '1kg_pca/v42' as the base path to build upon in this method

    >>> from cpg_utils.hail_batch import output_path
    >>> output_path('loadings.ht')
    'gs://cpg-fewgenomes-test/1kg_pca/v42/loadings.ht'
    >>> output_path('report.html', 'web')
    'gs://cpg-fewgenomes-test-web/1kg_pca/v42/report.html'

    Notes
    -----
    Requires the `workflow/output_prefix` config variable to be set, in addition to the
    requirements for `dataset_path`.

    Parameters
    ----------
    suffix : str
        A path suffix to append to the bucket + output directory.
    category : str, optional
        A category like "upload", "tmp", "web". If omitted, defaults to the "main" and
        "test" buckets based on the access level. See
        https://github.com/populationgenomics/team-docs/tree/main/storage_policies
        for a full list of categories and their use cases.

    Returns
    -------
    str
    """
    return dataset_path(
        os.path.join(get_config()['workflow']['output_prefix'], suffix), category
    )


def image_path(suffix: str) -> str:
    """Returns a full path to a container image in the default registry.

    Examples
    --------
    >>> image_path('bcftools:1.10.2')
    'australia-southeast1-docker.pkg.dev/cpg-common/images/bcftools:1.10.2'

    Notes
    -----
    Requires the `workflow/image_registry_prefix` config variable to be set.

    Parameters
    ----------
    suffix : str
        Describes the location within the registry.

    Returns
    -------
    str
    """
    return os.path.join(get_config()['workflow']['image_registry_prefix'], suffix)


def reference_path(suffix: str) -> Union[CloudPath, Path]:
    """Returns a full path to a reference file.

    Examples
    --------
    >>> reference_path('hg38/v0/wgs_calling_regions.hg38.interval_list')
    'gs://cpg-reference/hg38/v0/wgs_calling_regions.hg38.interval_list'

    Notes
    -----
    Requires the `workflow/reference_prefix` config variable to be set.

    Parameters
    ----------
    suffix : str
        Describes path relative to the reference prefix.

    Returns
    -------
    str
    """
    # A leading slash results in the prefix being ignored, therefore use strip below.
    return to_anypath(get_config()['workflow']['reference_prefix']) / suffix.strip('/')


def authenticate_cloud_credentials_in_job(
    job,
    print_all_statements: bool = True,
):
    """
    Takes a hail batch job, activates the appropriate service account

    Once multiple environments are supported this method will decide
    on which authentication method is appropriate

    Parameters
    ----------
    job
        * A hail BashJob
    print_all_statements
        * logging toggle

    Returns
    -------
    None
    """

    # Use "set -x" to print the commands for easier debugging.
    if print_all_statements:
        job.command('set -x')

    # activate the google service account
    job.command(GCLOUD_AUTH_COMMAND)


def query_command(
    module,
    func_name: str,
    *func_args,
    setup_gcp: bool = False,
    hail_billing_project: Optional[str] = None,
    hail_bucket: Optional[str] = None,
    default_reference: str = 'GRCh38',
    packages: Optional[List[str]] = None,
) -> str:
    """
    Run a Python Hail Query function inside a Hail Batch job.
    Constructs a command string to use with job.command().
    If hail_billing_project is provided, Hail Query will be initialised.
    """
    python_cmd = BASE_CMD
    if hail_billing_project:
        assert hail_bucket
        python_cmd += HAIL_STARTUP.format(
            default_reference=default_reference,
            hail_billing_project=hail_billing_project,
            hail_bucket=hail_bucket,
        )
    python_cmd += CMD_MODULE.format(
        source_module=textwrap.dedent(inspect.getsource(module)),
        func_name=func_name,
        func_args=func_args,
    )

    return CMD_SCRIPT.format(
        gcloud_auth=GCLOUD_AUTH_COMMAND if setup_gcp else '',
        packages=('pip3 install ' + ' '.join(packages)) if packages else '',
        python_cmd=python_cmd,
    )
