#!/usr/bin/env python3

################################################
#
#   Function to import from old
#       MetaWorkflowRun[portal]
#
################################################
import json

from dcicutils import ff_utils

from magma.metawflrun import MetaWorkflowRun
from magma_ff.create_metawfr import MetaWorkflowRunFromSampleProcessing
from magma_ff.runupdate import RunUpdate
from magma_ff.utils import make_embed_request


################################################
#   Functions
################################################
def import_metawfr(
    meta_workflow_uuid,
    metawfr_uuid,
    sample_processing_uuid,
    steps_name,
    ff_key,
    post=False,
    patch=False,
    verbose=False,
    expect_family_structure=True,
):
    """Create new MetaWorkflowRun[json] from existing MetaWorkflowRun[portal].
    Import specified steps. If post, POST the MetaWorkflowRun[json] to portal
    and PATCH SampleProcessing[portal].

    :param meta_workflow_uuid: MetaWorkflow[portal] UUID
    :type meta_workflow_uuid: str
    :param metawfr_uuid: Existing MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param sample_processing_uuid: SampleProcessing[portal] UUID
    :type sample_processing_uuid: str
    :param steps_name: Names for the steps to import from existing
        MetaWorkflowRun[portal]
    :type steps_name: list(str)
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param post: Whether to POST the new MetaWorkflowRun[json]
    :type post: bool
    :param patch: Whether to PATCH new MetaWorkflowRun[json] to
        SampleProcessing[portal]
    :type patch: bool
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param expect_family_structure: Whether a family structure is
        expected for the SampleProcessing
    :type expect_family_structure: bool
    :return: New MetaWorkflowRun[json]
    :rtype: dict
    """
    run_json_to_import = ff_utils.get_metadata(
        metawfr_uuid, add_on="frame=raw", key=ff_key
    )
    run_obj_to_import = MetaWorkflowRun(run_json_to_import)
    meta_workflow_run_creator = MetaWorkflowRunFromSampleProcessing(
        sample_processing_uuid,
        meta_workflow_uuid,
        ff_key,
        expect_family_structure=expect_family_structure,
    )
    new_meta_workflow_run = meta_workflow_run_creator.meta_workflow_run
    run_obj = MetaWorkflowRun(new_meta_workflow_run)
    runupd_obj = RunUpdate(run_obj)
    updated_meta_workflow_run = runupd_obj.import_steps(run_obj_to_import, steps_name)
    # A little hacky, but replace the MWFR on the creator class to access POST and
    # PATCH methods
    meta_workflow_run_creator.meta_workflow_run = updated_meta_workflow_run
    if post:
        post_response = meta_workflow_run_creator.post_meta_workflow_run()
        if verbose:
            print(post_response)
        update_success, update_errors = add_new_meta_workflow_run_uuid_to_copied_items(
            updated_meta_workflow_run, ff_key
        )
        if verbose:
            print(
                "Updated %s copied MWFR output items with new MWFR UUID"
                % len(update_success)
            )
        if update_errors:  # Not raising Exception here so SampleProcessing PATCH occurs
            print(
                "WARNING: %s items were not updated with new MWFR UUID"
                % len(update_errors)
            )
            print("UUIDs and errors:")
            print(json.dumps(update_errors, indent=4))
    if patch:
        patch_response = meta_workflow_run_creator.patch_sample_processing()
        if verbose:
            print(patch_response)
    return updated_meta_workflow_run


def add_new_meta_workflow_run_uuid_to_copied_items(meta_workflow_run, auth_key):
    """For all output items copied, add new MWFR to
    Item.associated_meta_workflow_runs.

    :param meta_workflow_run: MetaWorkflowRun properties
    :type meta_workflow_run: dict
    :param auth_key: Portal authorization key
    :type auth_key: dict
    :return: Successful PATCHes and items with errors on PATCH
    :rtype: tuple(list, dict)
    """
    success = []
    errors = {}
    patch_items_and_bodies = {}
    workflow_run_uuids = []
    workflow_run_embed_fields = [
        "uuid",
        "associated_meta_workflow_runs",
        "output_files.value.uuid",
        "output_files.value.associated_meta_workflow_runs",
        "output_files.value_qc.uuid",
        "output_files.value_qc.associated_meta_workflow_runs",
    ]
    meta_workflow_run_uuid = meta_workflow_run.get("uuid")
    workflow_runs = meta_workflow_run.get("workflow_runs", [])
    for item in workflow_runs:
        workflow_run_uuid = item.get("workflow_run")
        if workflow_run_uuid:
            workflow_run_uuids.append(workflow_run_uuid)
    embed_result = make_embed_request(
        workflow_run_uuids, workflow_run_embed_fields, auth_key
    )
    for result in embed_result:
        add_to_patch(patch_items_and_bodies, result, meta_workflow_run_uuid)
        output_files = result.get("output_files", [])
        for output_file in output_files:
            file_item = output_file.get("value")
            add_to_patch(patch_items_and_bodies, file_item, meta_workflow_run_uuid)
            qc_file_item = output_file.get("value_qc")
            add_to_patch(patch_items_and_bodies, qc_file_item, meta_workflow_run_uuid)
    for item_to_patch, patch_body in patch_items_and_bodies.items():
        try:
            ff_utils.patch_metadata(patch_body, obj_id=item_to_patch, key=auth_key)
            success.append(item_to_patch)
        except Exception as e:
            errors[item_to_patch] = str(e)
    return success, errors


def add_to_patch(patch_dict, item_properties, meta_workflow_run_uuid):
    """Add item UUID and updated associated_meta_workflow_runs PATCH
    body to patch_dict.

    :param patch_dict: Dictionary with key, value pairs of item UUIDs
        and corresponding PATCH bodies
    :type patch_dict: dict
    :param item_properties: Item metadata
    :type item_properties: dict
    :param meta_workflow_run_uuid: MetaWorkflowRun UUID to add to
        item's associated_meta_workflow_runs
    :type meta_workflow_run_uuid: str
    """
    if item_properties:
        item_uuid = item_properties.get("uuid")
        item_associated_meta_workflow_runs = item_properties.get(
            "associated_meta_workflow_runs", []
        )
        item_associated_meta_workflow_runs.append(meta_workflow_run_uuid)
        if item_uuid:
            patch_dict[item_uuid] = {
                "associated_meta_workflow_runs": item_associated_meta_workflow_runs
            }
