"""Tests tutorials individually.

Unlike the tutorials, these tests do not use hosted pods on staging or production.
Instead, we create pods for these tests to use so that the tests can be run standalone
without dependencies on shared resources.

We use `testbook` to inject code into the first cell of each notebook that patches the
necessary objects and then again in the last cell to stop the patching. This code
injection must be done because we can't use monkeypatch/unittest to mock at the pytest
test level because each tutorial starts up a jupyter kernel within the pytest test which
is unaffected by our mocking attempts. We patch two things:

- `bitfount.hub.helper.BitfountSession`: we patch the BitfountSession for both Pod
and Modeller so that we can authenticate with the hub programmatically i.e. log in with
Selenium

- `"bitfount.federated.transport.oidc.webbrowser.open_new_tab`: we patch the webbrowser
opening call that is made in the OIDC authentication flow which happens when a training
request is made by the Modeller. Again, we open the URL with Selenium in a headless
browser, this time in a separate thread so that we don't block the Modeller's responses
to the OIDC challenges
"""
import asyncio
from dataclasses import dataclass
import json
import logging
from multiprocessing import Process
import os
from pathlib import Path
import time
from typing import Callable, Dict, Final, Generator, Tuple, Union, cast

from _pytest.monkeypatch import MonkeyPatch
from _pytest.tmpdir import TempPathFactory
import jupytext
from nbclient.client import CellTimeoutError
from nbformat.notebooknode import NotebookNode
import pytest
from pytest import fixture
from testbook import testbook
from testbook.client import TestbookNotebookClient

from tests.integration.bitfount_web_interactions import (
    WebdriverBitfountSession,
    get_bitfount_session,
)
from tests.integration.tutorials.notebook_logging import (
    LogQueueManager,
    notebook_queue_logging_code,
)
from tests.integration.utils import mock_authentication_code_nb
from tests.utils import PytestRequest
from tests.utils.helper import (
    tutorial_1_test,
    tutorial_2_test,
    tutorial_3_test,
    tutorial_4_test,
    tutorial_5_test,
    tutorial_6_test,
    tutorial_7_test,
    tutorial_8_test,
    tutorial_9_test,
    tutorial_10_test,
    tutorial_test,
)

logger = logging.getLogger(__name__)

MODELLER_TIMEOUT_PERIOD: Final[int] = 5 * 60  # 5 minutes
IMAGE_MODELLER_TIMEOUT_PERIOD: Final[int] = 12 * 60  # 12 minutes
MULTI_POD_MODELLER_TIMEOUT_PERIOD: Final[int] = 12 * 60  # 12 minutes
POD_TEST_TIMEOUT_PERIOD: Final[int] = 3 * 60  # 3 minutes

# This is the maximum time that a _background_ Pod will be running for.
# All tasks should comfortably be run in this time.
POD_TIMEOUT_PERIOD: Final[int] = 45 * 60  # 45 minutes
MODELLER_USERNAME: Final[str] = "e2e_modeller"
DATA_PROVIDER_USERNAME: Final[str] = "e2e_provider_1"  # currently not used
TUTORIALS: Final[Dict[int, str]] = {
    1: "01_running_a_pod",
    2: "02_running_a_pod_using_yaml",
    3: "03_querying_and_training_a_model",
    4: "04_training_a_model_using_yaml",
    5: "05_training_a_model_on_two_pods",
    6: "06_running_an_image_data_pod",
    7: "07_training_on_images",
    8: "08_training_a_custom_model",
    9: "09_using_pretrained_models",
    10: "10_privacy_preserving_techniques",
}

# Constants representing the names of the pods as in the tutorials
ADULT_POD_NAME: Final[str] = "adult-demo"
ADULT_YAML_POD_NAME: Final[str] = "adult-yaml-demo"
MNIST_POD_NAME: Final[str] = "mnist-demo"


@dataclass
class PodInfo:
    """Wrapper for background pod processes."""

    name: str
    process: Process


def _run_pod(
    tutorial_num: int,
    replacement_pod_name: str,
    pod_log_name: str,
    change_dir_code: str,
    extra_imports: str,
    mock_authentication_code: str,
) -> None:
    """Runs a pod from one of the tutorials. This is required for some tutorials.

    This is defined outside of the TestTutorials class so that it can be run as a
    separate `multiprocessing.Process` - otherwise it is not picklable.

    Args:
        tutorial_num: Relevant tutorial number.
        replacement_pod_name: The replacement, unique name to use for this pod.
        pod_log_name: Name to use to annotate log messages from this pod.
        change_dir_code: Code to change the directory.
        extra_imports: Code to import extra packages for testing.
        mock_authentication_code: Mock authentication code.
    """
    try:
        tutorial_file: str = f"tutorials/{TUTORIALS[tutorial_num]}.md"
        logger.info(f"Running pod from {tutorial_file}.")

        # Need to set a new event loop in this process to ensure no gRPC clash
        asyncio.set_event_loop(asyncio.new_event_loop())

        nb = jupytext.read(tutorial_file)
        if tutorial_num in (1, 2):
            # Adult pod
            # As we know which tutorial this is we don't need to specify full set
            # of args, using empty strings for the ones we don't care about.
            nb = _perform_notebook_replacements(
                nb,
                tutorial_num,
                adult_pod_name=replacement_pod_name,
                mnist_pod_name="",
                second_adult_pod_name="",
            )
        else:  # tutorial_num == 6
            # MNIST pod
            # As we know which tutorial this is we don't need to specify full set
            # of args, using empty strings for the ones we don't care about.
            nb = _perform_notebook_replacements(
                nb,
                tutorial_num,
                adult_pod_name="",
                mnist_pod_name=replacement_pod_name,
                second_adult_pod_name="",
            )

        with testbook(nb, execute=False, timeout=POD_TIMEOUT_PERIOD) as tb:
            logger.info("Injecting change_dir code")
            tb.inject(change_dir_code, pop=True)
            logger.info("Injecting mock authentication code")
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)

            # Add multiprocessing logging support
            logger.info("Injecting queue logging code")
            tb.inject(
                notebook_queue_logging_code(pod_log_name),
                after="logger_setup",
                run=False,
            )

            _execute(tb, fail_on_timeout=False)
    except Exception as e:
        logger.exception(e)
        raise e


def _execute(tb: TestbookNotebookClient, fail_on_timeout: bool = True) -> None:
    """Executes provided notebook.

    Args:
        tb (TestbookNotebookClient): the notebook in testbook foxrmat
        fail_on_timeout (bool, optional): whether the test should fail if the timeout
            is exceeded. Defaults to True.

    Raises:
        Exception: whatever exception is raised during notebook execution is re-raised
    """
    try:
        tb.execute()
    except Exception as e:
        if isinstance(e, CellTimeoutError):
            logger.error("Timeout error while executing notebook")
            if not fail_on_timeout:
                return

        # Fail test if there is an exception during execution
        # Displays outputs of all code cells for debugging
        cell_outputs = [
            cell["outputs"] for cell in tb.cells if cell["cell_type"] == "code"
        ]
        pytest.fail(json.dumps(cell_outputs, indent=2))


def _replace_in_notebook_source_code(
    query: str, replacement: str, notebook: NotebookNode
) -> NotebookNode:
    """Replaces all occurrences of `query` with `replacement` in `notebook` source code.

    Args:
        query (str): code to replace
        replacement (str): replacement code
        notebook (NotebookNode): notebook to have code replaced

    Returns:
        NotebookNode: the same notebook with updated source code
    """
    loggable_query = query.replace("\n", "\\n")
    loggable_replacement = replacement.replace("\n", "\\n")
    logger.info(f'Replacing "{loggable_query}" with "{loggable_replacement}" ')

    changes_made = False
    for i, cell in enumerate(notebook["cells"]):
        orig_source_code: str = cell["source"]
        if cell["cell_type"] == "code" and query in orig_source_code:
            # Mark if changes have been made so we know that things have been
            # applied correctly; every replace should cause at least one change.
            # We know it will be applied because of the `query in` check above.
            changes_made = True
            new_source_code = orig_source_code.replace(query, replacement)
            notebook["cells"][i]["source"] = new_source_code

    if not changes_made:
        raise AssertionError(
            f'No code was replaced when trying to replace "{loggable_query}" '
            f'with "{loggable_replacement}"'
        )
    return notebook


def _perform_notebook_replacements(
    nb: NotebookNode,
    nb_num: int,
    adult_pod_name: str,
    mnist_pod_name: str,
    second_adult_pod_name: str,
    run_user: str = MODELLER_USERNAME,
) -> NotebookNode:
    """Replaces code in the notebook denoted by `nb_num` for testing purposes.

    Args:
        nb (NotebookNode): notebook object
        nb_num (int): number of the notebook

    Returns:
        NotebookNode: the notebook with relevant source code modified
    """
    logger.info(f"Replacing content in notebook for tutorial {nb_num}")
    # If tutorials 3, 5, 8, 9 or 10:
    # - Change production pod(s) name to unique local pod name(s)
    # - Explicitly specify username as modeller
    if nb_num in (3, 5, 8, 9, 10):
        nb = _replace_in_notebook_source_code(ADULT_POD_NAME, adult_pod_name, nb)

        pod_identifier = "first_pod_identifier" if nb_num == 5 else "pod_identifier"
        if nb_num != 5:
            nb = _replace_in_notebook_source_code(
                f"schema = get_pod_schema({pod_identifier})",
                "from bitfount import BitfountSchema\nschema = BitfountSchema."
                "load_from_file('../tests/integration/resources/schemas/adult_schema.yaml')\n"  # noqa: B950
                f"schema.tables[0].name = '{adult_pod_name}'",
                nb,
            )
        if nb_num == 5:
            # Also replace the other pod for tutorial 5
            if not second_adult_pod_name:
                raise ValueError("Second pod name is needed")
            nb = _replace_in_notebook_source_code(
                ADULT_YAML_POD_NAME,
                second_adult_pod_name,
                nb,
            )
            nb = _replace_in_notebook_source_code(
                "schema = combine_pod_schemas([first_pod_identifier, second_pod_identifier])",  # noqa: B950
                "schema = BitfountSchema.load_from_file('../tests/integration/resources/schemas/adult_schema.yaml')\n"  # noqa: B950
                "import copy;schema.tables.append(copy.deepcopy(schema.tables[0]))\n"  # noqa: B950
                f"schema.tables[0].name = '{adult_pod_name}';schema.tables[1].name = '{second_adult_pod_name}'",  # noqa: B950
                nb,
            )
        if nb_num == 8:
            nb = _replace_in_notebook_source_code(
                'model_ref=Path("MyCustomModel.py"),',
                f'model_ref=Path("MyCustomModel.py"),username="{run_user}",',
                nb,
            )
    # If tutorials 1 or 2 or 6 (pod tutorials):
    # - Explicitly specify username as modeller
    # - Change pod name to be unique
    elif nb_num in (1, 2, 6):
        # Explicitly add username as data provider
        if nb_num == 2:
            # Yaml pod explicitly add username as data provider
            nb = _replace_in_notebook_source_code(
                "pod_name:", f"username: {run_user}\npod_name:", nb
            )
        # Change pod name to be unique
        if nb_num == 1:
            old_pod_name = ADULT_POD_NAME
            replacement_pod_name = adult_pod_name
        elif nb_num == 2:
            old_pod_name = ADULT_YAML_POD_NAME
            replacement_pod_name = second_adult_pod_name
        elif nb_num == 6:
            old_pod_name = MNIST_POD_NAME
            replacement_pod_name = mnist_pod_name

        # Replace pod name
        nb = _replace_in_notebook_source_code(old_pod_name, replacement_pod_name, nb)

        if nb_num in (1, 6):
            # Load pod keys from file to slightly speed up the tests
            nb = _replace_in_notebook_source_code(
                "pod = Pod(",
                f'pod_keys=_get_pod_keys(user_storage_path / "{replacement_pod_name}")\npod = Pod(pod_keys=pod_keys,',  # noqa: B950
                nb,
            )

            nb = _replace_in_notebook_source_code(
                "data_config=PodDataConfig(",
                f'username="{run_user}",\ndata_config=PodDataConfig(',
                nb,
            )

    # If tutorial 7:
    # - Explicitly specify username as modeller
    # - Change pod name to be the unique pod created
    elif nb_num == 7:

        # # Change pod name to be the unique pod created
        nb = _replace_in_notebook_source_code(
            MNIST_POD_NAME,
            mnist_pod_name,
            nb,
        )
        # Load schema from file
        nb = _replace_in_notebook_source_code(
            "schema = get_pod_schema(pod_identifier)",
            "from bitfount import BitfountSchema\nschema = BitfountSchema."
            "load_from_file('../tests/integration/resources/schemas/mnist_schema.yaml')\n"  # noqa: B950
            f"schema.tables[0].name = '{mnist_pod_name}'",
            nb,
        )

    elif nb_num == 4:
        # Tutorial 4 uses the YAML pod, but its test uses the non-YAML pod so we need to
        # replace the YAML pod name with the new non-YAML pod name
        nb = _replace_in_notebook_source_code(ADULT_YAML_POD_NAME, adult_pod_name, nb)

        nb = _replace_in_notebook_source_code(
            "pods:\n  identifiers:",
            f"modeller:\n  username: {run_user}\npods:\n  identifiers:",
            nb,
        )

    return nb


@tutorial_test
class TestTutorials:
    """Tests tutorials to ensure they are working as expected.

    The tests below differ slightly depending on the value of the BITFOUNT_ENVIRONMENT
    environment variable.
    """

    @fixture(autouse=True, scope="module")
    def set_bitfount_environment(self, monkeypatch_module_scope: MonkeyPatch) -> None:
        """Sets bitfount environment to staging for tests."""
        monkeypatch_module_scope.setenv("BITFOUNT_ENVIRONMENT", "staging")

    @fixture(autouse=True, scope="module")
    def cleanup(self) -> Generator[None, None, None]:
        """Removes models before and after all tests."""
        tutorials = (3, 4, 5, 7, 8, 9)
        for num in tutorials:
            output = Path(f"tutorials/part_{num}_model.pt")
            output.unlink(missing_ok=True)

        yield

        for num in tutorials:
            output = Path(f"tutorials/part_{num}_model.pt")
            output.unlink(missing_ok=True)
        # This gets overwritten in Tutorial 8 so no need to remove beforehand as well
        Path("MyCustomModel.py").unlink(missing_ok=True)

    @fixture(scope="module")
    def change_dir_code(self) -> str:
        """Changes the directory of the jupyter notebook execution to `tutorials`."""
        return "%cd tutorials"

    @fixture(scope="module")
    def extra_imports(self) -> str:
        """Extra imports needed for testing."""
        return (
            "from bitfount.federated.pod_keys_setup import _get_pod_keys\n"
            "from pathlib import Path\n"
            "from typing import Tuple, Any\n"
            "import unittest"
        )

    @fixture
    def authentication_user(self, request: PytestRequest) -> str:
        """Returns the username to use for authentication as in the request."""
        username: str = request.param
        if username in (MODELLER_USERNAME, DATA_PROVIDER_USERNAME):
            return username
        else:
            raise ValueError("Request must be a valid predefined username.")

    @fixture
    def authentication_password(self, authentication_user: str) -> str:
        """Returns the password associated with the authentication username."""
        if authentication_user == MODELLER_USERNAME:
            return os.environ["e2e_modeller_pswd"]
        elif authentication_user == DATA_PROVIDER_USERNAME:
            return os.environ["e2e_provider_1_pswd"]
        else:
            raise ValueError(
                f'Username "{authentication_user}" is not a valid predefined username.'
            )

    @fixture(scope="module")
    def token_dir(self, tmp_path_factory: TempPathFactory) -> Path:
        """Temporary directory for tokens."""
        return tmp_path_factory.mktemp(".bitfount", numbered=False) / "bitfount_tokens"

    @fixture
    def mock_authentication_code(
        self, authentication_password: str, authentication_user: str, token_dir: Path
    ) -> str:
        """Returns code that patches bitfount session and OIDC authentication."""
        return mock_authentication_code_nb(
            authentication_user, authentication_password, token_dir
        )

    @fixture(scope="module")
    def mock_authentication_cleanup_code(self) -> str:
        """Stops the BitfountSession and OIDC patchers.

        Should be injected at the end of the notebook execution. Relies on variables
        defined in the `mock_authentication_code` fixture.
        """
        return "session_patcher.stop(); oidc_patcher.stop()"

    @fixture
    def fixed_notebooks(
        self,
        adult_pod_name: str,
        authentication_user: str,
        mnist_pod_name: str,
        request: PytestRequest,
        second_adult_pod_name: str,
    ) -> Union[NotebookNode, Tuple[NotebookNode, NotebookNode]]:
        """Opens requested notebook(s), performs modifications and returns it."""
        nb_nums = request.param
        if not isinstance(nb_nums, tuple):
            nb_nums = (nb_nums,)

        fixed_notebooks = []

        for nb_num in nb_nums:
            nb = jupytext.read(f"tutorials/{TUTORIALS[nb_num]}.md")
            fixed_notebooks.append(
                _perform_notebook_replacements(
                    nb=nb,
                    nb_num=nb_num,
                    adult_pod_name=adult_pod_name,
                    mnist_pod_name=mnist_pod_name,
                    second_adult_pod_name=second_adult_pod_name,
                    run_user=authentication_user,
                )
            )

        if len(fixed_notebooks) == 1:
            return fixed_notebooks[0]
        elif len(fixed_notebooks) == 2:
            return cast(Tuple[NotebookNode, NotebookNode], tuple(fixed_notebooks))
        else:
            raise ValueError("Too many notebooks output.")

    @fixture(scope="module")
    def pod_run_user(self) -> str:
        """User who will be running the background pods."""
        return MODELLER_USERNAME

    @fixture(scope="module")
    def pod_run_password(self) -> str:
        """Password for user running background pods."""
        return os.environ["e2e_modeller_pswd"]

    @fixture(scope="module")
    def pod_run_bitfount_session(
        self, pod_run_password: str, pod_run_user: str, token_dir: Path
    ) -> WebdriverBitfountSession:
        """Creates an authenticated bitfount session for the authenticated user."""
        session = get_bitfount_session(pod_run_user, pod_run_password, token_dir)
        session.authenticate()
        return session

    @fixture(scope="module")
    def pod_factory(
        self,
        change_dir_code: str,
        extra_imports: str,
        log_queue_manager: LogQueueManager,
        pod_run_user: str,
        pod_run_password: str,
        pod_suffix: str,
        token_dir: Path,
    ) -> Callable[[str, str], PodInfo]:
        """Returns function which returns either mnist or adult pod process."""

        def get_pod_process(process_name: str, replacement_pod_name: str) -> PodInfo:
            """Returns either mnist or adult pod process."""
            if "adult" in replacement_pod_name:
                tutorial_num = 1
            elif "mnist" in replacement_pod_name:
                tutorial_num = 6
            else:
                raise ValueError(f"Invalid pod name {replacement_pod_name}")

            mock_authentication_code = mock_authentication_code_nb(
                pod_run_user, pod_run_password, token_dir
            )

            pod_process = Process(
                name=process_name,
                target=_run_pod,
                args=(
                    tutorial_num,
                    replacement_pod_name,
                    process_name,
                    change_dir_code,
                    extra_imports,
                    mock_authentication_code,
                ),
            )

            # Start pod
            logger.info(f"Starting pod {process_name}:{replacement_pod_name}")
            pod_process.start()

            # We sleep for 60 seconds to give time for the pod to start up
            # Without this sleep, there ends up being confusion around encryption keys
            # and the pod is unable to decrypt the messages from the Modeller.
            logger.info(
                f"Waiting for pod {process_name}:{replacement_pod_name} to start "
                f"up and register"
            )
            time.sleep(60)
            logger.info(
                f"Pod {process_name}:{replacement_pod_name} should be started by now"
            )
            return PodInfo(replacement_pod_name, pod_process)

        return get_pod_process

    @fixture(scope="module")
    def pod_suffix(self) -> str:
        """Generate a unique suffix for all pods in this test run."""
        return str(int(time.time()))  # unix timestamp

    @fixture(scope="module")
    def adult_pod_name(self, pod_suffix: str) -> str:
        """Name of the adult pod."""
        adult_pod_name = f"{ADULT_POD_NAME}-{pod_suffix}"
        logger.info(f"Adult pod name: {adult_pod_name}")
        return adult_pod_name

    @fixture(scope="module")
    def adult_pod(
        self,
        pod_factory: Callable[[str, str], PodInfo],
        adult_pod_name: str,
    ) -> Generator[PodInfo, None, None]:
        """Returns Adult pod at the module level.

        Terminates the pod after all tests have run.
        """
        logger.info("Creating adult pod")
        adult_pod_info = pod_factory("adult", adult_pod_name)
        yield adult_pod_info
        logger.info("Stopping adult pod")
        adult_pod_info.process.terminate()
        adult_pod_info.process.join()

    @fixture(scope="module")
    def mnist_pod_name(self, pod_suffix: str) -> str:
        """Name of the MNIST pod."""
        mnist_pod_name = f"{MNIST_POD_NAME}-{pod_suffix}"
        logger.info(f"MNIST pod name: {mnist_pod_name}")
        return mnist_pod_name

    @fixture(scope="module")
    def mnist_pod(
        self,
        mnist_pod_name: str,
        pod_factory: Callable[[str, str], PodInfo],
    ) -> Generator[PodInfo, None, None]:
        """Returns MNIST pod at the module level.

        Terminates the pod after all tests have run.
        """
        logger.info("Creating MNIST pod")
        mnist_pod_info = pod_factory("mnist", mnist_pod_name)
        yield mnist_pod_info
        logger.info("Stopping MNIST pod")
        mnist_pod_info.process.terminate()
        mnist_pod_info.process.join()

    @fixture
    def second_adult_pod_name(self, pod_suffix: str) -> str:
        """Name of the second adult pod."""
        adult_pod_name = f"{ADULT_POD_NAME}-2-{pod_suffix}"
        logger.info(f"Second adult pod name: {adult_pod_name}")
        return adult_pod_name

    @fixture
    def second_adult_pod(
        self, pod_factory: Callable[[str, str], PodInfo], second_adult_pod_name: str
    ) -> Generator[PodInfo, None, None]:
        """Second adult pod used for Tutorial 3."""
        logger.info("Creating second Adult Pod")
        pod_process_info = pod_factory("adult_2", second_adult_pod_name)
        yield pod_process_info
        logger.info("Stopping second Adult Pod")
        pod_process_info.process.terminate()
        pod_process_info.process.join()

    @tutorial_1_test
    @pytest.mark.skip(
        "Other tests currently rely on this Pod so this can be skipped for now."
    )
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(1, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_1(
        self,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        fixed_notebooks: NotebookNode,
        mock_authentication_code: str,
    ) -> None:
        """Tests that we can start a fresh pod."""
        tutorial_1: NotebookNode = fixed_notebooks
        with testbook(tutorial_1, execute=False, timeout=POD_TEST_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_1"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 1")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            cell_outputs = [
                cell["outputs"] for cell in tb.cells if cell["cell_type"] == "code"
            ]

        # We check the outputs of the second last item of the last cell of the notebook
        # The reason it is the second last output of the cell is because the stack
        # trace that gets outputted when the pod is halted is the last item
        assert "Pod started... press Ctrl+C to stop" in cell_outputs[-1][-2]["text"]

    @tutorial_2_test
    @pytest.mark.skip(
        "This tutorial works and should pass but it fails due to a CellTimeOutError. "
        + "Needs further investigation."
    )
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(2, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_2(
        self,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_code: str,
    ) -> None:
        """Tests that we can start a fresh pod using the yaml configuration."""
        tutorial_2: NotebookNode = fixed_notebooks
        with testbook(tutorial_2, execute=False, timeout=POD_TEST_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_2"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 2")
            with tb.patch("bitfount.hub.helper._save_key_to_key_store"):
                _execute(tb, fail_on_timeout=False)

            cell_outputs = [
                cell["outputs"] for cell in tb.cells if cell["cell_type"] == "code"
            ]

        # We check the outputs of the second last item of the last cell of the notebook
        # The reason it is the second last output of the cell is because the stack
        # trace that gets outputted when the pod is halted is the last item
        assert "Pod started... press Ctrl+C to stop" in cell_outputs[-1][-2]["text"]

    @tutorial_3_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(3, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_3(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests that modeller can train on adult pod."""
        tutorial_3: NotebookNode = fixed_notebooks

        with testbook(tutorial_3, execute=False, timeout=MODELLER_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_3"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 3")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_3_model.pt").exists()

    @tutorial_4_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(4, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_4(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests that modeller can train on adult pod using yaml configuration."""
        # Grant proactive access for modeller
        tutorial_4: NotebookNode = fixed_notebooks
        with testbook(tutorial_4, execute=False, timeout=MODELLER_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_4"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 4")
            with tb.patch("bitfount.hub.helper._save_key_to_key_store"):
                _execute(tb)

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_4_model.pt").exists()

    @tutorial_5_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(5, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_5(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
        second_adult_pod: PodInfo,
    ) -> None:
        """Tests that we can train on multiple pods in one task."""
        tutorial_5: NotebookNode = fixed_notebooks
        with testbook(
            tutorial_5, execute=False, timeout=MULTI_POD_MODELLER_TIMEOUT_PERIOD
        ) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_5"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 5")
            with tb.patch("bitfount.hub.helper._save_key_to_key_store"):
                _execute(tb)

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_5_model.pt").exists()

    @tutorial_6_test
    @pytest.mark.skip(
        "Other tests currently rely on this Pod so this can be skipped for now."
    )
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(6, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_6(
        self,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_code: str,
    ) -> None:
        """Tests running image data pod."""
        tutorial_6: NotebookNode = fixed_notebooks
        with testbook(tutorial_6, execute=False, timeout=POD_TEST_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_6"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 6")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb, fail_on_timeout=False)
                mock_save_to_key_store.is_called_once()

            cell_outputs = [
                cell["outputs"] for cell in tb.cells if cell["cell_type"] == "code"
            ]

        # We check the outputs of the second last item of the last cell of the notebook
        # The reason it is the second last output of the cell is because the stack
        # trace that gets outputted when the pod is halted is the last item
        assert "Pod started... press Ctrl+C to stop" in cell_outputs[-1][-2]["text"]

    @tutorial_7_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(7, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_7(
        self,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mnist_pod: PodInfo,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests training on images."""
        tutorial_7: NotebookNode = fixed_notebooks
        with testbook(
            tutorial_7, execute=False, timeout=IMAGE_MODELLER_TIMEOUT_PERIOD
        ) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_7"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 7")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_7_model.pt").exists()

    @tutorial_8_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(8, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_8(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests custom models."""
        tutorial_8: NotebookNode = fixed_notebooks
        with testbook(tutorial_8, execute=False, timeout=MODELLER_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)

            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_8"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 8")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_8_model.pt").exists()

    @tutorial_9_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [((3, 9), MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_9(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: Tuple[NotebookNode, NotebookNode],
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests pretrained models.

        First runs tutorial 2 to get the pretrained model that gets generated before
        running tutorial 9.
        """
        tutorial_3, tutorial_9 = fixed_notebooks
        with testbook(tutorial_3, execute=False, timeout=MODELLER_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_3"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 3")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)

        assert Path("tutorials/part_3_model.pt").exists()

        with testbook(tutorial_9, execute=False, timeout=MODELLER_TIMEOUT_PERIOD) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_9"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 9")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)

    @tutorial_10_test
    @pytest.mark.parametrize(
        "fixed_notebooks, authentication_user",
        [(10, MODELLER_USERNAME)],
        indirect=True,
    )
    def test_tutorial_10(
        self,
        adult_pod: PodInfo,
        authentication_user: str,
        change_dir_code: str,
        clear_log_queue: None,
        extra_imports: str,
        fixed_notebooks: NotebookNode,
        mock_authentication_cleanup_code: str,
        mock_authentication_code: str,
    ) -> None:
        """Tests that modeller can train privately on adult pod."""
        tutorial_10: NotebookNode = fixed_notebooks

        with testbook(
            tutorial_10,
            execute=False,
            # Privacy tutorial takes longer to run, so give 8 minutes timeout
            timeout=8 * 60,
        ) as tb:
            tb.inject(change_dir_code, pop=True)
            tb.inject(extra_imports, pop=True)
            tb.inject(mock_authentication_code, pop=True)
            # Add notebook logging support
            tb.inject(
                notebook_queue_logging_code("tutorial_10"),
                after="logger_setup",
                run=False,
            )

            logger.info("Running tutorial 10")
            with tb.patch(
                "bitfount.hub.helper._save_key_to_key_store"
            ) as mock_save_to_key_store:
                _execute(tb)
                mock_save_to_key_store.is_called_once()

            tb.inject(mock_authentication_cleanup_code, pop=True)
