import os
import boto3
from base64 import b64decode
from .logger import setup_logging


class FunctionCoordinator():

    instance = None

    def __init__(self):
        self.coldstart_functions = []
        self.globals = {}
        self.function = None
        self.logger = setup_logging()

    @staticmethod
    def get():
        if not FunctionCoordinator.instance:
            FunctionCoordinator.instance = FunctionCoordinator()

        return FunctionCoordinator.instance

    @staticmethod
    def register_coldstart_function(function):
        coordinator = FunctionCoordinator.get()

        coordinator.coldstart_functions.append(function)

    def register_encrypted_vars(secrets):
        coordinator = FunctionCoordinator.get()

        coordinator.secrets = secrets

    @staticmethod
    def coldstart():
        coordinator = FunctionCoordinator.get()

        kms = None

        for env_var in os.environ:
            # Is this an encrypted variable?
            if env_var in coordinator.secrets:
                # Do we have a pre decrypted version of this var (for testing)
                if os.environ.get('decrypted_' + env_var, 'unset') == 'unset':
                    # Decrypt env var
                    if kms is None:
                        kms = boto3.client('kms')

                    coordinator.globals[env_var] = kms.decrypt(
                        CiphertextBlob=b64decode(os.environ[env_var]))['Plaintext']
                else:
                    # Use pre decrypted version
                    coordinator.globals[env_var] = bytes(os.environ['decrypted_' + env_var], 'utf-8')

            else:
                # Not an encrypted var just fetch it directly
                coordinator.globals[env_var] = os.environ[env_var]

        for func in coordinator.coldstart_functions:
            func(coordinator)

    @staticmethod
    def register_function(function):
        coordinator = FunctionCoordinator.get()

        coordinator.function = function

    @staticmethod
    def execute(event, context):
        coordinator = FunctionCoordinator.get()

        return coordinator.function(coordinator, event, context)


FunctionCoordinator.get()
