################################################
#
#   Function to check and patch status
#       runs in MetaWorkflowRun[portal]
#
################################################
from dcicutils import ff_utils

from magma_ff import checkstatus
from magma_ff.metawflrun import MetaWorkflowRun
from magma_ff.utils import check_status, make_embed_request


################################################
#   Functions
################################################
def status_metawfr(
    metawfr_uuid, ff_key, verbose=False, env="fourfront-cgap", valid_status=None
):
    """Perform status check on MetaWorkflowRun[portal].

    Retrieve the MetaWorkflowRun[portal], check all of its runs for
    updates, check for QC failures (if applicable),
    and then PATCH MetaWorkflowRun[portal] with updates (if found).

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param env: Environment name
    :type env: str
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    patch_body = None
    run_json = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw&datastore=database", key=ff_key
    )
    perform_action = check_status(run_json, valid_status)
    if perform_action:
        ignore_quality_metrics = run_json.get("ignore_output_quality_metrics")
        run_obj = MetaWorkflowRun(run_json)
        cs_obj = checkstatus.CheckStatusFF(run_obj, env)
        status_updates = list(cs_obj.check_running())  # Get all updates
        if status_updates:
            patch_body = status_updates[-1]  # Take most updated
        if patch_body:
            if not ignore_quality_metrics:
                updated_workflow_runs = get_recently_completed_workflow_runs(
                    run_json, patch_body
                )
                quality_metrics_failing = evaluate_quality_metrics(
                    updated_workflow_runs, ff_key
                )
                if quality_metrics_failing:
                    patch_body["final_status"] = "quality metric failed"
            patch_response = ff_utils.patch_metadata(
                patch_body, metawfr_uuid, key=ff_key
            )
            if verbose:
                print(patch_response)


def get_recently_completed_workflow_runs(meta_workflow_run, updated_properties):
    """Compare between original and updated MetaWorkflowRun[json] to find
    UUIDs for all newly finished runs.

    :param meta_workflow_run: Original MetaWorkflowRun[json]
    :type meta_workflow_run: dict
    :param updated_properties: Updated MetaWorkflowRun[json]
    :type updated_properties: dict
    :return: UUIDs of newly completed runs
    :rtype: list(str)
    :raises ValueError: If number of workflow runs on MetaWorkflowRun
        differs from that on the updated properties
    """
    result = []
    original_workflow_runs = meta_workflow_run.get("workflow_runs", [])
    updated_workflow_runs = updated_properties.get("workflow_runs", [])
    if len(original_workflow_runs) != len(updated_workflow_runs):
        raise ValueError(
            "Workflow run length unexpectedly changed during status update."
            "\nOriginal: %s\nUpdated: %s"
            % (original_workflow_runs, updated_workflow_runs)
        )
    for idx in range(len(original_workflow_runs)):
        original_workflow_run = original_workflow_runs[idx]
        updated_workflow_run = updated_workflow_runs[idx]
        original_status = original_workflow_run.get("status")
        updated_status = updated_workflow_run.get("status")
        if updated_status != original_status and updated_status == "completed":
            workflow_run_item = updated_workflow_run.get("workflow_run")
            if workflow_run_item:
                result.append(workflow_run_item)
    return result


def evaluate_quality_metrics(workflow_runs_to_check, ff_key):
    """Retrieve runs and evaluate their output QualityMetrics
    for any failures.

    :param workflow_runs_to_check: WorkflowRun[portal] UUIDs to evaluate
    :type workflow_runs_to_check: list(str)
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :return: Whether any of given WorkflowRuns have failing QCs
    :rtype: bool
    """
    result = False
    embed_fields = ["output_files.value_qc.overall_quality_status"]
    embed_response = make_embed_request(workflow_runs_to_check, embed_fields, ff_key)
    for workflow_run in embed_response:
        quality_metrics_failed = evaluate_workflow_run_quality_metrics(workflow_run)
        if quality_metrics_failed:
            result = True
            break
    return result


def evaluate_workflow_run_quality_metrics(workflow_run):
    """Evaluate WorkflowRun[json] output QualityMetrics for failure.

    NOTE: All status other than FAIL (such as WARN) are considered
    equivalent to PASS here.

    :param workflow_run: WorkflowRun[json] to evaluate
    :type workflow_run: dict
    :return: Whether any ouput QualityMetric has failed
    :rtype: bool
    """
    result = False
    output_files = workflow_run.get("output_files", [])
    for output_file in output_files:
        quality_metric = output_file.get("value_qc", {})
        if quality_metric:
            quality_metric_status = quality_metric.get("overall_quality_status")
            if quality_metric_status == "FAIL":
                result = True
                break
    return result
