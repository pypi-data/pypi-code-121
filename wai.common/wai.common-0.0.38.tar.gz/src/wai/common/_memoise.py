"""
Provides memoisation of function calls.

For long-running functions, it is sometimes nice to store the result,
and then simply load it the next time the function is called with the same
parameters. This module uses pickle to store the result to disk, and to
load it again.

Instead of:

    result = func(*args, **kwargs)

you would call:

    factory = MemoiserFactory("/path/to/memo/files/")
    memo_func = factory(func)
    result = memo_func(*args, **kwargs)

The first call will run the function as usual, but subsequent calls will load
the result from disk instead.

N.B.:
    - All arguments to the function and the function's result must be picklable.
    - Function state/closures are not pickled. Should only be used with pure functions.
"""
import hashlib
import os
import pickle
from typing import Callable, Tuple, Dict, Any

# The hashing function to use
HASH = hashlib.sha256

# The extension for memo files
MEMO_EXTENSION = ".memo"


class MemoFile:
    """
    Class representing .memo files on disk as produced/consumed
    by the Memoiser class.
    """
    def __init__(self, directory: str, func: Callable, *args, **kwargs):
        self.pickled_func_and_args = pickle_function_and_arguments(func, *args, **kwargs)
        self.code_hash: bytes = hash_function_code(func)
        self.filename: str = normalise_directory(directory) + get_memo_filename(self.pickled_func_and_args)

    def exists(self) -> bool:
        """
        Whether this memo file exists on disk.

        :return:    True if the file exists, False if not.
        """
        return os.path.exists(self.filename)

    def save(self, result):
        """
        Saves the given result of the function to the file.

        :param result:      The result to save.
        """
        with open(self.filename, "wb") as file:
            file.write(self.pickled_func_and_args)
            file.write(self.code_hash)
            pickle.dump(result, file)

    def load(self):
        """
        Loads the result from this memo file. Raises an error if the
        result can't be loaded for any reason.

        :return:    The saved result.
        """
        try:
            with open(self.filename, "rb") as file:
                # Check that the file is valid
                self._check_stored_func_and_args(file)
                self._check_stored_code_hash(file)

                # Return the stored result
                return pickle.load(file)

        # Just re-raise any FNF or already-wrapped errors
        except (FileNotFoundError, InvalidMemoFileError):
            raise

        # Wrap any other errors
        except Exception as e:
            raise InvalidMemoFileError("Error reading " + self.filename + ": " + str(e)) from e

    def _check_stored_func_and_args(self, file):
        """
        Checks if the function/arguments stored in the given file
        are valid for this memo-file. Raises an error if not, and
        simply returns if they do.

        :param file:    The file handle.
        """
        try:
            stored_func_and_args = file.read(len(self.pickled_func_and_args))
        except Exception as e:
            raise InvalidMemoFileError("Error reading stored function/arguments from " +
                                       self.filename + ": " + str(e)) from e

        if self.pickled_func_and_args != stored_func_and_args:
            raise InvalidMemoFileError("Hash collision for " + self.filename)

    def _check_stored_code_hash(self, file):
        """
        Checks if the code hash stored in the given file
        is valid for this memo-file. Raises an error if not, and
        simply returns if it is.

        :param file:    The file handle.
        """
        try:
            stored_code_hash = file.read(len(self.code_hash))
        except Exception as e:
            raise InvalidMemoFileError("Error reading stored code hash from " +
                                       self.filename + ": " + str(e)) from e

        if self.code_hash == stored_code_hash:
            raise InvalidMemoFileError("Function code change invalidates " + self.filename)


class Memoiser:
    """
    Class that acts like the given function, except memoises the result
    to disk. If the function is then called with the same arguments,
    reads the result from disk instead.
    """
    def __init__(self, func: Callable, save_directory: str = ""):
        self.func: Callable = func
        self.save_directory: str = normalise_directory(save_directory)

        # Create the save directory if it doesn't exist yet
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def __call__(self, *args, **kwargs):
        # Get the memo file to use for this function/arguments
        memo_file: MemoFile = MemoFile(self.save_directory, self.func, *args, **kwargs)

        # Try to load the result
        try:
            if memo_file.exists():
                return memo_file.load()
        except InvalidMemoFileError:
            # Continue to normal function call if file loading fails
            pass

        # If loading failed, call the function
        result = self.func(*args, **kwargs)

        # Save the result for next time
        memo_file.save(result)

        # Return the result
        return result


class MemoiserFactory:
    """
    Class that produces Memoisers all using the same save directory.
    """
    def __init__(self, save_directory: str = ""):
        self.save_directory: str = normalise_directory(save_directory)

    def __call__(self, func: Callable) -> Memoiser:
        return Memoiser(func, self.save_directory)

    def sub_dir(self, path: str) -> 'MemoiserFactory':
        """
        Returns a factory for a sub-directory of this one.

        :param path:    The extended path of the sub-directory.
        :return:        The factory.
        """
        # Normalise the path
        path = normalise_directory(path)

        # Remove any leading separator
        if path.startswith(os.sep):
            path = path[1:]

        return MemoiserFactory(self.save_directory + path)


class InvalidMemoFileError(Exception):
    """
    Error for when a memo file is invalidated by a change in function code,
    or a hash-collision.
    """
    pass


def normalise_directory(directory: str) -> str:
    """
    Normalises a directory string so that a filename can
    be directly appended and used.

    :param directory:   The directory string to normalise.
    :return:            The normalised directory string.
    """
    # Add the final separator if not cwd and not already present
    if directory != "" and not directory.endswith(os.sep):
        directory += os.sep

    return directory


def get_memo_filename(data: bytes) -> str:
    """
    Generates a memo filename for a bytes.

    :param data:    The bytes.
    :return:        The filename.
    """
    # Hash the data and get the hex representation as a string
    data_hash = HASH(data).hexdigest()

    # Return the last 16 hex characters of the hash with the extension
    return data_hash[-16:] + MEMO_EXTENSION


def pickle_function_and_arguments(func: Callable, *args, **kwargs):
    """
    Creates a binary representation of a function and its arguments.

    :param func:    The function.
    :param args:    The positional arguments to the function.
    :param kwargs:  The keyword arguments to the function.
    :return:        The binary pickle representation.
    """
    return pickle.dumps((func, args, PicklableDict(kwargs)))


def hash_function_code(func: Callable) -> bytes:
    """
    Hashes the code of a function so that it can be identified
    when it changes.

    :param func:    The function to hash.
    :return:        The hash bytes.
    """
    return HASH(func.__code__.co_code).digest()


class PicklableDict:
    """
    Class which is a picklable representation of a dictionary
    (assuming all keys/values are picklable).
    """
    def __init__(self, dictionary: Dict[Any, Any]):
        # The internal representation of the dictionary
        self.intern: Tuple[Tuple[Any, Any], ...] = tuple(dictionary.items())

    def __eq__(self, other):
        if isinstance(other, PicklableDict):
            other = other.to_dict()

        if isinstance(other, dict):
            return other == self.to_dict()

        return False

    def to_dict(self) -> Dict[Any, Any]:
        """
        Reconstructs the dictionary.

        :return:    The dictionary.
        """
        return {key: value for key, value in self.intern}
