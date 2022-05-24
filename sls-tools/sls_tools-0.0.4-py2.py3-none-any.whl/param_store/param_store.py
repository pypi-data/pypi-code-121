import os
import boto3
import logging
from enum import Enum
from .param_store_result import ParamStoreResult


class ParamStore:
    """Provides access to key/values (variables) stored locally on the OS or AWS SSM.

    examples:

        # Set and get a value in SSM:
        ParamStore.set('MY_VAR', '123')
        my_var = ParamStore.get('MY_VAR').value
        >> '123'

        # Set and get a value from the OS:
        ParamStore.set('MY_VAR', '123', store=ParamStore.Stores.OS)
        my_var = ParamStore.get('MY_VAR').value
        >> '123'
        # Or explicitly:
        my_var = ParamStore.get('MY_VAR', store=ParamStore.Stores.OS).value
        >> '123'

        # Set and get a value in SSM and convert it to a list:
        ParamStore.set('MY_VAR', 'one,two,three')
        my_var = ParamStore.get('MY_VAR').to_list()
        >> ['one', 'two', 'three']
    """

    class Stores(Enum):
        """Enum for the available Key/Value stores.

        Supported options are: OS, SSM, AUTO

        "AUTO" is a reserved keyword that can be passed to each method to delegate
        the choice to each individual method.
        """
        OS = 'os'
        SSM = 'ssm'
        AUTO = 'auto'

    @classmethod
    def set(cls, key, value, store=Stores.SSM):
        """Sets a key/value pair.

        Args:
            key: The key to set.
            value: The value to set.
            store: Where to set the value. Defaults to Stores.SSM.

        Returns:
            True if successfully set otherwise False.
        """
        result = False

        # Set the value in the local environment.
        if store in [cls.Stores.OS, cls.Stores.AUTO]:
            result = cls._set_in_os(key, value)

        # Set the value in SSM.
        if store in [cls.Stores.SSM, cls.Stores.AUTO]:
            result = cls._set_in_ssm(key, value)

        return result

    @classmethod
    def get(cls, key, default=None, store=Stores.AUTO):
        """Gets the value for a key.

        Will return the value from the OS if its set otherwise it will try to get the value from SSM.
        
        Args:
            key: The key for the value to get.
            default: The value to return if the key value is None.
            store: Where to get the value from. Defaults to Stores.AUTO.

        Returns:
            ParamStoreResult
        """
        # Try to get the value from the local environment.
        if store in [cls.Stores.OS, cls.Stores.AUTO]:
            result = cls._get_from_os(key)
            if result is not None:
                return ParamStoreResult(key, result, cls.Stores.OS)

        # Try to get the value from SSM.
        if store in [cls.Stores.SSM, cls.Stores.AUTO]:
            result = cls._get_from_ssm(key)
            if result is not None:
                return ParamStoreResult(key, result, cls.Stores.SSM)

        return ParamStoreResult(key, default, None)

    @classmethod
    def delete(cls, key, store=Stores.AUTO):
        """Deletes a key/value.

        Args:
            key: The key to delete.
            store: Where to delete from. Defaults to Stores.AUTO.

        Returns:
            True if successfully deleted otherwise False.
        """
        result = False

        # Delete the value from the local environment.
        if store in [cls.Stores.OS, cls.Stores.AUTO]:
            result = cls._delete_from_os(key)

        # Delete the value from SSM.
        if store in [cls.Stores.SSM, cls.Stores.AUTO]:
            result = cls._delete_from_ssm(key)

        return result

    @classmethod
    def contains(cls, key, store=Stores.AUTO):
        """Gets if a key is present in one of the param stores.

        Args:
            key: The key to check for.
            store: Where to look for the key. Defaults to Stores.AUTO.

        Returns:
            True if the key is contained in the store.
        """
        result = cls.get(key, default=None, store=store)
        return result.store is not None and result.value is not None

    @classmethod
    def _get_from_os(cls, key):
        """Gets a value from the OS environment variables.

        Args:
            key: The key for the value to get.

        Returns:
            The key value or None.
        """
        return os.environ.get(key)

    @classmethod
    def _set_in_os(cls, key, value):
        """Sets a key/value in the OS environment.

        Args:
            key: The key to set.
            value: The value to set.

        Returns:
            True
        """
        os.environ[key] = value
        return True

    @classmethod
    def _delete_from_os(cls, key):
        """Deletes the key from the OS environment.

        Args:
            key: The key to delete.

        Returns:
            True
        """
        if key in os.environ.keys():
            del os.environ[key]

        return True

    @classmethod
    def _get_from_ssm(cls, key):
        """Gets a value from SSM.

        Args:
            key: The key for the value to get.

        Returns:
            The key value or None, or raises
        """
        result = None
        ssm_key = cls._build_ssm_key(key)
        client = cls._get_ssm_client()
        try:
            get_response = client.get_parameter(Name=ssm_key, WithDecryption=True)
            result = get_response.get('Parameter').get('Value')
        except client.exceptions.ParameterNotFound:
            logging.exception('SSM Parameter Not Found: {0}'.format(ssm_key))
        except Exception as ex:
            logging.exception('SSM Error: {0}'.format(ex))

        return result

    @classmethod
    def _set_in_ssm(cls, key, value, type='SecureString'):
        """Sets a key/value pair in SSM.

        Args:
            key: The key to set.
            value: The value to set.
            type: The SSM parameter type. Defaults to SecureString.

        Returns:
            True if successful otherwise False.
        """
        ssm_key = cls._build_ssm_key(key)
        try:
            cls._get_ssm_client().put_parameter(Name=ssm_key, Value=value, Type=type, Overwrite=True)
            return True
        except Exception as ex:
            logging.exception('SSM Error: {0}'.format(ex))
        return False

    @classmethod
    def _delete_from_ssm(cls, key):
        """Deletes a key in SSM.

        Args:
            key: The key to delete.

        Returns:
            True if successful or the key does not exist otherwise False.
        """
        ssm_key = cls._build_ssm_key(key)
        try:
            cls._get_ssm_client().delete_parameter(Name=ssm_key)
            return True
        except cls._get_ssm_client().exceptions.ParameterNotFound as ex:
            return True
        except Exception as ex:
            logging.exception('SSM Error: {0}'.format(ex))
        return False

    @classmethod
    def _build_ssm_key(cls, key):
        """Builds an SSM key.

        The format is "service_name/service_stage/key".

        Args:
            key: The key to build a fully qualified key for.

        Returns:
            The fully qualified key string.
        """
        service_name = cls.get('SERVICE_NAME', store=cls.Stores.OS).value
        service_stage = cls.get('SERVICE_STAGE', store=cls.Stores.OS).value

        if not service_name:
            raise ValueError('Environment variable not set: SERVICE_NAME')

        if not service_stage:
            raise ValueError('Environment variable not set: SERVICE_STAGE')

        return '/{0}/{1}/{2}'.format(service_name, service_stage, key)

    # Cached instance of the SSM client.
    _ssm_client = None

    @classmethod
    def _get_ssm_client(cls):
        """Gets an SSM boto3 client.

        Returns:
            SSM client or None.
        """
        try:
            if not cls._ssm_client:
                cls._ssm_client = boto3.client('ssm')
            return cls._ssm_client
        except Exception as ex:
            logging.exception('SSM Error: {0}'.format(ex))
        return None
