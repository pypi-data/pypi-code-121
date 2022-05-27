"""Tests the system end-to-end using real web calls."""
from functools import partial
import logging
import multiprocessing
from multiprocessing import Queue
import os
from pathlib import Path
import time
from typing import Any, cast
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
import pytest
from pytest_mock import MockerFixture

from bitfount import BitfountSchema, DataStructure
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.csv_source import CSVSource
from bitfount.runners.config_schemas import ModellerConfig, PodConfig
from bitfount.runners.modeller_runner import setup_modeller_from_config
from bitfount.runners.pod_runner import setup_pod_from_config
from tests.integration import CONFIG_DIR
from tests.integration.bitfount_web_interactions import (
    WebdriverBitfountSession,
    get_bitfount_session,
    grant_proactive_access,
    oidc_flow,
)
from tests.integration.utils import (
    load_modeller_config,
    load_pod_config,
    password_from_modeller_config,
    password_from_pod_config,
    pod_start,
    run_modeller_process,
    tie_together_configs,
)
from tests.utils.helper import TABLE_NAME, backend_test, end_to_end_test

logger = logging.getLogger(__name__)

# Get timeouts/sleeps from envvars if possible
POD_STARTUP_SLEEP: int = int(os.getenv("E2E_TEST_POD_STARTUP_SLEEP", default=20))
MODELLER_STARTUP_SLEEP: int = int(
    os.getenv("E2E_TEST_MODELLER_STARTUP_SLEEP", default=5)
)
MODELLER_RUN_TIMEOUT: int = int(
    os.getenv("E2E_TEST_MODELLER_RUN_TIMEOUT", default=2.5 * 60)
)


@backend_test
@end_to_end_test
class TestAdultEndToEnd:
    """End-to-end tests using the Adult dataset."""

    @pytest.fixture(autouse=True)
    def bitfount_env(self, monkeypatch: MonkeyPatch) -> None:
        """Set BITFOUNT_ENVIRONMENT env var to 'staging'."""
        monkeypatch.setenv("BITFOUNT_ENVIRONMENT", "staging")

    @pytest.fixture
    def token_dir(self, tmp_path: Path) -> Path:
        """Directory to store tokens."""
        return tmp_path / "bitfount_tokens"

    @pytest.fixture
    def modeller_config(self) -> ModellerConfig:
        """Modeller config."""
        return load_modeller_config(CONFIG_DIR / "modeller.yaml")

    @pytest.fixture
    def adult_modeller_config(self) -> ModellerConfig:
        """Adult modeller config."""
        return load_modeller_config(CONFIG_DIR / "modeller_adult_result_only.yaml")

    @pytest.fixture
    def modeller_pswd(self, modeller_config: ModellerConfig) -> str:
        """Modeller password."""
        return password_from_modeller_config(modeller_config)

    @pytest.fixture
    def pod_1_config(self, adult_data: Path) -> PodConfig:
        """Pod 1 config."""
        return load_pod_config(CONFIG_DIR / "pod_1.yaml", adult_data)

    @pytest.fixture
    def adult_pod_config(self, adult_data: Path) -> PodConfig:
        """Adult pod config."""
        return load_pod_config(CONFIG_DIR / "pod_adult.yaml", adult_data)

    @pytest.fixture
    def pod_1_pswd(self, pod_1_config: PodConfig) -> str:
        """Pod 1 password."""
        return password_from_pod_config(pod_1_config)

    @pytest.fixture
    def pod_2_config(self, adult_data: Path) -> PodConfig:
        """Pod 2 config."""
        return load_pod_config(CONFIG_DIR / "pod_2.yaml", adult_data)

    @pytest.fixture
    def pod_2_pswd(self, pod_2_config: PodConfig) -> str:
        """Pod 2 password."""
        return password_from_pod_config(pod_2_config)

    @pytest.fixture
    def datasource(self, adult_data: Path) -> _BaseSource:
        """Adult datasource."""
        return CSVSource(adult_data, seed=100, ignore_cols=["fnlwgt"])

    @pytest.fixture
    def mock_modeller_oidc(self, mocker: MockerFixture) -> Any:
        """Mock out oidc auth flow."""
        oidc_webbrowser_import = (
            "bitfount.federated.transport.identity_verification"
            ".oidc.webbrowser.open_new_tab"
        )

        oidc_patcher = mocker.patch(oidc_webbrowser_import)
        return oidc_patcher

    @pytest.fixture
    def schema(self, datasource: _BaseSource) -> BitfountSchema:
        """Adult schema."""
        return BitfountSchema(
            datasource,
            table_name=TABLE_NAME,
            force_stypes={
                TABLE_NAME: {
                    "categorical": [
                        "TARGET",
                        "workclass",
                        "marital-status",
                        "occupation",
                        "relationship",
                        "race",
                        "native-country",
                        "gender",
                        "education",
                    ]
                },
            },
        )

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    async def test_local_vs_pod(
        self,
        adult_modeller_config: ModellerConfig,
        adult_pod_config: PodConfig,
        datasource: _BaseSource,
        mock_bitfount_session: Mock,
        mock_modeller_oidc: Mock,
        modeller_pswd: str,
        pod_1_pswd: str,
        schema: BitfountSchema,
        token_dir: Path,
    ) -> None:
        """Tests local vs remote results with oidc device code auth."""
        try:
            # Load configs and tie together
            adult_modeller_config.pods.identifiers = [adult_pod_config.pod_id]
            # Mock BitfountSession
            # Override default return_value with side_effect
            # get_bitfount_session() one. side_effect takes precedence
            # over return_value.
            # If you ever change the order that the processes start in,
            # then be sure to change the order of these...
            mock_bitfount_session.side_effect = [
                # pod 1 bitfount session
                get_bitfount_session(adult_pod_config.username, pod_1_pswd, token_dir),
                # modeller bitfount session
                get_bitfount_session(
                    adult_modeller_config.modeller.username, modeller_pswd, token_dir
                ),
            ]

            mock_modeller_oidc.side_effect = [
                partial(
                    oidc_flow,
                    username=adult_modeller_config.modeller.username,
                    password=modeller_pswd,
                )
            ]
            # Load pods
            pod = setup_pod_from_config(adult_pod_config)

            # Start pods
            logger.info("Spinning up pods... ")
            pod_process = multiprocessing.Process(
                target=pod_start, name="Pod_Runner", args=(pod,)
            )
            pod_process.start()

            time.sleep(POD_STARTUP_SLEEP)  # give the pods time to spin up

            assert pod_process.is_alive()

            logger.info("Pods loaded.")

            # Sort proactive access to each pod
            logger.info(
                f"Granting proactive access to pod {adult_pod_config.pod_id}..."
            )
            grant_proactive_access(
                modeller_username=adult_modeller_config.modeller.username,
                pod_id=adult_pod_config.pod_id,
                role="general_modeller",
                # This is a WebdriverBitfountSession as we mocked it out
                pod_session=cast(WebdriverBitfountSession, pod._session),
            )

            # Load modeller
            # We do this after the pods have started, as we need the pods to have
            # published their public keys to the Hub.
            modeller, pod_identifiers = setup_modeller_from_config(
                adult_modeller_config
            )

            queue: Queue = Queue()

            modeller_process = multiprocessing.Process(
                target=run_modeller_process,
                name="Modeller_Run",
                args=(
                    modeller,
                    pod_identifiers,
                    None,
                    queue,
                ),
            )

            # Start modeller
            logger.info("Starting Modeller...")
            modeller_process.start()
            time.sleep(MODELLER_STARTUP_SLEEP)  # give modeller time to spin up

            # Join modeller, wait for output for MODELLER_RUN_TIMEOUT seconds
            modeller_process.join(MODELLER_RUN_TIMEOUT)

            # Check modeller is done, pods still going
            logger.info("Modeller should be finished by this point.")
            assert not modeller_process.is_alive()
            assert (
                modeller_process.exitcode is not None and modeller_process.exitcode <= 0
            )

            pod_results = queue.get()[0]
            # Check pod_results exists
            assert pod_results
            # Ensure pods are still running
            assert pod_process.is_alive()

            # Stop all pods
            pod_process.terminate()
            pod_process.join()

            # Ensure shutdown
            assert pod_process.exitcode is not None and pod_process.exitcode <= 0

            schema.unfreeze()
            datastructure = DataStructure(table=pod.name, target="TARGET")
            hyperparameters = adult_modeller_config.task.model.hyperparameters
            model_name = adult_modeller_config.task.model.name
            if model_name:
                assert PyTorchTabularClassifier == eval(model_name)
                local_model = PyTorchTabularClassifier(
                    datastructure=datastructure,
                    schema=schema,
                    **hyperparameters,
                )

                local_results = local_model.fit(data=datasource)
                if local_results:
                    # Check results are the same
                    for k, pod_value in pod_results:
                        assert pod_value == local_results.get(k)
                else:
                    raise ValueError("Local results are None")
        finally:
            # Stop all processes
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                modeller_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            except Exception:
                pass

    @pytest.mark.skip("Signature-based access not working until [BIT-1291] implemented")
    async def test_adult_e2e_results_only(
        self,
        mock_bitfount_session: Mock,
        modeller_config: ModellerConfig,
        modeller_pswd: str,
        pod_1_config: PodConfig,
        pod_1_pswd: str,
        pod_2_config: PodConfig,
        pod_2_pswd: str,
        tmp_path: Path,
        token_dir: Path,
    ) -> None:
        """Tests a full end-to-end run.

        End to end run using Adult dataset with key-based id verification.
        """
        try:
            # Load configs and tie together
            tie_together_configs(modeller_config, pod_1_config, pod_2_config)
            # Mock BitfountSession
            # Override default return_value with side_effect
            # get_bitfount_session() one. side_effect takes precedence
            # over return_value.
            # If you ever change the order that the processes start in,
            # then be sure to change the order of these...
            mock_bitfount_session.side_effect = [
                # pod 1 bitfount session
                get_bitfount_session(pod_1_config.username, pod_1_pswd, token_dir),
                # pod 2 bitfount session
                get_bitfount_session(pod_2_config.username, pod_2_pswd, token_dir),
                # modeller bitfount session
                get_bitfount_session(
                    modeller_config.modeller.username, modeller_pswd, token_dir
                ),
            ]
            # Load pods
            pod_1 = setup_pod_from_config(pod_1_config)
            pod_2 = setup_pod_from_config(pod_2_config)

            # Start pods
            logger.info("Spinning up pods... ")
            logger.info("Spinning up pod 1... ")
            pod_1_process = multiprocessing.Process(
                target=pod_start, name="Pod_1_Runner", args=(pod_1,)
            )
            pod_1_process.start()

            logger.info("Spinning up pod 2... ")
            pod_2_process = multiprocessing.Process(
                target=pod_start, name="Pod_2_Runner", args=(pod_2,)
            )
            pod_2_process.start()
            time.sleep(POD_STARTUP_SLEEP)  # give the pods time to spin up

            assert pod_1_process.is_alive()
            assert pod_2_process.is_alive()

            logger.info("Pods loaded.")

            # Sort proactive access to each pod
            logger.info(f"Granting proactive access to pod {pod_1_config.pod_id}...")
            grant_proactive_access(
                modeller_username=modeller_config.modeller.username,
                pod_id=pod_1_config.pod_id,
                role="general_modeller",
                # This is a WebdriverBitfountSession as we mocked it out
                pod_session=cast(WebdriverBitfountSession, pod_1._session),
            )
            logger.info(f"Granting proactive access to pod {pod_2_config.pod_id}...")
            grant_proactive_access(
                modeller_username=modeller_config.modeller.username,
                pod_id=pod_2_config.pod_id,
                role="general_modeller",
                # This is a WebdriverBitfountSession as we mocked it out
                pod_session=cast(WebdriverBitfountSession, pod_2._session),
            )

            # Load modeller
            # We do this after the pods have started, as we need the pods to have
            # published their public keys to the Hub.
            modeller, pod_identifiers = setup_modeller_from_config(modeller_config)
            model_out = tmp_path / "model.out"

            modeller_process = multiprocessing.Process(
                target=run_modeller_process,
                name="Modeller_Run",
                args=(
                    modeller,
                    pod_identifiers,
                    model_out,
                ),
            )

            # Start modeller
            logger.info("Starting Modeller...")
            modeller_process.start()
            time.sleep(MODELLER_STARTUP_SLEEP)  # give modeller time to spin up
            assert not model_out.exists()  # check doesn't exist at this point

            # Join modeller, wait for output for MODELLER_RUN_TIMEOUT seconds
            modeller_process.join(MODELLER_RUN_TIMEOUT)

            # Check modeller is done, pods still going
            logger.info("Modeller should be finished by this point.")
            assert not modeller_process.is_alive()
            assert (
                modeller_process.exitcode is not None and modeller_process.exitcode <= 0
            )

            # Check output file exists and has nonzero size
            assert model_out.exists()
            assert os.path.getsize(model_out) > 0

            # Ensure pods are still running
            assert pod_1_process.is_alive()
            assert pod_2_process.is_alive()

            # Stop all pods
            for process in [pod_1_process, pod_2_process]:
                process.terminate()
                process.join()

            # Ensure shutdown
            assert pod_1_process.exitcode is not None and pod_1_process.exitcode <= 0
            assert pod_2_process.exitcode is not None and pod_2_process.exitcode <= 0
        finally:
            try:
                # The unbound variable issue is handled by the NameError catching below.
                # noinspection PyUnboundLocalVariable
                private_key_file: Path = cast(
                    Path, modeller_config.modeller.private_key_file
                )
                os.remove(private_key_file)
            except FileNotFoundError:
                pass
            except NameError:
                # Means the modeller_config variable didn't even get created;
                # another exception has occurred that has booted us out of the
                # `try` block before it even got to there. We pass on NameError
                # to avoid masking whatever that underlying exception was.
                pass

            # Stop all processes
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                modeller_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_1_process.terminate()
            except Exception:
                pass
            # noinspection PyBroadException
            try:
                # noinspection PyUnboundLocalVariable
                pod_2_process.terminate()
            except Exception:
                pass
