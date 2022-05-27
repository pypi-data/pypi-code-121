"""Contains pytest fixtures related to hub and access manager interactions."""
import inspect
from typing import cast
from unittest.mock import Mock

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from pytest import fixture
from pytest_mock import MockerFixture


@fixture
def authoriser_public_key() -> RSAPublicKey:
    """Authoriser public key fixture."""
    serialized = inspect.cleandoc(
        """-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAifKZtWWu9JqavRu1pZOS
        / 9NKyWJ7gvTCibVeoXpiSvRaVVnaQ+VIQveMWr3O5871CKLB1DtDjpLw1hyvOIg6
        FTzt2odicizRUML / RAHzKEbZ1fWaCt9imjtsESrJN2rumjmtvO96CU8BLaIAx7Kv
        khd1HWeMKxQzekTjo4AU80T4CJMWSKzliNFxo6YFEP8FVwQmV7Q0C4F8mV9Qv0hu
        bV96wY2H0DsPDRXbUcoETBjFZG25+JxrsaV3fMxJmK / 3OBO8JQ0O9yvfAk8wCGLB
        coIEgiWGcbDS6x3uzbutYaONvgzaGm5Ysj8HjfujaJbptVjXB / 6+KkMANHWtFcva
        wQIDAQAB
        -----END PUBLIC KEY-----"""
    )
    return cast(
        RSAPublicKey,
        serialization.load_pem_public_key(
            serialized.encode(), backend=default_backend()
        ),
    )


@fixture
def access_manager_private_key() -> RSAPrivateKey:
    """Access manager private key fixture."""
    serialized = inspect.cleandoc(
        """-----BEGIN RSA PRIVATE KEY-----
        MIIEogIBAAKCAQEAyXmGr0cJ3ZfBrllSI1YQKuDp5UIa+zn3PksveKea4fbqQhZ2
        0mBMJNGDxgUCucF8R9PbbsY801qcLTBlZgc4H/OJd8PE1Wv+gxPH5akYxb9v7ZoZ
        H5In6Vv9UwxoJP3yxHegcnx5ayIpfAvIqtYMM01gdNxUKMpxWyNhnDIG7qHzZTnK
        JS3mmOVJxT9F8QNVzG39v3SsjstQDKAGunA63JEl0jtsqBg4Z34TQ/vVkwtaVmA4
        x6UTQgEOMtgftp607r8FrZt/4rYuI1WUiwrS2enqDc8ALRKCRzWmvJcqKfKmS0JG
        /TOQKsUfFGAhOpqodI1VyhMPhFaH+RMdOIZRfQIDAQABAoIBAA7Uey17tSYyfXcv
        6/Pd6eK+G3lcnE/RvHlBX4UqESSA4E1tCeICZJhxM5nn1IOH0nYXChflT6TfDo/k
        +BHChkcTzhKavmpXQKy1UAl/oOstZDfBGAhS4c0zkDoEt8XBS5VamNzUfLt+ED+p
        PmQUzWEZWPhBH5DBFgb3W7/7jrcR4zXaDL2G9Jmr2B6YZbHsGNJevfLx2HB5n4Kp
        DhiIT+NPUNVeMRwcQVvJbfZzPpxc0+Km+0xCi2ggIIPbGv4LdCryxreydCRgstnh
        TRQE5y3rl8UGX7dn311EFyxeLsPg6lCbjbzC2u/HgAiiiuARxaoWN2qgykZVbs8y
        3fevLgECgYEA70Vlda9EnzGV4ayqld9940H+9uYwuqWsTG2Nn9anlRpNzpBqN9oZ
        mQSz5pLxUejdXV8BP1uBc6cJsGca72u4UYtI0wdINHvRnO8TH0MkTrOacpiOSBQv
        f5poi6ZyFHUQZhxQP5n9i/WCCW65M72DYJYPnyvbylzp0gb12HYzQM0CgYEA14+h
        P0F/B7BO4xWU4ndRFTjxxPRydxgi1ffFhPK6MNEqEqgvHHvF3jdWmxRR/mD5wY7H
        8gh8Xu7WpHu7jTTn+BBOoHmvpDGRZcOI/NpDUlQDmIona19iA60K2ogQHanc09gG
        61nW70P95NE+Tbi0e3VsOi6MxJBNcjKOWQB1k3ECgYAWYkSanNnrlqTx5shSmwTY
        5MyoZmJ6o5MZ10nfgSJOVZaf02zMas/oO8Nkt6xxwDotSP0B41qZ6i+C3DJt4YLt
        xfz7GPxNRKQYbVk5nHtiDXVOcS0mWxUSd+x93AViGo19L/rl6E8K793Jah1TVNBc
        kc1GU8ENDmIlbtdC99PVpQKBgBhc3F2Y2nGVBKV3t/cMgzaB1Bltg05ghPdn5IQN
        JuwDh9zJ82ElwAxIdtpaJpY4gaHVsFVzjhLwrYOzlFP2Sc1okmpitm45R/SXb/Eb
        /gXdBvcDjkb9ZceClDp0rFWd8B5lSQrqgXdTWOu2lnMUUBmwAMZmonRI1uf0PNBk
        U+WRAoGAal4aCAJjW63QbLS7yipDP63vMqKE1Pg5mkksQ7NHP9W7KHsB9IQO9JZQ
        5BKyFv6dY7Dk5jHqa9J/tO/YHI5C2/hOe/pXBiarHNSE6MR/ItK6X30oW5rYj/aO
        OhEdX5Mr37Fa9UKGdkBZ7VbpYlIAnMCccuus4cZG3az/5BQTEy0=
        -----END RSA PRIVATE KEY-----"""
    )
    return cast(
        RSAPrivateKey,
        serialization.load_pem_private_key(
            serialized.encode(), backend=default_backend(), password=None
        ),
    )


@fixture
def access_manager_public_key() -> RSAPublicKey:
    """Access manager public key fixture."""
    serialized = inspect.cleandoc(
        """-----BEGIN RSA PUBLIC KEY-----
        MIIBCgKCAQEAyXmGr0cJ3ZfBrllSI1YQKuDp5UIa+zn3PksveKea4fbqQhZ20mBM
        JNGDxgUCucF8R9PbbsY801qcLTBlZgc4H/OJd8PE1Wv+gxPH5akYxb9v7ZoZH5In
        6Vv9UwxoJP3yxHegcnx5ayIpfAvIqtYMM01gdNxUKMpxWyNhnDIG7qHzZTnKJS3m
        mOVJxT9F8QNVzG39v3SsjstQDKAGunA63JEl0jtsqBg4Z34TQ/vVkwtaVmA4x6UT
        QgEOMtgftp607r8FrZt/4rYuI1WUiwrS2enqDc8ALRKCRzWmvJcqKfKmS0JG/TOQ
        KsUfFGAhOpqodI1VyhMPhFaH+RMdOIZRfQIDAQAB
        -----END RSA PUBLIC KEY-----"""
    )
    return cast(
        RSAPublicKey,
        serialization.load_pem_public_key(
            serialized.encode(), backend=default_backend()
        ),
    )


@fixture
def modeller_public_key_string() -> str:
    """Modeller public key as a string fixture."""
    return inspect.cleandoc(
        """
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAruIdWcWQKIph+mQd6XVk
        nbs95a0mslUq7Y6ukeCgE1nwqphTMDYefbvCXNQ9C1CX/b7ydyoZBSQ92RdsR19t
        J6AzpfZco3DflTamqxiqxyy75uMNni/hos6sCU0MR82IbvIe9IrA+ZXWsWDuJXsy
        mHNLvJ+nhD4w26y4+cu4ONxo9vW0+hFHzC2yg8RS9AsjwQ/NzmUvw2nGkbR4FfZZ
        GUONQhvqKr96nDBsWx2nmIjO3uDnI0pK9JLiT30M2Gma+QK5WQI7zYZYkXZRY4rf
        8Lsc5DO9Tc6MLEaNv46m332rVMNtl5o0TPuHLFIkN6hg58z4WRmZvSLswG6972qY
        NwIDAQAB
        -----END PUBLIC KEY-----"""
    )


@fixture
def modeller_public_key(modeller_public_key_string: str) -> RSAPublicKey:
    """Modeller public key fixture."""
    return cast(
        RSAPublicKey,
        serialization.load_pem_public_key(
            modeller_public_key_string.encode(), backend=default_backend()
        ),
    )


@fixture
def modeller_private_key() -> RSAPrivateKey:
    """Modeller private key fixture."""
    serialized = inspect.cleandoc(
        """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEAruIdWcWQKIph+mQd6XVknbs95a0mslUq7Y6ukeCgE1nwqphT
        MDYefbvCXNQ9C1CX / b7ydyoZBSQ92RdsR19tJ6AzpfZco3DflTamqxiqxyy75uMN
        ni / hos6sCU0MR82IbvIe9IrA+ZXWsWDuJXsymHNLvJ+nhD4w26y4+cu4ONxo9vW0
        +hFHzC2yg8RS9AsjwQ / NzmUvw2nGkbR4FfZZGUONQhvqKr96nDBsWx2nmIjO3uDn
        I0pK9JLiT30M2Gma+QK5WQI7zYZYkXZRY4rf8Lsc5DO9Tc6MLEaNv46m332rVMNt
        l5o0TPuHLFIkN6hg58z4WRmZvSLswG6972qYNwIDAQABAoIBAFjnwK4Tnq7NcvPd
        E8vMj0MUnmn1tbdxTqqIH70vaZGM5qmDWL8otCWNX0jb6NCovywTd6YW87NGcl67
        5qL+IzrC2Z7keMHqLu / nYaGXn7Izzq6Y / SJPCzE+Sf1MexLBrTthwVTmeSYpA4UX
        VtodIGKaMoWI0JuNFj+HNl5fL59PrfcPoDeo5rmm161fhIfaROvXBl526nowRZwC
        Z1Z / DmJfYOerO07m6Mx4LQwPOM5+WxqorN+rL+ / ARgLBF3K8ehYqHAjyskq73UzG
        33fBqlB9YfyYrDHSfdY5tQFCxreg5mrLI7rH0mtDct03QSR7EXFfc+Xp2875m8qi
        +vAeo4kCgYEA5fsWZZcKdwJxeNZoKweoHFEvGEQ7SQ4QYY3U3tlffVXrMNXFQ7XG
        RgQjw2wtDEz15yGYDezxfIFoeIACi2Kf3ZGNi697Jq68FYcKClz0sNX94ArfqivT
        wUrZEKmAFB5xZ52TzMdJs0B8G7dN2Mo9x8LadGZ4iJY8WgSTDq43b6sCgYEAwqs9
        9OKfT / M5JTqh1zu7HhKTAGoLGPGtJjDFApT1Df0RQtIOG6QYqEsM9plbJJ8kJ4+F
        kbZTxNh7cMGhsPxK / WW0ToCPVUDb06L1sSggEZEeHGaLE6TMVNZKLBl6VpZMYptO
        GRSkVxJegGPndGguoIRxJEwlmzz5Ed4VWMnb3aUCgYEAoBeSdrOW2FN+FAUEzHdv
        Ag9NflH5BxjgNFicB2k // KqzpvIYeNLvq8uz7ZS / IyHrx7Jt+7umOuqGg+NwYgEM
        khuBcex9COd4DHBNf / tHZlYAfVZ0bixGIvbsdZnYi6jJfryFp3ZPCpXoDw8iBLh8
        GzO8CG1QmJwkdPFcQUrrUjMCgYA2dW1pupRS63oLHjH0YnNgYFXbgc8E9Wc5Dd+v
        bzh251sS1Gy58tgrDIPd4N0Mi7CzmIUHVHhu0xkFXEX9mzbnWLJuW6y9bt2QgUA2
        hUEjaPOBgnZZ0nqPKTuqxp3g5z8LPuNERPAMo8joJgq0GAkjQqncO6kxmocbJoPW
        SPJHOQKBgQC7bspk7qkMthCSdpnvgBpeJI+FLgQkh46jw5b2NEoVs5VzOpYklQxV
        ddeMJgGRrmp2lzMU8oVlhtaElgCW / 11U4SbTPrktxFQWKP4gpVZ / qM6OFitUMv88
        D9yDvPTnj / Wyc2lpbhJF1GL8bzj / ygQfACjne2IGMJovOgc1hcxdHw ==
        -----END RSA PRIVATE KEY-----"""
    )
    return cast(
        RSAPrivateKey,
        serialization.load_pem_private_key(
            serialized.encode(), password=None, backend=default_backend()
        ),
    )


@fixture
def modeller_message() -> str:
    """Example modeller message."""
    return "TEST Message"


@fixture
def bitfount_model_correct_structure() -> str:
    """Example good BitfountModel."""
    return inspect.cleandoc(
        """
        from typing import Optional
        from bitfount.models.bitfount_model import BitfountModel
        from bitfount.federated.mixins import _DistributedModelMixIn

        class MyModel(BitfountModel, _DistributedModelMixIn):

            def __init__(self, **kwargs) -> None:
                super().__init__(**kwargs)
                self.epochs: Optional[int] = 1
                self.steps: Optional[int] = None
                self._total_num_batches_trained: int = 0

            @staticmethod
            def backend_tensor_shim():
                ...

            def tensor_precision(self):
                ...

            def get_param_states(self):
                ...

            def apply_weight_updates(self):
                ...

            def update_params(self):
                ...

            def deserialize_params(self):
                ...

            def serialize_params(self):
                ...

            def diff_params(self):
                ...

            def set_model_training_iterations(self):
                ...

            def reset_trainer(self) -> None:
                ...

            def fit(self):
                ...

            def log_(self):
                ...

            def initialise_model(self):
                ...

            def evaluate(self):
                ...

            def serialize(self):
                ...

            def deserialize(self):
                ...

            def _fit_local(self):
                ...
        """
    )


@fixture
def bitfount_model_incorrect_structure() -> str:
    """Example BitfountModel which doesn't implement DistributedModelProtocol.

    Some required methods from `bitfount_model_correct_structure` have been
    commented out.
    """
    return inspect.cleandoc(
        """
        from bitfount.models.bitfount_model import BitfountModel

        class MyModel(BitfountModel):

            def __init__(self, **kwargs) -> None:
                super().__init__(**kwargs)
                self.epochs: Optional[int] = 1
                self.steps: Optional[int] = None
                self._total_num_batches_trained: int = 0

            @staticmethod
            def backend_tensor_shim():
                ...

            def tensor_precision(self):
                ...

            def get_param_states(self):
                ...

            def apply_weight_updates(self):
                ...

            # def update_params(self):
            #     ...

            # def diff_params(self):
            #     ...

            def set_model_training_iterations(self):
                ...

            def reset_trainer(self) -> None:
                ...

            def fit(self):
                ...

            def log_(self):
                ...

            def initialise_model(self):
                ...

            def evaluate(self):
                ...

            def serialize(self):
                ...

            def deserialize(self):
                ...

            def _fit_local(self):
                ...
        """
    )


@fixture
def bitfount_model_correct_structure_size(bitfount_model_correct_structure: str) -> int:
    """Size of the correct structure BitfountModel fixture in storage."""
    return len(bitfount_model_correct_structure.encode("utf-8"))


@fixture
def mock_s3_data_upload_in_api_module(mocker: MockerFixture) -> Mock:
    """Mocks out the S3 data upload call in api.py.

    This call is used to upload the schema.
    """
    mock_s3_upload: Mock = mocker.patch(
        "bitfount.hub.api._upload_data_to_s3", autospec=True
    )
    return mock_s3_upload


@fixture
def mock_s3_file_upload_in_api_module(mocker: MockerFixture) -> Mock:
    """Mocks out the S3 file upload call in api.py.

    This call is used to upload models.
    """
    mock_s3_upload: Mock = mocker.patch(
        "bitfount.hub.api._upload_file_to_s3", autospec=True
    )
    return mock_s3_upload


@fixture
def mock_s3_data_download_in_api_module(mocker: MockerFixture) -> Mock:
    """Mocks out the S3 data download call in api.py.

    This call is used to download the schema.
    """
    mock_s3_download: Mock = mocker.patch(
        "bitfount.hub.api._download_data_from_s3", autospec=True
    )
    return mock_s3_download


@fixture
def mock_s3_file_download_in_api_module(mocker: MockerFixture) -> Mock:
    """Mocks out the S3 file download call in api.py.

    This call is used to download models.
    """
    mock_s3_download: Mock = mocker.patch(
        "bitfount.hub.api._download_file_from_s3", autospec=True
    )
    return mock_s3_download
