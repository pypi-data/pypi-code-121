import aiohttp
import asyncio
import contextlib
import logging
import os
import re
import shlex
import sys
import time
import typing
from . import artifacts
from . import context
from . import util


LOGGER = logging.getLogger(__name__)


def evaluate_composite_digests(
        outputs: typing.Iterable["artifacts.Artifact"],
        inputs: typing.Iterable["artifacts.Artifact"]) -> dict["artifacts.Artifact", bytes]:
    """
    Evaluate composite digests for all :code:`outputs`.

    A composite digest is defined as the digest of the digests of inputs and the digest of the
    output, i.e. it is a joint, concise summary of both inputs and outputs. A composite digest is
    :code:`None` if the corresponding output digest is :code:`None` or any input digests are
    :code:`None`.

    Args:
        inputs: Sequence of input artifacts.
        outputs: Sequence of output artifacts.

    Returns:
        digests: Mapping from outputs to composite digests.
    """
    # Evaluate input digests and abort if any of them are missing.
    input_digest = util.Crc32()
    for input in inputs:
        if input.digest is None:
            return {output: None for output in outputs}
        input_digest.update(bytes.fromhex(input.digest))

    # Construct composite digests for the outputs.
    return {
        output: util.Crc32(bytes.fromhex(output.digest), int(input_digest)).hexdigest() if
        output.digest is not None else None for output in outputs
    }


def cancel_all_transforms() -> None:
    """
    Cancel all running transforms.
    """
    try:
        tasks = asyncio.all_tasks()
    except RuntimeError:
        return

    for task in tasks:
        task.cancel()


class Transform(util.Once):
    """
    Base class for transforms that generates outputs given inputs. Inheriting classes should
    implement :meth:`execute`.

    Args:
        outputs: Artifacts to generate.
        inputs: Artifacts consumed by the transform.

    Attributes:
        stale_outputs: Sequence of outputs that are stale and need to be updated.
    """
    def __init__(self, outputs: typing.Iterable["artifacts.Artifact"],
                 inputs: typing.Iterable["artifacts.Artifact"]) -> None:
        super().__init__()
        self.inputs = artifacts.normalize_artifacts(inputs)
        for input in self.inputs:
            input.children.append(self)
        self.outputs = artifacts.normalize_artifacts(outputs)
        for output in self.outputs:
            output.parent = self

    def __iter__(self):
        for output in self.outputs:
            yield output

    async def execute(self) -> None:
        # Wait for all inputs artifacts.
        await asyncio.gather(*self.inputs)

        # Figure out which outputs are stale.
        stale_artifacts = self.stale_outputs
        if not stale_artifacts:
            LOGGER.debug("\U0001f7e2 artifacts %s are up to date", self.outputs)
            return

        if self.get_dry_run():
            LOGGER.info("\U0001f7e1 artifacts %s are stale; dry run", stale_artifacts)
            return

        LOGGER.info("\U0001f7e1 artifacts %s are stale; running transform", stale_artifacts)

        # Reset the composite digests of all outputs to ensure they get regenerated if the transform
        # fails.
        for output in self.outputs:
            metadata = context.get_current_context().artifact_metadata.get(output, {})
            metadata.pop("last_composite_digest", None)

        async with self.concurrency_context():
            try:
                # Execute the transform and measure the time.
                start = time.time()
                await self.apply()
                duration = time.time() - start

                # Update the composite digests.
                composite_digests = evaluate_composite_digests(self.outputs, self.inputs)
                for artifact, composite_digest in composite_digests.items():
                    metadata = \
                        context.get_current_context().artifact_metadata.setdefault(artifact, {})
                    metadata.update({
                        "last_composite_digest": composite_digest,
                        "last_duration": duration,
                    })

                LOGGER.info("\u2705 generated artifacts %s", self.outputs)
            except Exception as ex:
                LOGGER.error("\u274c failed to generate artifacts %s: %s", self.outputs, ex)
                raise

    @property
    def stale_outputs(self) -> typing.Iterable["artifacts.Artifact"]:
        # Get the outputs whose composite digests are `None` or different from the library of
        # composite digests.
        composite_digests = evaluate_composite_digests(self.outputs, self.inputs)
        current_context = context.get_current_context()
        return [
            output for output, composite_digest in composite_digests.items() if composite_digest is
            None or composite_digest !=
            current_context.artifact_metadata.get(output, {}).get("last_composite_digest")
        ]

    async def apply(self) -> None:
        """
        Apply the transform.
        """
        raise NotImplementedError

    def __repr__(self):
        inputs = ", ".join(map(repr, self.inputs))
        outputs = ", ".join(map(repr, self.outputs))
        return f"{self.__class__.__name__}([{inputs}] -> [{outputs}])"

    @classmethod
    def get_properties(cls):
        return context.get_current_context().get_properties(cls)

    @classmethod
    @contextlib.contextmanager
    def limit_concurrency(cls, num_concurrent):
        # We need to explicitly select the `Transform` key to ensure all transforms use the same
        # semaphore.
        properties = context.get_current_context().get_properties(Transform)
        if (semaphore := properties.get("semaphore")):  # pragma: no cover
            raise RuntimeError("semaphore is already set")
        if num_concurrent:
            semaphore = properties["semaphore"] = asyncio.Semaphore(num_concurrent)
        yield semaphore
        properties.pop("semaphore", None)

    @classmethod
    def concurrency_context(cls):
        properties = context.get_current_context().get_properties(Transform)
        if (semaphore := properties.get("semaphore")):
            return semaphore
        else:
            return util.noop_context()

    @classmethod
    def get_dry_run(cls) -> bool:
        return cls.get_properties().get("dry_run", False)

    @classmethod
    def set_dry_run(cls, dry_run: bool):
        cls.get_properties()["dry_run"] = dry_run


class _Sleep(Transform):
    """
    Sleeps for a given number of seconds and create any file artifact outputs. Mostly used for
    testing and debugging.

    Args:
        outputs: Artifacts to generate.
        inputs: Artifacts consumed by the transform.
        time: Number of seconds to sleep for.
    """
    def __init__(self, outputs: typing.Iterable["artifacts.Artifact"],
                 inputs: typing.Iterable["artifacts.Artifact"], *, sleep: float) -> None:
        super().__init__(outputs, inputs)
        self.sleep = sleep
        self.start = None
        self.end = None
        self.num_calls = 0

    async def apply(self) -> None:
        if self.num_calls:  # pragma: no cover
            raise RuntimeError("this transformation has already been applied")
        else:
            self.num_calls += 1
        self.start = time.time()
        LOGGER.debug("running %s for %f seconds...", self, self.sleep)
        await asyncio.sleep(self.sleep)
        for output in self.outputs:
            if isinstance(output, artifacts.File):
                with open(output.name, "w") as fp:
                    fp.write(output.name)
                LOGGER.debug("created %s", output)
        LOGGER.debug("completed %s", self)
        self.end = time.time()


class Download(Transform):
    """
    Download a file.

    Args:
        output: Output artifact for the downloaded data.
        url: Url to download from.

    Example:
        >>> data = bb.File("20news.tar.gz", expected_digest="af604312")
        >>> bb.Download(data, url="https://ndownloader.figshare.com/files/5975967")
        Download([] -> [File(20news.tar.gz)])
    """
    def __init__(self, output: "artifacts.File", url: str) -> None:
        super().__init__(output, [])
        self.url = url

    async def apply(self) -> None:
        # Abort if we already have the right file.
        # TODO: This should really rely on the digest of the URL rather than the artifact.
        output, = self.outputs
        if output.expected_digest and output.digest == output.expected_digest:
            return
        # Download the file.
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                with open(output.name, "wb") as fp:
                    fp.write(await response.read())


class Subprocess(Transform):
    r"""
    Execute a subprocess.

    The transform supports variable substitution using f-strings and Makefile syntax:

    - :code:`$@` represents the first output.
    - :code:`$<` represents the first input.
    - :code:`$^` represents all inputs.
    - :code:`$$@` represents the literal :code:`$@`, i.e. double dollars are properly escaped.
    - :code:`{outputs[0].name}` represents the name of the first output. The available f-string
      variables are :code:`outputs` and :code:`inputs`, each a list of
      :class:`Artifact <.artifacts.Artifact>`\ s.
    - :code:`$!` represents the current python interpreter.

    Environment variables are inherited by default, but global environment variables for all
    :class:`Subprocess` transforms can be specified by :meth:`set_global_env` or modifying
    :meth:`get_global_env`, and specific environment variables can be specified using the
    :code:`env` argument. Environment variables that are :code:`None` are removed from the
    environment of the transform.

    Args:
        outputs: Artifacts to generate.
        inputs: Artifacts consumed by the transform.
        cmd: Command to execute. Must be a single string if :code:`shell` is truthy and a sequence
            of strings otherwise.
        env: Mapping of environment variables.
        shell: Whether to execute the command through the shell, e.g. to expand the home directory
            :code:`~` or pipe information between processes or files using :code:`|`, :code:`<`, or
            :code:`>`. See :class:`subprocess.Popen` for details, including security considerations.
        **kwargs: Keyword arguments passed to :func:`asyncio.subprocess.create_subprocess_shell` (if
            :code:`shell == True`) or :func:`asyncio.subprocess.create_subprocess_exec` (if
            :code:`shell == False`).

    Raises:
        ValueError: If :code:`shell == True` and :code:`cmd` is not a string, or
            :code:`shell == False` and :code:`cmd` is not a list of strings.

    Attributes:
        ENV: Default mapping of environment variables for all :class:`Subprocess` transforms.

    Example:
        >>> bb.Subprocess("copy.txt", "input.txt", ["cp", "$<", "$@"])
        Subprocess([File(input.txt)] -> [File(copy.txt)])
    """
    def __init__(self, outputs: typing.Iterable["artifacts.Artifact"],
                 inputs: typing.Iterable["artifacts.Artifact"],
                 cmd: typing.Union[str, typing.Iterable[str]], *, env: dict[str, str] = None,
                 shell: bool = False, **kwargs) -> None:
        super().__init__(outputs, inputs)
        if shell and not isinstance(cmd, str):
            raise ValueError(f"`cmd` must be a string if `shell == True` but got {cmd}")
        if not shell and not isinstance(cmd, list):
            raise ValueError(f"`cmd` must be a list of strings if `shell == False` but got {cmd}")
        self.cmd = cmd
        self.shell = shell
        self.env = env or {}
        self.kwargs = kwargs

    def _apply_substitutions(self, part: str) -> str:
        part = part.format(outputs=self.outputs, inputs=self.inputs)
        # Apply Makefile-style and python interpreter substitutions.
        rules = {
            r"@": self.outputs[0],
            r"<": self.inputs[0] if self.inputs else None,
            r"\^": " ".join(input.name for input in self.inputs),
            r"!": sys.executable,
        }
        for key, value in rules.items():
            part = re.sub(r"(?<!\$)\$" + key, str(value), part)
        return part

    async def apply(self) -> None:
        # Prepare the command.
        if self.shell:
            pretty_cmd = cmd = self._apply_substitutions(self.cmd)
        else:
            cmd = [self._apply_substitutions(str(part)) for part in self.cmd]
            pretty_cmd = " ".join(map(shlex.quote, cmd))
        LOGGER.info("\u2699\ufe0f execute %s command `%s`", "shell" if self.shell else "subprocess",
                    pretty_cmd)
        # Call the process.
        env = os.environ | self.get_global_env() | self.env
        env = {key: str(value) for key, value in env.items() if value is not None}
        if self.shell:
            process = await asyncio.subprocess.create_subprocess_shell(cmd, env=env, **self.kwargs)
        else:
            process = await asyncio.subprocess.create_subprocess_exec(*cmd, env=env, **self.kwargs)
        status = await process.wait()
        if status:
            raise RuntimeError(f"{self} failed with status code {status}")

    @classmethod
    def get_global_env(cls) -> dict:
        """
        Get the global environment variables used by all :class:`Subprocess` transforms.
        """
        return cls.get_properties().get("ENV", {})

    @classmethod
    def set_global_env(cls, value: dict) -> None:
        """
        Set the global environment variables used by all :class:`Subprocess` transforms.
        """
        cls.get_properties()["ENV"] = value


class Shell(Subprocess):
    """
    Execute a command in the shell. See :class:`Subprocess` for details.

    Example:
    >>> Shell("output.txt", None, "echo hello > output.txt")
    Shell([] -> [File(output.txt)])
    """
    def __init__(self, outputs: typing.Iterable["artifacts.Artifact"],
                 inputs: typing.Iterable["artifacts.Artifact"],
                 cmd: str, *, env: dict[str, str] = None, **kwargs) -> None:
        super().__init__(outputs, inputs, cmd, env=env, shell=True, **kwargs)


class Functional(Transform):
    """
    Apply a python function.

    Args:
        outputs: Artifacts to generate.
        inputs: Artifacts consumed by the transform.
        func: Function to execute.
        *args: Positional arguments passed to :code:`func`.
        *kwargs: Keyword arguments passed to :code:`func`.
    """
    def __init__(self, outputs: typing.Iterable["artifacts.Artifact"], inputs:
                 typing.Iterable["artifacts.Artifact"], func: typing.Callable, *args, **kwargs) \
            -> None:
        super().__init__(outputs, inputs)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def apply(self) -> None:
        return self.func(self.outputs, self.inputs, *self.args, **self.kwargs)
