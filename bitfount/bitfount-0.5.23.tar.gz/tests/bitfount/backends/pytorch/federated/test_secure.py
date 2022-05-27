"""Test secure multi party computation with pytorch backend."""
import copy
from functools import partial
from typing import Any, Callable, Dict, List, Tuple, cast
from unittest.mock import AsyncMock, MagicMock, Mock, create_autospec

import numpy as np
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import torch

from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.federated.exceptions import SecureShareError
from bitfount.federated.secure import SecureShare
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import _TensorLike, _Weights
from tests.utils.helper import (
    backend_test,
    create_datasource,
    create_datastructure,
    unit_test,
)


@backend_test
@unit_test
class TestSecureShare:
    """Test SecureShare algorithm with pytorch tensors."""

    @fixture
    def datastructure(self) -> DataStructure:
        """Fixture for datastructure."""
        return create_datastructure()

    @fixture
    def datasource(self) -> _BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    @fixture
    def mock_secure_transport_methods(self) -> Tuple[Callable, Callable]:
        """Returns tuple of mocked SecureShare methods which need a mailbox."""

        def mock_share_own_shares(worker_shares: Any, self: Any, mailbox: Any) -> None:
            """Mocks '_share_own_shares' method."""
            for worker, shares in worker_shares.items():
                if worker != self.name:
                    rand_num = self._get_random_number()
                    shares.append(rand_num)

        def mock_receive_worker_shares(
            worker_shares: Any, self: Any, mailbox: Any
        ) -> None:
            """Mocks '_receive_worker_shares' method."""
            self._other_worker_shares = worker_shares[self.name]
            worker_shares[self.name] = []

        return mock_share_own_shares, mock_receive_worker_shares

    @pytest.mark.parametrize(
        "prime_q, tensor_list, precision",
        [
            (5, [0.1, 0.2, -0.2], 10),
            (13, [0.1, -0.2, -0.3], 10),
            (29, [-1.0, 0.2, 0.9], 10),
            (101, [0.1, -0.39, 0.5], 100),
            (1913, [0.1, -4, 0.39], 100),
            (1913, [0.1, -0.4, 0.4], 1000),
        ],
    )
    def test_encode_and_decode_finite_field(
        self, precision: int, prime_q: int, tensor_list: List[float]
    ) -> None:
        """Ensures output matches input after encoding and decoding."""
        sec = SecureShare(prime_q=prime_q, precision=precision)
        tensor = _AdaptorForPyTorchTensor(
            torch.tensor(tensor_list, dtype=torch.float64)
        )
        encoded_tensor = sec._encode_finite_field(tensor)
        assert isinstance(encoded_tensor, np.ndarray)
        decoded_tensor = sec._decode_finite_field(encoded_tensor)
        assert isinstance(decoded_tensor, np.ndarray)
        np.testing.assert_array_equal(tensor.torchtensor.numpy(), decoded_tensor)

    @pytest.mark.parametrize(
        "a, b",
        [
            ([13, 10], [29, 1]),
            ([13, 50], [49, 7]),
            ([-13, -50], [-49, -7]),
            ([-126, -41], [109, 111]),
            ([-123, 50], [-1, 17]),
            ([-123.23, 50.1], [-1.01, 16.99]),
            ([0.1234001, 0.23451], [0.13245, 0.674532]),
        ],
    )
    def test_addition_finite_field(self, a: List[float], b: List[float]) -> None:
        """Tests addition of encoded tensors, compares result with regular addition."""
        sec = SecureShare()
        encoded_a = sec._encode_finite_field(
            _AdaptorForPyTorchTensor(torch.tensor(a, dtype=torch.float32))
        )
        encoded_b = sec._encode_finite_field(
            _AdaptorForPyTorchTensor(torch.tensor(b, dtype=torch.float32))
        )
        encoded_result = sec._add([encoded_a, encoded_b])
        decoded_result = sec._decode_finite_field(encoded_result)

        np.testing.assert_almost_equal(
            np.array(a) + np.array(b), decoded_result, decimal=4
        )

    @pytest.mark.parametrize(
        "prime_q, tensor, error, num_other_workers",
        [
            (5, [0.1, 0.2, 0.3], True, 0),
            (7, [0.1, -0.2, -0.3], False, 0),
            (7, [0.1, 0.2, 0.3], False, 0),
            (7, [0.1, -0.39, 0.39], False, 0),
            (7, [0.1, -0.4, 0.39], True, 0),
            (7, [0.1, -0.39, 0.4], True, 0),
            (13, [0.1, -0.2, -0.3], False, 1),
            (13, [0.1, 0.2, 0.3], True, 2),
            (13, [0.1, -0.39, 0.39], True, 3),
        ],
    )
    def test_encode_finite_field_secure_share_error(
        self, error: bool, num_other_workers: int, prime_q: int, tensor: List[float]
    ) -> None:
        """Ensures SecureShareError is raised appropriately during encoding.

        When there are not enough positive integers in prime_q to map every positive
        and negative integer to an integer in the finite field without multiple values
        corresponding to the same value, a SecureShareError should be raised. When the
        precision is low and we still have floats after multiplying by `precision`, the
        number is truncated. This is why 0.39 does not raise a SecureShareError when
        `prime_q` is 7 but 0.4 does.
        """
        sec = SecureShare(prime_q=prime_q, precision=10)
        sec._own_shares = [1]
        sec._own_shares = sec._own_shares * num_other_workers
        if error:
            with pytest.raises(SecureShareError):
                sec._encode_finite_field(_AdaptorForPyTorchTensor(torch.tensor(tensor)))
        else:
            sec._encode_finite_field(_AdaptorForPyTorchTensor(torch.tensor(tensor)))

    def test_get_random_number(self) -> None:
        """Tests _get_random_number method."""
        sec = SecureShare(prime_q=101, precision=10)
        assert sec._own_shares == []
        for i in range(1, 10):
            sec._get_random_number()
            assert len(sec._own_shares) == i
            assert sec._own_shares[-1] < sec.prime_q

    @pytest.mark.parametrize(
        "input, output",
        [
            ([0.6, 0.7, 0.8], [1, 2, 3]),
            ([-1, -4, -3], [994, 964, 974]),
            ([-2, -3, 4.1], [984, 974, 36]),
        ],
    )
    def test_encode_secret(self, input: List[float], output: List[int]) -> None:
        """Tests _encode_secret method with fixed shares and simple tensors."""
        sec = SecureShare(prime_q=1009, precision=10)
        sec._own_shares = [-2, 3, 4]
        encoded_secret = sec._encode_secret(
            _AdaptorForPyTorchTensor(torch.tensor(input))
        )
        assert isinstance(encoded_secret, np.ndarray)
        np.testing.assert_array_equal(encoded_secret, np.array(output))

    def test_reconstruct_secret(self) -> None:
        """Tests _reconstruct_secret with simple tensors."""
        sec = SecureShare(prime_q=101, precision=10)
        reconstructed = sec._reconstruct_secret([np.array([1, 2, 3]), 4, 5, 6])
        assert isinstance(reconstructed, np.ndarray)
        assert len(reconstructed) == 3
        np.testing.assert_array_equal(reconstructed, np.array([16, 17, 18]))

    def test_encode_and_reconstruct_update(self) -> None:
        """Tests _encode_and_reconstruct_update with simple tensors."""
        sec = SecureShare()
        state_dict: _Weights = {
            "tensor_a": _AdaptorForPyTorchTensor(torch.tensor([-0.1, 0.9, 1.9])),
            "tensor_b": _AdaptorForPyTorchTensor(torch.tensor([-1.0, 0.0, 1.0])),
        }
        encoded_state_dict = sec._encode_and_reconstruct_update(state_dict)
        assert isinstance(encoded_state_dict, dict)
        assert len(encoded_state_dict) == 2
        for param in encoded_state_dict.values():
            assert isinstance(param, np.ndarray)
            assert len(param) == 3

    async def test_do_secure_aggregation(self, mocker: MockerFixture) -> None:
        """Tests do_secure_aggregation method.

        Mocks out transport layer and makes the relevant assertions on calls/awaits.
        """
        sec = SecureShare()
        state_dict: Dict[str, _TensorLike] = {
            "tensor_a": _AdaptorForPyTorchTensor(torch.tensor([-0.1, 0.9, 1.9])),
            "tensor_b": _AdaptorForPyTorchTensor(torch.tensor([-1.0, 0.0, 1.0])),
        }
        num_other_pods = 3
        mock_mailbox = create_autospec(_WorkerMailbox, instance=True)

        # Create mocks for transport layer send and receive functions.
        def mock_send(secure_share_generator: Any, _mailbox: Any) -> None:
            """Mocks `_send_secure_shares_to_others` transport layer function."""
            for _ in range(num_other_pods):
                # As the result of this callable is stored on `SecureShare.own_shares`
                # we have to mock out the calls to it here.
                secure_share_generator()

        secure_share_send_mock: MagicMock = mocker.patch(
            "bitfount.federated.secure._send_secure_shares_to_others"
        )
        secure_share_send_mock.side_effect = mock_send
        secure_share_receive_mock: AsyncMock = mocker.patch(
            "bitfount.federated.secure._get_worker_secure_shares"
        )
        secure_share_receive_mock.return_value = [1, 2, 3]

        await sec.do_secure_aggregation(state_dict, mock_mailbox)

        # Assertions
        assert secure_share_send_mock.call_count == 1
        # This should only be awaited once as it returns all shares
        assert secure_share_receive_mock.await_count == 1
        # We should have generated one share per other pod
        assert len(sec._own_shares) == num_other_pods
        # We should have received one share from each other pod
        assert len(sec._other_worker_shares) == num_other_pods

    def test_average_and_decode_state_dicts(self) -> None:
        """Tests `average_and_decode_state_dicts` works correctly."""
        state_dict_a = {
            "tensor_a": torch.tensor([-0.9, 0.1, 1.1]),
            "tensor_b": torch.tensor([-2.0, -1.0, 0.0]),
        }
        state_dict_b = {
            "tensor_a": torch.tensor([-0.1, 0.9, 1.9]),
            "tensor_b": torch.tensor([-1.0, 0.0, 1.0]),
        }
        sec_a = SecureShare(prime_q=1009, precision=10)
        sec_b = SecureShare(prime_q=1009, precision=10)
        rand_a = sec_a._get_random_number()
        rand_b = sec_b._get_random_number()
        sec_a._other_worker_shares.append(rand_b)
        sec_b._other_worker_shares.append(rand_a)
        encoded_state_dict_a = sec_a._encode_and_reconstruct_update(
            cast(_Weights, state_dict_a)
        )
        encoded_state_dict_b = sec_b._encode_and_reconstruct_update(
            cast(_Weights, state_dict_b)
        )

        average_state_dict = sec_a.average_and_decode_state_dicts(
            [encoded_state_dict_a, encoded_state_dict_b], dtype=torch.float32
        )

        expected_average = [
            torch.tensor([-0.5, 0.5, 1.5]),
            torch.tensor([-1.5, -0.5, 0.5]),
        ]

        for x, y in zip(average_state_dict.values(), expected_average):
            if isinstance(x, _AdaptorForPyTorchTensor):
                assert torch.equal(x.torchtensor, y)
            else:
                assert torch.equal(cast(torch.Tensor, x), y)

    @pytest.mark.parametrize(
        "a, b",
        [
            ([13, 10], [29, 1]),
            ([13, 50], [49, 7]),
            ([-13, -50], [-49, -7]),
            ([-126, -41], [109, 111]),
            ([-123, 50], [-1, 17]),
            ([-123.23, 50.1], [-1.01, 16.99]),
            ([0.1234001, 0.23451], [0.13245, 0.674532]),
        ],
    )
    def test_secure_averaging_with_simple_tensors_without_mailbox(
        self, a: List[float], b: List[float]
    ) -> None:
        """Tests secure averaging with simple tensors.

        The methods concerning the sharing and receiving of shares have been bypassed.
        """
        sec_a = SecureShare()
        sec_b = SecureShare()
        tensor_a = _AdaptorForPyTorchTensor(torch.tensor(a, dtype=torch.float64))
        tensor_b = _AdaptorForPyTorchTensor(torch.tensor(b, dtype=torch.float64))
        rand_a = sec_a._get_random_number()
        rand_b = sec_b._get_random_number()
        sec_a._other_worker_shares.append(rand_b)
        sec_b._other_worker_shares.append(rand_a)
        encoded_tensor_a = sec_a._encode_and_reconstruct_update({"tensor": tensor_a})
        encoded_tensor_b = sec_b._encode_and_reconstruct_update({"tensor": tensor_b})

        encoded_result = sec_a._add(
            [encoded_tensor_a["tensor"], encoded_tensor_b["tensor"]]
        )
        decoded_result = sec_a._decode_finite_field(encoded_result)

        np.testing.assert_almost_equal(
            np.array(a) + np.array(b), decoded_result, decimal=4
        )

    @pytest.mark.parametrize("num_workers", [2, 3, 5])
    async def test_secure_averaging_with_simple_tensors(
        self,
        mock_secure_transport_methods: Mock,
        mocker: MockerFixture,
        num_workers: int,
    ) -> None:
        """Tests secure averaging with simple tensors.

        The methods which rely on the transport layer have been mocked.
        """
        worker_shares: Dict[str, List[SecureShare]] = {}
        nn_params: List[_Weights] = []
        for i in range(num_workers):
            params = {
                "tensor": torch.tensor([-5.1, -3.2, -1.3], dtype=torch.float64) + i
            }
            nn_params.append(cast(Dict[str, _TensorLike], params))
            worker_shares[f"worker_{i}"] = []

        mocker.patch.object(
            SecureShare,
            "_share_own_shares",
            autospec=True,
            side_effect=partial(mock_secure_transport_methods[0], worker_shares),
        )
        mocker.patch.object(
            SecureShare,
            "_receive_worker_shares",
            autospec=True,
            side_effect=partial(mock_secure_transport_methods[1], worker_shares),
        )

        secures = []

        for name in worker_shares:
            sec = SecureShare()
            sec.name = name  # type: ignore[attr-defined] # Reason: name attr is only used in our patched functions above # noqa: B950
            await sec._share_own_shares(None)  # type: ignore[arg-type] # Reason: the function is mocked # noqa: B950
            secures.append(sec)

        for sec in secures:
            await sec._receive_worker_shares(None)  # type: ignore[arg-type] # Reason: the function is mocked # noqa: B950

        encoded_weights = []

        for i, sec in enumerate(secures):
            reconstructed_secret = list(
                sec._encode_and_reconstruct_update(nn_params[i]).values()
            )
            encoded_weights.append(reconstructed_secret[0])

        summed_weights = encoded_weights[0]
        for i in range(1, len(encoded_weights)):
            summed_weights = sec._add([summed_weights, encoded_weights[i]])

        decoded: torch.Tensor = torch.tensor(sec._decode_finite_field(summed_weights))
        insecure_sum: torch.Tensor = torch.sum(
            torch.stack([cast(torch.Tensor, list(p.values())[0]) for p in nn_params]),
            dim=0,
        )
        for decoded_item, insecure_item in zip(decoded, insecure_sum):
            assert torch.isclose(decoded_item, insecure_item, atol=1e-4)

    @pytest.mark.parametrize(
        "num_workers",
        [2, 3, 10],
    )
    async def test_secure_averaging_with_neural_network_parameters(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        mock_secure_transport_methods: Mock,
        mocker: MockerFixture,
        num_workers: int,
    ) -> None:
        """Tests secure averaging with neural network parameters.

        The methods which rely on a transport layer have been mocked.
        """
        worker_shares: Dict[str, List[SecureShare]] = {}
        nn_params = []
        for i in range(num_workers):
            nn = PyTorchTabularClassifier(
                datastructure=datastructure, schema=BitfountSchema(), seed=i, epochs=2
            )
            nn.initialise_model(datasource)
            params = copy.deepcopy(nn.get_param_states())
            nn_params.append(nn._get_torch_tensor_states(params))
            worker_shares[f"worker_{i}"] = []
        weight_update = nn_params[0]
        for i in range(1, len(nn_params)):
            for param in nn_params[i]:
                weight_update[param] = weight_update[param] + nn_params[i][param]

        for param in weight_update:
            weight_update[param] = weight_update[param] / len(nn_params)

        mocker.patch.object(
            SecureShare,
            "_share_own_shares",
            autospec=True,
            side_effect=partial(mock_secure_transport_methods[0], worker_shares),
        )
        mocker.patch.object(
            SecureShare,
            "_receive_worker_shares",
            autospec=True,
            side_effect=partial(mock_secure_transport_methods[1], worker_shares),
        )

        secures = []

        for name in worker_shares:
            sec = SecureShare()
            sec.name = name  # type: ignore[attr-defined] # Reason: name attr is only used in our patched functions above # noqa: B950
            await sec._share_own_shares(None)  # type: ignore[arg-type] # Reason: the function is mocked # noqa: B950
            secures.append(sec)

        for sec in secures:
            await sec._receive_worker_shares(None)  # type: ignore[arg-type] # Reason: the function is mocked # noqa: B950

        encoded_weights: List[Dict[str, np.ndarray]] = []

        for i, sec in enumerate(secures):
            reconstructed_state_dict: Dict[
                str, np.ndarray
            ] = sec._encode_and_reconstruct_update(
                nn._get_torch_adapter_states(nn_params[i])
            )
            encoded_weights.append(reconstructed_state_dict)

        secure_decoded_average = sec.average_and_decode_state_dicts(
            encoded_weights, dtype=torch.float32
        )
        secure_decoded_average_tensors = {}
        for k, v in secure_decoded_average.items():
            if isinstance(v, _AdaptorForPyTorchTensor):
                secure_decoded_average_tensors[k] = v.torchtensor
            elif isinstance(v, torch.Tensor):
                secure_decoded_average_tensors[k] = v
        for param in nn_params[0]:
            insecure_average = nn_params[0][param]
            for i in range(1, len(nn_params)):
                insecure_average += nn_params[i][param]
            insecure_average /= len(nn_params)
            assert torch.isclose(
                torch.mean(insecure_average),
                torch.mean(secure_decoded_average_tensors[param]),
                atol=1e-4,
            )
