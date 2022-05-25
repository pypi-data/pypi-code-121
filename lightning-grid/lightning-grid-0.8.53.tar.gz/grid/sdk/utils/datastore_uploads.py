import concurrent.futures
import datetime
import math
import os
import signal
import time
import warnings
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from hashlib import blake2b
from pathlib import Path
from threading import Event
from typing import List, Optional, TYPE_CHECKING, Dict, Union

import requests
import ujson
from dataclasses_json import dataclass_json
from requests.adapters import HTTPAdapter
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TaskID, TransferSpeedColumn
from rich.status import Status
from urllib3 import Retry

from grid.sdk.user_messaging import errors

try:
    from rich.console import RenderGroup as Group
except ImportError:
    from rich.console import Group

from grid.metadata import __version__
from grid.sdk import env
from grid.sdk.rest.datastores import (
    datastore_upload_object_from_data_file,
    create_presigned_urls,
    complete_presigned_url_upload,
    mark_datastore_upload_complete,
)

if TYPE_CHECKING:
    from grid.sdk.rest import GridRestClient

_SEC = 1
_MIN = 60 * _SEC
_HOUR = 60 * _MIN
_DAY = 24 * _HOUR

_MAX_FILE_SIZE = 10_000 * env.MAX_BYTES_PER_FILE_PART_UPLOAD  # s3 limit is 10,000 parts

warnings.simplefilter("ignore")

# -------------- interrupt handling ---------------

done_event = Event()
received_signal = None


def handle_termination_signal(signum, frame):
    global received_signal
    done_event.set()
    received_signal = signum


def wrap_signals(fn):
    def wrapper(*args, **kwargs):

        global received_signal
        prev_sigint_handler = signal.signal(signal.SIGINT, handle_termination_signal)
        prev_sigterm_handler = signal.signal(signal.SIGTERM, handle_termination_signal)

        try:
            fn(*args, **kwargs)
        except RuntimeError as e:
            print(e)

        signal.signal(signal.SIGTERM, prev_sigterm_handler)
        signal.signal(signal.SIGINT, prev_sigint_handler)
        if received_signal is not None:
            signal.raise_signal(received_signal)

    return wrapper


# ----------------- data structures ----------------


@dataclass
class PBar:
    p_upload_bytes: Progress = Progress(
        TextColumn("[progress.description]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
    )

    p_upload_files: Progress = Progress(
        TextColumn("[progress.description]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "{task.completed} / {task.total} Parts Completed",
    )

    p_finalize: Progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TextColumn("{task.completed} / {task.total} File Parts"),
    )

    action_status: Status = Status("[bold yellow] Initializing Upload")

    upload_bytes_task_id: TaskID = p_upload_bytes.add_task("Upload Progress (Data Bytes)")
    upload_files_task_id: TaskID = p_upload_files.add_task("Upload Progress (File Parts)")
    finalize_task_id: TaskID = p_finalize.add_task("Finalizing Upload", visible=False)

    # group of progress bars;
    # some are always visible, others will disappear when progress is complete
    progress_group: Group = Group(
        Panel(Group(p_upload_files, p_upload_bytes, p_finalize)),
        action_status,
    )

    upload_bytes_beginning_advance: int = None
    upload_bytes_total: int = None
    upload_files_beginning_advance: int = None
    upload_files_total: int = None
    finalize_beginning_advance: int = None
    finalize_total: int = None

    status_text_initializing: str = "[bold yellow] Indexing Datastore Files"
    status_text_uploading: str = "[bold blue] Uploading Data"
    status_text_saving: str = "[bold yellow] Checkpointing Current Upload Progress"
    status_text_finalizing: str = "[bold blue] Finalizing Upload"
    status_text_done: str = "[bold green] Done!"

    def __post_init__(self):
        self.p_upload_bytes.refresh()
        self.p_upload_files.refresh()
        self.p_finalize.refresh()

    def setup_progress_meter(self, work: 'Work'):
        current_part_progress, total_part_count = 0, 0
        current_byte_progress, total_byte_count = 0, 0
        current_finalize_progress, total_finalize_files = 0, 0

        for file in work.files.values():
            total_byte_count += file.size_bytes
            total_part_count += int(file.part_count)
            total_finalize_files += 1

            if file.is_uploaded:
                current_byte_progress += file.size_bytes
                current_part_progress += int(file.part_count)
            if file.is_marked_complete:
                current_finalize_progress += 1

        self.upload_bytes_beginning_advance = current_byte_progress
        self.upload_bytes_total = total_byte_count
        self.upload_files_beginning_advance = current_part_progress
        self.upload_files_total = total_part_count
        self.finalize_beginning_advance = current_finalize_progress
        self.finalize_total = total_finalize_files

        self.p_upload_bytes.update(
            self.upload_bytes_task_id, advance=self.upload_bytes_beginning_advance, total=int(self.upload_bytes_total)
        )
        self.p_upload_files.update(
            self.upload_files_task_id, advance=self.upload_files_beginning_advance, total=self.upload_files_total
        )
        self.p_finalize.update(
            self.finalize_task_id, advance=self.finalize_beginning_advance, total=self.finalize_total, visible=False
        )


@dataclass_json
@dataclass
class UploadTask:
    data_file_local_id: str
    part_number: str
    read_offset_bytes: int  # beginning position to seek to in the file
    read_range_bytes: int  # how many bytes to read after the starting position
    url: str
    etag: Optional[str] = None


@dataclass_json
@dataclass
class DataFile:
    absolute_path: str  # path to file to upload on client
    relative_file_name: str  # key of the object in the datastore (relative path from datastore source at creation)
    size_bytes: int  # total size of the file in bytes
    local_id: str  # uuid generated when the file contents are first read.

    part_count: Optional[int] = None
    upload_id: Optional[str] = None
    expiry_time: Optional[int] = None  # unix timestamp when presigned url will expire.
    tasks: List[UploadTask] = field(default_factory=list)

    is_uploaded: bool = False
    is_marked_complete: bool = False


@dataclass_json
@dataclass
class Work:
    datastore_id: str
    datastore_name: str
    datastore_version: str
    cluster_id: str
    source: str
    creation_timestamp: int  # unix timestamp of the initial creation time
    grid_cli_version: str = __version__
    files: Dict[str, DataFile] = field(default_factory=dict)  # files contained in the datastore

    def check_for_modified_files(self) -> List[DataFile]:
        """Find all files which exist in self but which have changed or been removed from other.

        This method calculates the difference between two sets of work. For the sakke of simplicity
        we do not detect if files within the original datastore source dir have been added which were
        not included in the initial work state; nor do we report the difference type of each file
        that is different in the original work from the current state (as in, we do not report if
        a difference is due to a file being changed or if it is due to the file being removed / moved
        from the recorded filesystem path).
        """
        current_filesystem_work_state = initialize_upload_work(
            name=self.datastore_name,
            version=self.datastore_version,
            datastore_id=self.datastore_id,
            cluster_id=self.cluster_id,
            creation_timestamp=self.creation_timestamp,
            source_path=str(self.source),
        )
        differences = []
        different_in_self = set(self.files.keys()).difference(current_filesystem_work_state.files.keys())
        for difference in different_in_self:
            differences.append(self.files[difference])
        return differences


# ------------------ serialization / de-serialization --------------------


def load_datastore_work_state(grid_dir: Path, datastore_id: str) -> Work:
    state_file = grid_dir.joinpath("datastores", f"{datastore_id}.json")
    if not state_file.exists():
        raise FileNotFoundError(f"work state file does not exist at: {state_file}")
    work = Work.from_dict(ujson.loads(state_file.read_text()))
    if work.grid_cli_version != __version__:
        raise RuntimeError(
            "An incomplete datastore upload was dected which was created from a different version "
            "of the grid CLI. The incomplete work has been invalidated and the datastore must be "
            "re-uploaded in full as part of a new `grid datastore create` command."
        )
    return work


def _save_work_state(grid_dir: Path, work: Work) -> None:
    datastores_dir = grid_dir.joinpath("datastores")
    datastores_dir.mkdir(parents=True, exist_ok=True)
    state_file = datastores_dir.joinpath(f"{work.datastore_id}.json")
    state_file.touch()
    state_file.write_text(ujson.dumps(asdict(work)))


def remove_datastore_work_state(grid_dir: Path, datastore_id: str) -> None:
    state_file = grid_dir / "datastores" / f"{datastore_id}.json"
    if not state_file.exists():
        raise FileNotFoundError(f"could not find / remove work state file: {state_file}")
    os.remove(str(state_file.absolute()))


def find_incomplete_datastore_upload(grid_dir: Path) -> Union[str, None]:
    """Finds an incomplete upload in the grid dir and returns the datastore id if it exsists, else None"""
    datastores_dir = grid_dir.joinpath("datastores")
    datastores_dir.mkdir(parents=True, exist_ok=True)
    for work_state_file in list(datastores_dir.iterdir()):
        if not work_state_file.is_file() or not work_state_file.name.endswith(".json"):
            continue
        datastore_id = work_state_file.name.rstrip(".json")
        return datastore_id
    return None


# ----------------------- initialization ------------------------------

_hasher = blake2b(digest_size=15)


def _calculate_file_local_id(f: Path) -> str:
    """Calculate a deterministic / unique identifier for a file in the work index.

    This calculates a blake2b digest based off the file path, mod-time, & file size.
    This is done instead of simply generating a UUID for the key in order to allow
    incomplete file upload `Work` dicts to be compared to a resumed datastore
    upload work state simply by checking if all the keys in the dictionary are
    the same (an op resolving to a simple set difference on dict key pairs rather
    than some sort of  iteration -> sort -> attr lookup -> set comparison method)
    """
    h = _hasher.copy()
    h.update(str(f.resolve()).encode('utf-8'))
    h.update(str(f.stat().st_mtime_ns).encode('utf-8'))
    h.update(str(f.stat().st_size).encode('utf-8'))
    return h.hexdigest()


def initialize_upload_work(
    name: str,
    datastore_id: str,
    cluster_id: str,
    creation_timestamp: int,
    source_path: str,
    version: str,
) -> Work:
    rel_path = Path(source_path)
    abs_path = rel_path.absolute()
    if not abs_path.exists():
        raise OSError(f"the datastore upload source path: {source_path} does not exist")

    all_work = Work(
        datastore_name=name,
        datastore_id=datastore_id,
        cluster_id=cluster_id,
        creation_timestamp=creation_timestamp,
        source=str(abs_path),
        datastore_version=version,
    )

    # handle a single file upload case.
    if abs_path.is_file():
        local_id = _calculate_file_local_id(abs_path)
        file_size = abs_path.stat().st_size
        if file_size >= _MAX_FILE_SIZE:
            raise RuntimeError(
                f"file {abs_path.absolute()} exceeds the maximum file size for "
                f"uploads to grid datastores. please contact support @grid.ai"
                f"for assistance"
            )
        all_work.files[local_id] = DataFile(
            absolute_path=str(abs_path.resolve()),
            relative_file_name=abs_path.name,
            size_bytes=file_size,
            local_id=local_id,
            part_count=max(1, math.ceil(file_size / env.MAX_BYTES_PER_FILE_PART_UPLOAD))
        )
        return all_work

    # if the source_path is a directory...
    for f in abs_path.glob("**/*"):
        if f.is_dir():
            continue

        if f.is_symlink():
            warnings.warn(f"Cannot upload symlinked files. Skipping: {str(f)}", category=UserWarning)
            continue

        local_id = _calculate_file_local_id(f)
        file_size = f.stat().st_size
        if file_size >= _MAX_FILE_SIZE:
            raise RuntimeError(
                f"file {f.absolute()} exceeds the maximum file size for "
                f"uploads to grid datastores. please contact support @grid.ai"
                f"for assistance."
            )

        all_work.files[local_id] = DataFile(
            absolute_path=str(f.resolve()),
            relative_file_name=str(f.relative_to(abs_path)),
            size_bytes=file_size,
            local_id=local_id,
            part_count=max(1, math.ceil(file_size / env.MAX_BYTES_PER_FILE_PART_UPLOAD))
        )

    return all_work


# ----------------------- perform upload -----------------------------


def _get_next_upload_batch(work: Work) -> List[DataFile]:
    num_bytes, num_files = 0, 0
    next_batch = []
    for file in work.files.values():
        if file.is_uploaded:
            continue
        next_batch.append(file)
        num_bytes += file.size_bytes
        num_files += 1
        # ordering is important here in case there is a very large
        # files which exceeds the MAX_BYTES_PER_BATCH_UPLOAD limit.
        if num_bytes > env.MAX_BYTES_PER_BATCH_UPLOAD or num_files >= env.MAX_FILES_PER_UPLOAD_BATCH:
            break

    return next_batch


def _do_upload(session: requests.Session, file_path: Path, task: UploadTask, progress_bar: PBar) -> UploadTask:
    """Do upload, fill ETag value in UploadTask
    """
    if done_event.is_set():
        return task

    try:
        with file_path.open("rb") as file:
            file.seek(task.read_offset_bytes)
            data = file.read(task.read_range_bytes)
            bytes_read = len(data)

        response = session.put(task.url, data=data)
        if 'ETag' not in response.headers:
            raise ValueError(f"Unexpected response from S3, response: {response.content}")
        task.etag = str(response.headers['ETag']).strip('"')
    except FileNotFoundError:
        # don't error and allow the progress bar to continue updating as expected.
        bytes_read = task.read_range_bytes

    progress_bar.p_upload_bytes.update(progress_bar.upload_bytes_task_id, advance=bytes_read)
    progress_bar.p_upload_files.update(progress_bar.upload_files_task_id, advance=1)
    return task


def _upload_next_batch(c: 'GridRestClient', work: Work, progress_bar: PBar) -> Dict[str, DataFile]:
    upload_objects = []
    batch = _get_next_upload_batch(work)
    if len(batch) == 0:
        return {}

    for file in batch:
        up_obj = datastore_upload_object_from_data_file(file)
        upload_objects.append(up_obj)

    responses = create_presigned_urls(
        c=c,
        cluster_id=work.cluster_id,
        datastore_id=work.datastore_id,
        upload_objects=upload_objects,
    )

    batch_files = {}
    for resp, file in zip(responses, batch):
        file.upload_id = resp.upload_id
        file.expiry_time = resp.expiry_time
        file.part_count = resp.part_count
        for idx, url in enumerate(resp.urls):
            offset = idx * env.MAX_BYTES_PER_FILE_PART_UPLOAD
            file.tasks.append(
                UploadTask(
                    data_file_local_id=file.local_id,
                    part_number=url.part_number,
                    url=url.url,
                    read_offset_bytes=offset,
                    read_range_bytes=env.MAX_BYTES_PER_FILE_PART_UPLOAD,
                )
            )
        batch_files[file.local_id] = file

    # We can use a with statement to ensure threads are cleaned up promptly
    #
    # The algorithm dictating backoff factor is as follows:
    #
    # {backoff factor} * (2 ** ({number of total retries} - 1))
    #
    # For example, if the backoff factor is set to:
    #
    # 1 second the successive sleeps will be 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256.
    # 2 seconds - 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
    # 10 seconds - 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560
    #
    # To find the total time spent before erroring, sum up backoff factors for
    # each sleep iterations up to the total number of retries (max_retries)
    retries = Retry(
        total=8,
        # status_forcelist retry codes
        # ----------------------------
        # 104: connection reset by peer can occur when 307 redirect requests aren't received quickly enough.
        # 429: too many requests (just need to slow down... exponential backoff handles this)
        # 500, 502, 503, 504: assorted errors AWS uses to say "yeah... we screwed up"
        status_forcelist=[104, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "PUT", "POST"],
        backoff_factor=2,
    )
    max_work_threads = env.UPLOAD_MAX_WORKER_THREADS
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_work_threads) as executor, requests.Session() as s:
        # For explanation of HTTPAdapter and request session see: https://stackoverflow.com/a/34893364
        s.mount(
            'https://',
            HTTPAdapter(
                # should only ever "need" 1 pool_connection(s); but using 3 to be safe in even of redirects
                pool_connections=3,
                pool_maxsize=max_work_threads * 2,
                max_retries=retries,
            )
        )
        futures = []
        uploaded_file_tasks: Dict[str, List[UploadTask]] = defaultdict(list)
        for file in batch_files.values():
            file_path = Path(file.absolute_path)
            for task in file.tasks:
                futures.append(executor.submit(_do_upload, s, file_path, task, progress_bar))

        for future in concurrent.futures.as_completed(futures):
            if done_event.is_set():
                raise RuntimeError(errors.datastore_upload_process_cancelled())
            res = future.result()
            uploaded_file_tasks[res.data_file_local_id].append(res)

    for k in list(uploaded_file_tasks.keys()):
        uploaded_file_tasks[k] = sorted(uploaded_file_tasks[k], key=lambda x: int(x.part_number))

    completed_files: Dict[str, DataFile] = {}
    for data_file_local_id, completed_tasks in uploaded_file_tasks.items():
        completed_file = batch_files[data_file_local_id]
        completed_file.tasks = completed_tasks
        completed_file.is_uploaded = True
        completed_files[data_file_local_id] = completed_file

    return completed_files


def _start_upload(c: 'GridRestClient', grid_dir: Path, work: Work, progress_bar: PBar) -> Work:
    """Entrypoint to begin processing file uploads.
    """
    while True:
        if done_event.is_set():
            # stop progression since we're in trouble.
            raise RuntimeError(errors.datastore_upload_process_cancelled())

        progress_bar.action_status.update(progress_bar.status_text_uploading)

        completed_files = _upload_next_batch(c=c, work=work, progress_bar=progress_bar)
        if done_event.is_set():
            # don't save if we're not sure that everything completed uploading.
            raise RuntimeError(errors.datastore_upload_process_cancelled())

        if len(completed_files) == 0:
            break
        for file_id, file in completed_files.items():
            work.files[file_id] = file

        progress_bar.action_status.update(progress_bar.status_text_saving)
        _save_work_state(grid_dir, work)

    return work


# ---------------------------- perform finalize ---------------------------


def _get_next_finalize_batch(work: Work) -> List[DataFile]:
    next_batch = []
    num_tasks = 0
    for file in work.files.values():
        if file.is_marked_complete:
            continue
        next_batch.append(file)
        num_tasks += len(file.tasks)
        # ordering is important here in case this value is somehow set to 0.
        if num_tasks >= env.MAX_FILES_PER_FINALIZE_BATCH:
            break

    return next_batch


def _start_finalize(c: 'GridRestClient', grid_dir: Path, work: Work, progress_bar: PBar) -> Work:
    """Entrypoint to finalize uploaded files.
    """
    progress_bar.p_finalize.update(progress_bar.finalize_task_id, visible=True)

    while True:
        if done_event.is_set():
            raise RuntimeError(errors.datastore_upload_process_cancelled())

        progress_bar.action_status.update(progress_bar.status_text_finalizing)
        completed_batch = _get_next_finalize_batch(work)
        if len(completed_batch) == 0:
            break

        complete_presigned_url_upload(
            c=c, cluster_id=work.cluster_id, datastore_id=work.datastore_id, data_files=completed_batch
        )
        completed_parts = 0
        for completed_file in completed_batch:
            work.files[completed_file.local_id].is_marked_complete = True
            completed_parts += int(work.files[completed_file.local_id].part_count)

        progress_bar.p_finalize.update(progress_bar.finalize_task_id, advance=completed_parts)
        progress_bar.action_status.update(progress_bar.status_text_saving)
        _save_work_state(grid_dir=grid_dir, work=work)

    return work


# ------------------------- module user methods ---------------------------


@wrap_signals
def resume_datastore_upload(client: 'GridRestClient', grid_dir: Path, work: Work):
    pbar = PBar()
    with Live(pbar.progress_group):
        pbar.action_status.update(pbar.status_text_initializing)
        pbar.setup_progress_meter(work)

        _start_upload(c=client, grid_dir=grid_dir, work=work, progress_bar=pbar)
        _start_finalize(c=client, grid_dir=grid_dir, work=work, progress_bar=pbar)
        mark_datastore_upload_complete(c=client, cluster_id=work.cluster_id, datastore_id=work.datastore_id)
        pbar.action_status.update(pbar.status_text_done)
        remove_datastore_work_state(grid_dir=grid_dir, datastore_id=work.datastore_id)
    return True


@wrap_signals
def begin_new_datastore_upload(
    client: 'GridRestClient',
    grid_dir: Path,
    source_path: Path,
    cluster_id: str,
    datastore_id: str,
    datastore_name: str,
    datastore_version: str,
    creation_timestamp: datetime.datetime,
):
    creation_timestamp = int(time.mktime(creation_timestamp.timetuple()))  # convert to unix time

    pbar = PBar()
    with Live(pbar.progress_group):
        pbar.action_status.update(pbar.status_text_initializing)
        work = initialize_upload_work(
            name=datastore_name,
            version=datastore_version,
            datastore_id=datastore_id,
            cluster_id=cluster_id,
            creation_timestamp=creation_timestamp,
            source_path=str(source_path),
        )
        pbar.setup_progress_meter(work)

        _save_work_state(grid_dir, work)
        _start_upload(c=client, grid_dir=grid_dir, work=work, progress_bar=pbar)
        _start_finalize(c=client, grid_dir=grid_dir, work=work, progress_bar=pbar)
        mark_datastore_upload_complete(c=client, cluster_id=cluster_id, datastore_id=datastore_id)
        pbar.action_status.update(pbar.status_text_done)
        remove_datastore_work_state(grid_dir=grid_dir, datastore_id=datastore_id)

    return True
