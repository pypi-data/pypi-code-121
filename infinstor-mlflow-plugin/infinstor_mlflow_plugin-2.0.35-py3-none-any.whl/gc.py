from mlflow.tracking import _get_store
from mlflow.entities.lifecycle_stage import LifecycleStage
import sys

def gc(backend_store_uri, run_ids):
    """
    Permanently delete runs in the `deleted` lifecycle stage from the specified backend store.
    This command deletes all artifacts and metadata associated with the specified runs.
    """
    backend_store = _get_store(backend_store_uri, None)
    if not hasattr(backend_store, "_hard_delete_run"):
        raise MlflowException(
            "This cli can only be used with a backend that allows hard-deleting runs"
        )
    if not run_ids:
        run_ids = backend_store._get_deleted_runs()
    else:
        run_ids = run_ids.split(",")

    for run_id in run_ids:
        run = backend_store.get_run(run_id)
        if run.info.lifecycle_stage != LifecycleStage.DELETED:
            raise MlflowException(
                "Run {} is not in `deleted` lifecycle stage. Only runs in "
                "`deleted` lifecycle stage can be deleted.".format(run_id)
            )
        backend_store._hard_delete_run(run_id)
        print("Run with ID %s has been permanently deleted." % str(run_id))


def main():
    if (len(sys.argv) > 1):
        a = sys.argv[1]
    else:
        a = None
    gc('infinstor://infinstor.com/', a)

if __name__ == "__main__":
    if (main()):
        exit(0)
    else:
        exit(255)
