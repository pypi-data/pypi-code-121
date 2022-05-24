import datetime
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Built-in configs.
WORKING_DIR = os.environ.get("ANYSCALE_WORKING_DIR", "/home/ray")

# Experimental configs propagated from the cluster config service.
EFS_IP = os.environ.get("ANYSCALE_EXPERIMENTAL_EFS_IP", "")
WORKSPACE_ID = os.environ.get("ANYSCALE_EXPERIMENTAL_WORKSPACE_ID", "")
USERNAME = os.environ.get("ANYSCALE_EXPERIMENTAL_USERNAME", "unknown_user")
BASE_SNAPSHOT = os.environ.get("ANYSCALE_EXPERIMENTAL_BASE_SNAPSHOT") or None

# Other debug configs.
SNAPSHOT_INTERVAL = int(os.environ.get("WORKSPACE_SNAPSHOT_INTERVAL", 300))
EFS_WORKSPACE_DIR = os.environ.get("EFS_WORKSPACE_DIR", "/efs/workspaces")
EFS_JOB_DIR = os.environ.get("EFS_WORKSPACE_DIR", "/efs/jobs")
EFS_OBJECTS_DIR = os.environ.get("EFS_OBJECTS_DIR", "/efs/workspaces/shared_objects")
EFS_CREDS_DIR = os.environ.get("EFS_CREDS_DIR", "/efs/generated_credentials")
RAY_ML_DEV = bool(os.environ.get("RAY_ML_DEV"))
AUTOGC = bool(os.environ.get("AUTOGC_SNAPSHOTS", True))


def optimize_git_repo(directory: str, shared_repo: str) -> None:
    """Optimize the space usage of a git repo by syncing objects to a shared repo.

    Any objects in the source repo will be replicated to the shared repo, and then
    deleted from the source repo. The source repo is setup to reference objects in
    the shared repo via the `.git/objects/info/alternates` mechanism.

    Args:
        directory: The directory to optimize.
        shared_repo: The path that should be used to hold shared objects. This path
            will be created if it doesn't already exist. Multiple checkouts of the
            same repo can share the objects stored in the shared repo.
    """
    start = time.time()
    objects_path = "{}/.git/objects".format(directory)
    if os.path.exists(objects_path):
        if not os.path.exists(shared_repo):
            os.makedirs(os.path.dirname(shared_repo), exist_ok=True)
            # TODO(ekl) it's faster to do a copy of just the objects dir, but it seems
            # we need to git clone in order for alternates to be recognized as valid.
            subprocess.check_call(  # noqa
                "git clone --bare {}/ {}/".format(directory, shared_repo), shell=True,
            )
        shared_objects_dir = os.path.join(shared_repo, "objects")
        subprocess.check_call(  # noqa
            "rsync -a {}/ {}/".format(objects_path, shared_objects_dir), shell=True
        )
        subprocess.check_call("rm -rf {}".format(objects_path), shell=True)  # noqa
        os.makedirs(os.path.join(objects_path, "info"), exist_ok=True)
        with open(os.path.join(objects_path, "info/alternates"), "w") as f:
            f.write("{}\n".format(shared_objects_dir))
    logger.info(
        "Synced git objects for {} to {} in {}s.".format(
            directory, shared_repo, time.time() - start
        )
    )


def create_snapshot_zip(directory: str, auto: bool) -> str:
    """Create a snapshot of the given directory.

    The snapshot will include all git tracked files as well as unstaged
    (but otherwise trackable) files. It will also include the full
    contents of the `.git` folder. To optimize the disk space usage of
    snapshots, call `optimize_git_repo` on the repo directory prior to
    calling `create_snapshot_zip`.

    Args:
        directory: Path of the directory to snapshot.

    Returns:
        Path of a .zip file that contains the snapshot files.
    """

    start = time.time()
    orig = os.path.abspath(os.curdir)
    prefix = "snapshot_{}_".format(datetime.datetime.now().isoformat())
    if auto:
        prefix += "auto_"
    target = tempfile.mktemp(suffix=".zip", prefix=prefix)
    try:
        os.chdir(directory)
        for child in os.listdir("."):
            if os.path.exists(os.path.join(child, ".git")):
                raise ValueError(
                    f"Git repo detected in sub-directory {child}. Please ensure that "
                    "your git repo is cloned in the top-level workspace directory."
                )
        if os.path.exists(".git"):
            subprocess.check_call(  # noqa
                "(git ls-files -co --exclude-standard || true; find .git || true) | "
                f"zip --symlinks -@ -0 -q {target}",
                shell=True,
            )
        else:
            subprocess.check_call(  # noqa
                f"find . | zip --symlinks -@ -0 -q {target}", shell=True,
            )
    finally:
        os.chdir(orig)

    assert os.path.exists(target), target
    logger.info(
        "Created snapshot for {} at {} of size {} in {}s.".format(
            directory, target, os.path.getsize(target), time.time() - start
        )
    )
    return target


def unpack_snapshot_zip(zip_path: str, directory: str) -> None:
    """Unpack a snapshot to the given directory.

    Args:
        zip_path: Path of the zip returned by create_snapshot_zip.
        directory: Output directory to unpack the zip into.
    """

    start = time.time()
    os.makedirs(directory, exist_ok=True)
    subprocess.check_call(  # noqa
        "unzip -X -o -q {} -d {}".format(zip_path, directory), shell=True
    )
    logger.info(
        "Unpacked snapshot {} to {} in {}s.".format(
            zip_path, directory, time.time() - start
        )
    )


def compute_content_hash(zip_path: str) -> bytes:
    """Return the md5 hash of a given zipfile on disk."""
    md5 = subprocess.check_output(  # noqa
        "unzip -p {} | md5sum -b | cut -f1 -d ' '".format(zip_path), shell=True
    )
    md5 = md5.strip()
    return md5


def get_or_create_snapshot_zip(directory: str, auto: bool) -> str:
    """Create a snapshot zip, or return the last snapshot if unchanged.

    A corresponding .md5 file is created alongside the snapshot zip.
    """
    new_zip = create_snapshot_zip(directory, auto)
    new_hash = compute_content_hash(new_zip)
    # Ignore the base snapshot in auto save mode. This means we will always generate
    # a new snapshot within the autosave interval, allowing the base snapshot to be
    # safely garbage collected.
    old_zip = find_latest(ignore_base_snapshot=auto)
    if old_zip:
        try:
            old_hash: Optional[bytes] = open(old_zip + ".md5", "rb").read().strip()
        except Exception:
            logger.warning("Failed to read md5 file")
            old_hash = None
    else:
        old_hash = None
    logger.info("Content hashes {!r} vs {!r}".format(old_hash, new_hash))
    if old_hash == new_hash:
        logger.info("Content hash unchanged, not saving new snapshot.")
        os.unlink(new_zip)
        assert old_zip is not None
        return old_zip
    else:
        with open(new_zip + ".md5", "wb") as f:
            f.write(new_hash)
        return new_zip


def do_snapshot(auto: bool = False):
    """Command to create a snapshot within an Anyscale workspace.

    Can be run via `python -m anyscale.snapshot_util snapshot`.
    """
    workspace_dir = os.path.join(EFS_WORKSPACE_DIR, WORKSPACE_ID)
    snapshot_dir = os.path.join(workspace_dir, "snapshots")
    # TODO(ekl) should we isolate the objects by workspace or repo?
    optimize_git_repo(WORKING_DIR, EFS_OBJECTS_DIR)
    zip = get_or_create_snapshot_zip(WORKING_DIR, auto)

    # If the zip was already on EFS, we're done.
    if zip.startswith(snapshot_dir):
        return

    # Otherwise, move the zip into EFS along with its md5 file.
    os.makedirs(snapshot_dir, exist_ok=True)
    shutil.move(zip, os.path.join(snapshot_dir, os.path.basename(zip)))
    shutil.move(
        zip + ".md5", os.path.join(snapshot_dir, os.path.basename(zip) + ".md5")
    )
    shutil.copy(
        os.path.expanduser("~/.bash_history"),
        os.path.join(workspace_dir, ".bash_history"),
    )
    if AUTOGC:
        gc_snapshots()


def gc_snapshots() -> None:
    """Garbage collect snapshots older than 1 hr.

    This is safe since when we clone a workspace, the autosave loop will generate a
    new snapshot, so the clone will be decoupled from the original.
    """
    workspace_dir = os.path.join(EFS_WORKSPACE_DIR, WORKSPACE_ID)
    snapshot_dir = os.path.join(workspace_dir, "snapshots")
    if not os.path.exists(snapshot_dir):
        return
    snapshots = sorted([x for x in os.listdir(snapshot_dir) if x.endswith(".zip")])
    # Never GC the latest snapshot.
    snapshots = snapshots[:-1]
    horizon = datetime.datetime.now() - datetime.timedelta(hours=1)
    prefix = "snapshot_{}_".format(horizon.isoformat())
    # GC snapshots older than 1 hour.
    for snapshot in snapshots:
        if snapshot < prefix:
            full_path = os.path.join(snapshot_dir, snapshot)
            md5 = full_path + ".md5"
            logger.info("Deleting old snapshot {}".format(full_path))
            try:
                os.unlink(full_path)
                os.unlink(md5)
            except Exception:
                logger.exception("Failed to delete snapshot")


def find_latest(ignore_base_snapshot: bool) -> Optional[str]:
    """Return path to latest .zip snapshot, if it exists."""
    workspace_dir = os.path.join(EFS_WORKSPACE_DIR, WORKSPACE_ID)
    snapshot_dir = os.path.join(workspace_dir, "snapshots")
    if not os.path.exists(snapshot_dir):
        if ignore_base_snapshot:
            return None
        else:
            return find_base_snapshot()
    snapshots = sorted([x for x in os.listdir(snapshot_dir) if x.endswith(".zip")])
    if not snapshots:
        return find_base_snapshot()
    return os.path.join(snapshot_dir, snapshots[-1])


def find_base_snapshot() -> Optional[str]:
    if not BASE_SNAPSHOT:
        return None
    try:
        base_data = json.loads(BASE_SNAPSHOT)
    except Exception:
        logger.exception("Failed to parse base snapshot info")
        return None

    # Jobs snapshot
    if "from_job" in base_data:
        job_id = base_data["from_job"]["job_id"]
        if not job_id:
            logger.info("Invalid base snapshot, no job id")
            return None
        logger.info(f"Base snapshot from job {job_id}")
        return os.path.join(EFS_JOB_DIR, job_id, "working_dir.zip")

    # Workspace snapshot
    if "from_workspace" in base_data:
        workspace_id = base_data["from_workspace"]["workspace_id"]
        iso_time = base_data["from_workspace"]["iso_time"]
        if not workspace_id or not iso_time:
            logger.info("Invalid base snapshot, no workspace id or time")
            return None
        logger.info(f"Base snapshot from workspace {workspace_id} and {iso_time}")
        snapshot_dir = os.path.join(EFS_WORKSPACE_DIR, workspace_id, "snapshots")
        snapshot_time = "snapshot_{}_".format(iso_time)
        if not os.path.exists(snapshot_dir):
            return None
        # Find the latest matching snapshot before the time stamp
        snapshots = sorted(
            [
                x
                for x in os.listdir(snapshot_dir)
                if x.endswith(".zip") and x < snapshot_time
            ]
        )
        if not snapshots:
            return None
        return os.path.join(snapshot_dir, snapshots[-1])

    return None


def restore_latest():
    """Command to restore the latest snapshot within an Anyscale workspace.

    Can be run via `python -m anyscale.snapshot_util restore`.
    """
    latest = find_latest(ignore_base_snapshot=False)
    logger.info(f"Latest snapshot found was {latest}")
    if not latest:
        return
    workspace_dir = os.path.join(EFS_WORKSPACE_DIR, WORKSPACE_ID)
    unpack_snapshot_zip(latest, WORKING_DIR)
    hist = os.path.join(workspace_dir, ".bash_history")
    if os.path.exists(hist):
        shutil.copy(hist, os.path.expanduser("~/.bash_history"))


def checkpoint_job(job_id, runtime_env: Dict[str, Any]) -> Dict[str, Any]:
    """Checkpoint the runtime environment and working directory of a job.

    This function will modify runtime_env to point to the new working
    directory on EFS and return the modified runtime_env.
    """
    # For some reason, in a job Ray first calls the env_hook with runtime_env = None
    # and then a second time with the proper runtime_env -- do nothing in the former case.
    if not runtime_env:
        return runtime_env
    dest_dir = os.path.join(EFS_JOB_DIR, job_id)
    os.makedirs(dest_dir, exist_ok=True)
    if "working_dir" in runtime_env and runtime_env["working_dir"].endswith(".zip"):
        # We're a job, also save a replica of the zip in EFS so the job can be cloned
        # as a workspace at a later time.
        working_dir = os.path.join(dest_dir, "working_dir.zip")
        import urllib.request

        urllib.request.urlretrieve(runtime_env["working_dir"], working_dir)
        runtime_env["working_dir"] = working_dir
    # Save the runtime_env to be used later.
    with open(os.path.join(dest_dir, "runtime_env.json"), "w") as f:
        f.write(json.dumps(runtime_env))
    return runtime_env


def setup_ml_dev(runtime_env):
    """Env hook for Ray ML development.

    This enables development for Ray ML libraries, assuming the working dir is the
    entire Ray repo, by replicating library changes to all nodes in the cluster via
    runtime_env py_modules.

    To enable this hook, set RAY_ML_DEV=1.
    """
    if not runtime_env:
        runtime_env = {}
    import ray

    sys_ray_module = os.path.dirname(ray.__file__)
    local_ray_module = os.path.join(WORKING_DIR, "python/ray")
    if not os.path.exists(local_ray_module):
        logger.info("RAY_ML_DEV was set, but could not find the local ray module.")
        return runtime_env
    tmp_module = "/tmp/ray_tmp_module/ray"
    shutil.rmtree(tmp_module, ignore_errors=True)
    shutil.copytree(sys_ray_module, tmp_module)
    # TODO(ekl) keep this in sync with setup-dev.py
    LIB_DIRS = [
        "rllib",
        "ml",
        "tune",
        "serve",
        "train",
        "data",
        "experimental",
        "util",
        "workflow",
        "cloudpickle",
        "_private",
        "internal",
        "node.py",
        "cluster_utils.py",
        "ray_constants.py",
    ]
    for lib_dir in LIB_DIRS:
        src = os.path.join(local_ray_module, lib_dir)
        dst = os.path.join(tmp_module, lib_dir)
        logger.info(f"Copying files from {src} to {dst}.")
        if os.path.isdir(src):
            shutil.rmtree(dst)
            shutil.copytree(os.path.join(local_ray_module, lib_dir), dst)
        else:
            shutil.copy(src, dst)
    if "py_modules" not in runtime_env:
        runtime_env["py_modules"] = []
    runtime_env["py_modules"].append(tmp_module)
    return runtime_env


def env_hook(runtime_env):
    """Env hook for including the working dir in the runtime_env by default.

    This should be set as `RAY_RUNTIME_ENV_HOOK=anyscale.snapshot_util.env_hook`.
    """
    if "ANYSCALE_EXPERIMENTAL_JOB_ID" in os.environ:
        return checkpoint_job(os.environ["ANYSCALE_EXPERIMENTAL_JOB_ID"], runtime_env)
    if not runtime_env:
        runtime_env = {}
    if not runtime_env.get("working_dir"):
        runtime_env["working_dir"] = WORKING_DIR
    if not runtime_env["working_dir"].endswith(".zip"):
        workspace = runtime_env["working_dir"]
        optimize_git_repo(workspace, EFS_OBJECTS_DIR)
        zipfile = get_or_create_snapshot_zip(workspace, auto=False)
        # Move the zip file to a consistent path so that we don't leak zip files as
        # jobs are run over time. This isn't thread safe: we assume one job at a time.
        # Note that the zip file isn't needed after the job starts successfully.
        final_path = "/tmp/ray_latest_runtime_env.zip"
        shutil.move(zipfile, final_path)
        os.unlink(zipfile + ".md5")
        runtime_env["working_dir"] = final_path
    if RAY_ML_DEV:
        runtime_env = setup_ml_dev(runtime_env)
    logger.info("Updated runtime env to {}".format(runtime_env))
    return runtime_env


def setup_credentials():
    """Command to create SSH credentials for the workspace.

    We generate unique Anyscale SSH keys for each username. This call will inject
    the key for the current user into the workspace.
    """
    private_key = os.path.join(EFS_CREDS_DIR, USERNAME, "id_rsa")
    public_key = os.path.join(EFS_CREDS_DIR, USERNAME, "id_rsa.pub")
    os.makedirs("/home/ray/.ssh", exist_ok=True)
    if os.path.exists(private_key):
        # Copy down from EFS.
        shutil.copy(private_key, "/home/ray/.ssh/id_rsa")
        shutil.copy(public_key, "/home/ray/.ssh/id_rsa.pub")
    else:
        # Copy up to EFS.
        subprocess.check_call(  # noqa
            "echo y | ssh-keygen -t rsa -f /home/ray/.ssh/id_rsa -N ''", shell=True
        )
        os.makedirs(os.path.dirname(private_key), exist_ok=True)
        shutil.copy("/home/ray/.ssh/id_rsa", private_key)
        shutil.copy("/home/ray/.ssh/id_rsa.pub", public_key)


def setup_nfs():
    """Setup EFS mounts in the container."""
    COMMANDS = [
        # TODO: move dep install to base image
        "sudo apt-get update",
        "sudo apt-get install -y nfs-common zip unzip awscli",
        "sudo mkdir -p /efs",
        "sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,"
        f"timeo=600,retrans=2,noresvport {EFS_IP}:/ /efs",
        "sudo mkdir -p /efs",
        f"mkdir -p /efs/workspaces/{WORKSPACE_ID}/cluster_storage",
        f"sudo ln -sf /efs/workspaces/{WORKSPACE_ID}/cluster_storage "
        "/mnt/cluster_storage",
        "mkdir -p /efs/shared_storage",
        "sudo ln -sf /efs/shared_storage /mnt/shared_storage",
    ]
    for cmd in COMMANDS:
        try:
            subprocess.check_call(cmd, shell=True)  # noqa
        except Exception:
            logger.exception(f"Error running {cmd}")


def setup_container(ray_params: Any, is_head: bool):
    """Setup the container synchronously prior to Ray start.

    This handles (1) mounting network storage, (2) restoring workspace data, and
    (3) restoring credentials. This is intended to be triggered via the Ray start hook,
    i.e., ``RAY_START_HOOK=anyscale.snapshot_util.setup_container``.
    """
    if os.path.exists("/tmp/initialized"):
        logger.info("Init previously completed, skipping.")
        return
    if not EFS_IP:
        logger.info("No EFS IP configured, skipping workspace container setup.")
    else:
        try:
            setup_nfs()
        except Exception:
            logger.exception("Failed to setup NFS")
        if not WORKSPACE_ID:
            logger.info("No workspace id configured, skipping workspace restore.")
        elif not is_head:
            logger.info("Not head node, skipping workspace restore.")
        else:
            try:
                restore_latest()
            except Exception:
                logger.exception("Failed to restore workspace")
            try:
                setup_credentials()
            except Exception:
                logger.exception("Failed to setup SSH credentials")
    with open("/tmp/initialized", "w") as f:
        f.write("ok")


def autosnapshot_loop():
    if not WORKSPACE_ID:
        logger.info("Workspaces disabled.")
        return
    logger.info("Started autosnapshot loop with interval {}".format(SNAPSHOT_INTERVAL))
    while True:
        time.sleep(SNAPSHOT_INTERVAL)
        do_snapshot(auto=True)


if __name__ == "__main__":
    import sys

    if sys.argv[1] == "snapshot":
        do_snapshot()
    elif sys.argv[1] == "autosnapshot":
        autosnapshot_loop()
    elif sys.argv[1] == "restore":
        restore_latest()
    elif sys.argv[1] == "gc":
        gc_snapshots()
    elif sys.argv[1] == "setup_credentials":
        setup_credentials()
    elif sys.argv[1] == "setup_container":
        setup_container(None, True)
    else:
        print("unknown arg")
