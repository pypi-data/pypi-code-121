"""Secure aggregation."""
from __future__ import annotations

import inspect
import logging
import secrets
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Mapping,
    Optional,
    Type,
    Union,
    cast,
)

from marshmallow import fields
import numpy as np

from bitfount.federated.exceptions import SecureShareError
from bitfount.federated.shim import _load_default_tensor_shim
from bitfount.federated.transport.worker_transport import (
    _get_worker_secure_shares,
    _InterPodWorkerMailbox,
    _send_secure_shares_to_others,
)
from bitfount.types import (
    T_FIELDS_DICT,
    T_NESTED_FIELDS,
    _BaseSerializableObjectMixIn,
    _Weights,
)

if TYPE_CHECKING:
    from bitfount.types import T_DTYPE, _TensorLike

# Can't be larger than 2^64 -1 (largest unsigned 64 bit integer). Otherwise we get:
# “OverflowError: Python int too large to convert to C long"
LARGE_PRIME_NUMBER: int = (2**59) - 1  # Largest possible Mersenne prime number.

# Precision does not need to be greater than this in order be able to perform lossless
# computation on IEEE 754 32-bit floating point values
FLOAT_32_BIT_PRECISION: int = 10**10

_secure_share_registry: Dict[str, Type[_BaseSecureShare]] = {}
secure_share_registry: Mapping[str, Type[_BaseSecureShare]] = MappingProxyType(
    _secure_share_registry
)
logger = logging.getLogger(__name__)


class _BaseSecureShare:
    @classmethod
    def __init_subclass__(cls, **kwargs: Any):
        if not inspect.isabstract(cls):
            logger.debug(f"Adding {cls.__name__}: {cls} to registry")
            _secure_share_registry[cls.__name__] = cls


class SecureShare(_BaseSecureShare, _BaseSerializableObjectMixIn):
    """Additive, replicated, secret sharing algorithm responsible for secure averaging.

    This secret sharing implementation is 'additive' because the secret can be
    reconstructed by taking the sum of all the shares it is split into, and 'replicated'
    because each party receives more than one share.

    The algorithm works as follows:
        1. First every worker shares a securely generated random number (between 0 and
        `prime_q`) with every other worker such that every worker ends up with one
        number from every other worker. These numbers are known as shares as they will
        form part of the secret (the weight update) which will be shared.
        2. The tensors in the weight update are then converted to positive integer field
        elements of a finite field bounded by `prime_q`.
        3. The random numbers generated are used to compute a final share for every
        tensor in the weight update. This final share has the same shape as the secret
        tensor.
        4. This final share is then reconstructed using the shares retrieved from the
        other workers. At this point, the final share from each worker is meaningless
        until averaged with every other weight update.
        5. This final share is sent to the modeller where it will be averaged with the
        updates from all the other workers (all the while in the finite field space).
        6. After averaging, the updates are finally decoded back to floating point
        tensors.

    Args:
        tensor_shim: Provides backend-specific tensor methods.
        prime_q: Large prime number used in secure aggregation. This should be a
            few orders of magnitude larger than the precision so that when we add
            encoded finite field elements with one another, we do not breach the limits
            of the finite field. A `SecureShareError` is raised if this occurs. Defaults
            to 2^59 -1 (the largest Mersenne 64 bit Mersenne prime number - for ease).
        precision: Degree of precision for floating points in secure aggregation
            i.e. the number of digits after the decimal point that we want to keep.
            Defaults to 10^10.

    Attributes:
        prime_q: Large prime number used in secure aggregation.
        precision: Degree of precision for floating points in secure aggregation.

    :::note

    The relationships between individual elements in the tensors are preserved in
    this implementation since our shares are scalars rather than vectors. Therefore,
    whilst the secret itself cannot be reconstructed, some properties of the secret can
    be deciphered e.g. which element is the largest/smallest, etc.

    :::
    """

    # TODO: [BIT-423] Review security
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "prime_q": fields.Integer(),
        "precision": fields.Integer(),
    }
    nested_fields: ClassVar[T_NESTED_FIELDS] = {}

    def __init__(
        self,
        prime_q: int = LARGE_PRIME_NUMBER,
        precision: int = FLOAT_32_BIT_PRECISION,
    ):
        self.class_name = type(self).__name__
        self.prime_q = prime_q
        self.precision = precision

        self._tensor_shim = _load_default_tensor_shim()
        self._own_shares: List[int] = []
        self._other_worker_shares: List[int] = []

    def _encode_finite_field(self, rational: _TensorLike) -> np.ndarray:
        """Converts tensor `rational` to integer in finite field.

        Raises:
            SecureShareError: if finite field limit is breached. This is raised if there
                are not enough integers to represent all the possible floating point
                numbers in `rational`.
        """
        # Warning! on Windows astype(int) returns the min long value.
        # We use astype(np.int64) to avoid this.
        upscaled = self._tensor_shim.to_numpy(rational * self.precision).astype(
            np.int64
        )
        total_num_workers = len(self._own_shares) + 1
        if (
            ((upscaled * total_num_workers) > self.prime_q / 2)
            | ((upscaled * total_num_workers) < -self.prime_q / 2)
        ).sum() != 0:
            raise SecureShareError("Choose a larger `prime_q` or a smaller `precision`")
        field_element = upscaled % self.prime_q
        return field_element

    def _decode_finite_field(
        self, field_element: np.ndarray
    ) -> Union[float, np.ndarray]:
        """Converts finite field array back into tensor."""
        field_element = np.where(
            field_element > (self.prime_q / 2),
            field_element - self.prime_q,
            field_element,
        )
        rational = field_element / self.precision
        if isinstance(rational, np.ndarray):
            rational = rational.astype(float)
        return rational

    def _encode_secret(self, secret: _TensorLike) -> np.ndarray:
        """Encodes the provided secret using `self.own_shares` and returns it.

        Secret is first moved to the finite field space and then split into n shares
        where n is the number of all workers participating in training. All but one
        shares (integers) are shared with the other workers and the final share
        (a dictionary of tensors) is returned. The sum of all these will yield the
        original (encoded) secret.
        """
        secret_array = self._encode_finite_field(secret)
        encoded_secret = (secret_array - sum(self._own_shares)) % self.prime_q
        return encoded_secret

    def _reconstruct_secret(self, shares: List[Union[np.ndarray, int]]) -> np.ndarray:
        """Reconstructs the shares into a secret.

        This secret is not the same secret as originally encoded and shared. This secret
        is useless unless averaged with the secret outputs from all the other workers.
        """
        return np.asarray(sum(shares) % self.prime_q)

    def _encode_and_reconstruct_update(
        self, secret_update: _Weights
    ) -> Dict[str, np.ndarray]:
        """Encodes and reconstructs update from own and worker shares.

        Encrypts `secret_update` using `own_shares` then reconstructs it using
        provided `other_worker_shares`.
        """
        encrypted_params = [self._encode_secret(v) for _, v in secret_update.items()]
        reconstructed = [
            self._reconstruct_secret([*self._other_worker_shares, param])
            for param in encrypted_params
        ]
        return dict(zip(list(secret_update), reconstructed))

    def _get_random_number(self) -> int:
        """Generate a random number, append it to `self.own_shares` and also return it.

        Random number generator is cryptographically secure.
        """
        rand_num = secrets.randbelow(self.prime_q)
        self._own_shares.append(rand_num)
        return rand_num

    async def _share_own_shares(self, mailbox: _InterPodWorkerMailbox) -> None:
        """Sends own secure aggregation shares to other workers (one each).

        A random number is securely generated and sent to each worker such that each
        worker receives a different random number from every other worker. Each worker
        keeps a copy of the random numbers they generated which later become 'shares'
        as they can be used to encode a secret (the parameter update).
        """
        self._own_shares = []
        await _send_secure_shares_to_others(self._get_random_number, mailbox)

    async def _receive_worker_shares(self, mailbox: _InterPodWorkerMailbox) -> None:
        """Receives secure aggregation shares from other workers."""
        self._other_worker_shares = await _get_worker_secure_shares(mailbox)

    def _add(self, arrays: List[np.ndarray]) -> np.ndarray:
        """Add multiple encoded numpy arrays element-wise and return a numpy array.

        All arrays must have the same shape.
        """
        if arrays[0].size > 1:
            return np.array(
                [np.sum(arrs, axis=0) % self.prime_q for arrs in zip(*arrays)]
            )
        else:
            return np.asarray(np.sum(arrays, axis=0) % self.prime_q)

    def average_and_decode_state_dicts(
        self, state_dicts: List[Dict[str, np.ndarray]], dtype: Optional[T_DTYPE] = None
    ) -> _Weights:
        """Averages and decodes multiple encrypted parameter dictionaries.

        Computes the mean of all the `state_dicts` before decoding the averaged result
        and returning it.

        Args:
            state_dicts: List of dictionaries of model parameters as numpy arrays.
            dtype: Optional dtype of the tensors in the returned tensor parameters.

        Returns:
            A dictionary of averaged and decoded model parameters.

        """
        average_state_dict: Dict[str, _TensorLike] = {}
        for param in state_dicts[0]:
            summed_param = self._add([state_dict[param] for state_dict in state_dicts])
            average_decoded_param = self._decode_finite_field(summed_param) / len(
                state_dicts
            )
            average_state_dict[param] = self._tensor_shim.to_tensor(
                average_decoded_param, dtype=dtype
            ).squeeze()
        return cast(_Weights, average_state_dict)

    async def do_secure_aggregation(
        self,
        param_update: _Weights,
        mailbox: _InterPodWorkerMailbox,
    ) -> Dict[str, np.ndarray]:
        """Performs secure aggregation.

        Args:
            param_update: A dictionary of tensors to be securely aggregated.
            mailbox: A mailbox to send and receive messages from other workers.

        Returns:
            A dictionary of encoded parameters as numpy arrays.

        Raises:
            SecureShareError: if finite field limit is breached. This is raised if there
                are not enough integers to represent all the possible floating point
                numbers.
        """
        await self._share_own_shares(mailbox)
        await self._receive_worker_shares(mailbox)
        return self._encode_and_reconstruct_update(param_update)
