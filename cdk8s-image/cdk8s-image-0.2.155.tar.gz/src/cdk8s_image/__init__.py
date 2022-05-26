'''
# cdk8s-image

An `Image` construct which takes care of building & pushing docker images that
can be used in [CDK8s](https://github.com/awslabs/cdk8s) apps.

The following example will build the docker image from `Dockerfile` under the
`my-app` directory, push it to a local registry and then define a Kubernetes
deployment that deploys containers that run this image.

```python
const image = new Image(this, 'image', {
  dir: `${__dirname}/my-app`,
  registry: 'localhost:5000'
});

new Deployment(this, 'deployment', {
  containers: [ new Container({ image: image.url }) ],
});
```

## Contributions

All contributions are celebrated.

## License

Licensed under [Apache 2.0](./LICENSE).
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import constructs


@jsii.data_type(
    jsii_type="cdk8s-image.BuildArg",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class BuildArg:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''Build arg to pass to the docker build.

        :param name: the name of the build arg.
        :param value: the value of the build arg.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''the name of the build arg.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''the value of the build arg.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildArg(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Image(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-image.Image",
):
    '''Represents a docker image built during synthesis from a context directory (``dir``) with a ``Dockerfile``.

    The image will be built using ``docker build`` and then pushed through ``docker push``. The URL of the pushed image can be accessed through ``image.url``.

    If you push to a registry other then docker hub, you can specify the registry
    URL through the ``registry`` option.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dir: builtins.str,
        build_args: typing.Optional[typing.Sequence[BuildArg]] = None,
        file: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dir: The docker build context directory (where ``Dockerfile`` is).
        :param build_args: List of build args to pass to the build action.
        :param file: Path to Dockerfile.
        :param platform: Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
        :param registry: The registry URL to use. This will be used as the prefix for the image name. For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``. Default: "docker.io/library"
        '''
        props = ImageProps(
            dir=dir,
            build_args=build_args,
            file=file,
            platform=platform,
            registry=registry,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''The image URL to use in order to pull this instance of the image.'''
        return typing.cast(builtins.str, jsii.get(self, "url"))


@jsii.data_type(
    jsii_type="cdk8s-image.ImageProps",
    jsii_struct_bases=[],
    name_mapping={
        "dir": "dir",
        "build_args": "buildArgs",
        "file": "file",
        "platform": "platform",
        "registry": "registry",
    },
)
class ImageProps:
    def __init__(
        self,
        *,
        dir: builtins.str,
        build_args: typing.Optional[typing.Sequence[BuildArg]] = None,
        file: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Props for ``Image``.

        :param dir: The docker build context directory (where ``Dockerfile`` is).
        :param build_args: List of build args to pass to the build action.
        :param file: Path to Dockerfile.
        :param platform: Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
        :param registry: The registry URL to use. This will be used as the prefix for the image name. For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``. Default: "docker.io/library"
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dir": dir,
        }
        if build_args is not None:
            self._values["build_args"] = build_args
        if file is not None:
            self._values["file"] = file
        if platform is not None:
            self._values["platform"] = platform
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def dir(self) -> builtins.str:
        '''The docker build context directory (where ``Dockerfile`` is).'''
        result = self._values.get("dir")
        assert result is not None, "Required property 'dir' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.List[BuildArg]]:
        '''List of build args to pass to the build action.'''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.List[BuildArg]], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''Path to Dockerfile.'''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Set to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).'''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''The registry URL to use.

        This will be used as the prefix for the image name.

        For example, if you have a local registry listening on port 500, you can set this to ``localhost:5000``.

        :default: "docker.io/library"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BuildArg",
    "Image",
    "ImageProps",
]

publication.publish()
