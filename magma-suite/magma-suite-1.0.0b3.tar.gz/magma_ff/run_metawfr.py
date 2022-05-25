################################################
#
#   Function to run MetaWorkflowRun[portal]
#       with tibanna and patch metadata
#
################################################
from dcicutils import ff_utils
from tibanna_ffcommon.core import API

from magma_ff import inputgenerator as ingen
from magma_ff.metawfl import MetaWorkflow
from magma_ff.metawflrun import MetaWorkflowRun
from magma_ff.utils import check_status, make_embed_request


################################################
#   Functions
################################################
def run_metawfr(
    metawfr_uuid,
    ff_key,
    verbose=False,
    sfn="tibanna_zebra",
    env="fourfront-cgap",
    maxcount=None,
    valid_status=None,
):
    """Launch pending runs on MetaWorkflowRun[portal] via tibanna.
    PATCH MetaWorkflowRun[portal] with updates.

    Can double-check MetaWorkflowRun.final_status is valid since
    grabbing item from Postgres here.

    :param metawfr_uuid: MetaWorkflowRun[portal] UUID
    :type metawfr_uuid: str
    :param ff_key: Portal authorization key
    :type ff_key: dict
    :param sfn: Step function name
    :type sfn: str
    :param env: Environment name
    :type env: str
    :param maxcount: Maximum number of WorkflowRuns to create for the
        MetaWorkflowRun
    :type maxcount: int
    :param verbose: Whether to print the POST response
    :type verbose: bool
    :param valid_status: Status considered valid for MetaWorkflowRun
        final_status property
    :type valid_status: list(str) or None
    """
    perform_action = True
    embed_fields = ["*", "meta_workflow.*"]
    meta_workflow_run = make_embed_request(
        metawfr_uuid, embed_fields, ff_key, single_item=True
    )
    meta_workflow = meta_workflow_run.get("meta_workflow")
    perform_action = check_status(meta_workflow_run, valid_status)
    if perform_action:
        run_obj = MetaWorkflowRun(meta_workflow_run)
        wfl_obj = MetaWorkflow(meta_workflow)
        ingen_obj = ingen.InputGenerator(wfl_obj, run_obj)
        in_gen = ingen_obj.input_generator(env)
        count = 0
        for input_json, patch_dict in in_gen:
            API().run_workflow(input_json=input_json, sfn=sfn)  # Start tibanna run
            res_post = ff_utils.patch_metadata(patch_dict, metawfr_uuid, key=ff_key)
            if verbose:
                print(res_post)
            count += 1
            if maxcount and count >= maxcount:
                break
