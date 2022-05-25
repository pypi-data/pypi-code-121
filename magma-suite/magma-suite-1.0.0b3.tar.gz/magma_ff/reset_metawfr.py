################################################
#
#   Functions to reset runs status
#       in MetaWorkflowRun[portal]
#
################################################
from dcicutils import ff_utils

from magma_ff.metawflrun import MetaWorkflowRun
from magma_ff.runupdate import RunUpdate
from magma_ff.utils import check_status


################################################
#   Functions
################################################
def reset_steps(metawfr_uuid, steps_name, ff_key, verbose=False, valid_status=None):
    """Reset runs in MetaWorkflowRun[portal] corresponding
    to specified step names.
    PATCH MetaWorkflowRun[portal] with updates.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param steps_name: Step names for runs to reset
    :type steps_name: list(str)
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun[portal]
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    meta_workflow_run = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        runupd_obj = RunUpdate(run_obj)
        patch_dict = runupd_obj.reset_steps(steps_name)
        res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
        if verbose:
            print(res_post)


def reset_shards(metawfr_uuid, shards_name, ff_key, verbose=False, valid_status=None):
    """Reset runs in MetaWorkflowRun[portal] corresponding
    to specified shard names.
    PATCH MetaWorkflowRun[portal] with updates.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param shards_name: Shard names for runs to reset
    :type shards_name: list(str)
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    meta_workflow_run = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        runupd_obj = RunUpdate(run_obj)
        patch_dict = runupd_obj.reset_shards(shards_name)
        res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
        if verbose:
            print(res_post)


def reset_status(
    metawfr_uuid, status, step_name, ff_key, verbose=False, valid_status=None
):
    """Reset runs in MetaWorkflowRun[portal] corresponding
    to specified step names if status match specified status.
    PATCH MetaWorkflowRun[portal] with updates.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param status: Status to reset
    :type status: str or list(str)
    :param steps_name: Step names for runs to reset
    :type steps_name: str or list(str)
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun
        final_status property
    :type valid_status: list(str) or None
    """
    if isinstance(status, str):
        status = [status]
    if isinstance(step_name, str):
        step_name = [step_name]
    perform_action = True
    meta_workflow_run = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        to_reset = []
        for shard_name, obj in run_obj.runs.items():
            if obj.status in status and obj.name in step_name:
                to_reset.append(shard_name)
        runupd_obj = RunUpdate(run_obj)
        patch_dict = runupd_obj.reset_shards(to_reset)
        res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
        if verbose:
            print(res_post)


def reset_all(metawfr_uuid, ff_key, verbose=False, valid_status=None):
    """Reset all runs in MetaWorkflowRun[portal].
    PATCH MetaWorkflowRun[portal] with updates.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    meta_workflow_run = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        to_reset = []
        for shard_name in run_obj.runs:
            to_reset.append(shard_name)
        runupd_obj = RunUpdate(run_obj)
        patch_dict = runupd_obj.reset_shards(to_reset)
        res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
        if verbose:
            print(res_post)


def reset_failed(metawfr_uuid, ff_key, verbose=False, valid_status=None):
    """Reset all failed runs in MetaWorkflowRun[portal].
    PATCH MetaWorkflowRun[portal] with updates.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun[portal]
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    meta_workflow_run = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        to_reset = []
        for shard_name, obj in run_obj.runs.items():
            if obj.status == "failed":
                to_reset.append(shard_name)
        runupd_obj = RunUpdate(run_obj)
        patch_dict = runupd_obj.reset_shards(to_reset)
        res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
        if verbose:
            print(res_post)
