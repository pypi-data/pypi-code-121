"""Convenience functions related to Hail."""

import asyncio
import inspect
import os
import textwrap
from pathlib import Path
from typing import Optional, Union, List

import hail as hl
import hailtop.batch as hb
from cloudpathlib import CloudPath
from cloudpathlib.anypath import to_anypath


GCLOUD_AUTH_COMMAND = (
    'gcloud -q auth activate-service-account --key-file=/gsa-key/key.json'
)


def init_batch(**kwargs):
    """
    Initializes the Hail Query Service from within Hail Batch.
    Requires the HAIL_BILLING_PROJECT and HAIL_BUCKET environment variables to be set.

    Parameters
    ----------
    kwargs : keyword arguments
        Forwarded directly to `hl.init_batch`.
    """

    billing_project = os.getenv('HAIL_BILLING_PROJECT')
    assert billing_project
    return asyncio.get_event_loop().run_until_complete(
        hl.init_batch(
            default_reference='GRCh38',
            billing_project=billing_project,
            remote_tmpdir=remote_tmpdir(),
            **kwargs,
        )
    )


def copy_common_env(job: hb.batch.job.Job) -> None:
    """Copies common environment variables that we use to run Hail jobs.

    These variables are typically set up in the analysis-runner driver, but need to be
    passed through for "batch-in-batch" use cases.

    The environment variable values are extracted from the current process and
    copied to the environment dictionary of the given Hail Batch job."""

    for key in (
        'CPG_ACCESS_LEVEL',
        'CPG_DATASET',
        'CPG_DATASET_GCP_PROJECT',
        'CPG_DATASET_PATH',
        'CPG_DRIVER_IMAGE',
        'CPG_IMAGE_REGISTRY_PREFIX',
        'CPG_REFERENCE_PREFIX',
        'CPG_OUTPUT_PREFIX',
        'HAIL_BILLING_PROJECT',
        'HAIL_BUCKET',
    ):
        val = os.getenv(key)
        if val:
            job.env(key, val)


def remote_tmpdir(hail_bucket: Optional[str] = None) -> str:
    """Returns the remote_tmpdir to use for Hail initialization.

    If `hail_bucket` is not specified explicitly, requires the HAIL_BUCKET environment variable to be set."""

    if not hail_bucket:
        hail_bucket = os.getenv('HAIL_BUCKET')
        assert hail_bucket
    return f'gs://{hail_bucket}/batch-tmp'


def dataset_path(suffix: str, category: Optional[str] = None) -> str:
    """
    Returns a full path for the current dataset, given a category and path suffix.

    This is useful for specifying input files, as in contrast to the output_path
    function, dataset_path does _not_ take the CPG_OUTPUT_PREFIX environment variable
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

    Notes
    -----
    Requires either the
    * `CPG_DATASET` and `CPG_ACCESS_LEVEL` environment variables, or the
    * `CPG_DATASET_PATH` environment variable
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

    Returns
    -------
    str
    """
    dataset = os.getenv('CPG_DATASET')
    access_level = os.getenv('CPG_ACCESS_LEVEL')

    if dataset and access_level:
        namespace = 'test' if access_level == 'test' else 'main'
        if category is None:
            category = namespace
        elif category not in ('archive', 'upload'):
            category = f'{namespace}-{category}'
        prefix = f'cpg-{dataset}-{category}'
    else:
        prefix = os.getenv('CPG_DATASET_PATH') or ''  # coerce to str
        assert prefix

    return os.path.join('gs://', prefix, suffix)


def output_path(suffix: str, category: Optional[str] = None) -> str:
    """Returns a full path for the given category and path suffix.

    In contrast to the dataset_path function, output_path takes the CPG_OUTPUT_PREFIX
    environment variable into account.

    Examples
    --------
    If using the analysis-runner, the CPG_OUTPUT_PREFIX would be set to the argument
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
    Requires the `CPG_OUTPUT_PREFIX` environment variable to be set, in addition to the
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
    output = os.getenv('CPG_OUTPUT_PREFIX')
    assert output
    return dataset_path(os.path.join(output, suffix), category)


def image_path(suffix: str) -> str:
    """Returns a full path to a container image in the default registry.

    Examples
    --------
    >>> image_path('bcftools:1.10.2')
    'australia-southeast1-docker.pkg.dev/cpg-common/images/bcftools:1.10.2'

    Notes
    -----
    Requires the `CPG_IMAGE_REGISTRY_PREFIX` environment variable to be set.

    Parameters
    ----------
    suffix : str
        Describes the location within the registry.

    Returns
    -------
    str
    """
    prefix = os.getenv('CPG_IMAGE_REGISTRY_PREFIX')
    assert prefix
    return f'{prefix}/{suffix}'


def reference_path(suffix: str) -> Union[CloudPath, Path]:
    """Returns a full path to a reference file.

    Examples
    --------
    >>> reference_path('hg38/v0/wgs_calling_regions.hg38.interval_list')
    'gs://cpg-reference/hg38/v0/wgs_calling_regions.hg38.interval_list'

    Notes
    -----
    Requires the `CPG_REFERENCE_PREFIX` environment variable to be set.

    Parameters
    ----------
    suffix : str
        Describes path relative to CPG_REFERENCE_PREFIX.

    Returns
    -------
    str
    """
    prefix = os.getenv('CPG_REFERENCE_PREFIX')
    assert prefix
    return to_anypath(prefix) / suffix


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
    python_cmd = f"""
import logging
logger = logging.getLogger(__file__)
logging.basicConfig(format='%(levelname)s (%(name)s %(lineno)s): %(message)s')
logger.setLevel(logging.INFO)
"""
    if hail_billing_project:
        assert hail_bucket
        python_cmd += f"""
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
        python_cmd += f"""
{textwrap.dedent(inspect.getsource(module))}
{func_name}{func_args}
"""
    cmd = f"""
set -o pipefail
set -ex
{GCLOUD_AUTH_COMMAND if setup_gcp else ''}

{('pip3 install ' + ' '.join(packages)) if packages else ''}

cat << EOT >> script.py
{python_cmd}
EOT
python3 script.py
"""
    return cmd
