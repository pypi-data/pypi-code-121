from os.path import dirname, join
from typing import Iterable, List

from sila2.code_generator.code_generator_base import CodeGeneratorBase
from sila2.code_generator.feature_generator import FeatureGenerator
from sila2.features.authenticationservice import AuthenticationServiceFeature
from sila2.features.authorizationproviderservice import AuthorizationProviderServiceFeature
from sila2.features.authorizationservice import AuthorizationServiceFeature
from sila2.features.lockcontroller import LockControllerFeature
from sila2.framework import Feature
from sila2.server import default_feature_implementations


class CodeGenerator(CodeGeneratorBase):
    def generate_package(
        self,
        package_name: str,
        features: List[Feature],
        out_dir: str,
        *,
        generate_main: bool = False,
        lock_controller: bool = False,
        auth_features: bool = False,
        for_git_repo: bool = False,
    ) -> None:
        if not package_name.isidentifier():
            raise ValueError(f"Package name must be a valid Python identifier, was {package_name!r}")

        # remove duplicate features
        if lock_controller:
            features = [
                f for f in features if f.fully_qualified_identifier != LockControllerFeature.fully_qualified_identifier
            ]
        if auth_features:
            features = [
                f
                for f in features
                if f.fully_qualified_identifier
                not in (
                    AuthenticationServiceFeature.fully_qualified_identifier,
                    AuthorizationProviderServiceFeature.fully_qualified_identifier,
                    AuthorizationServiceFeature.fully_qualified_identifier,
                )
            ]

        # generate directories early to fail fast if they exist and overwriting is not permitted
        package_dir = join(out_dir, package_name)
        generated_dir = join(package_dir, "generated")
        implementations_dir = join(package_dir, "feature_implementations")

        self.generate_directory(out_dir, allow_overwrite=True)
        self.generate_directory(package_dir)
        self.generate_directory(generated_dir)
        self.generate_directory(implementations_dir)

        # generate setup files
        self._generate_pyproject_toml(package_name, generate_main, out_dir)
        self._generate_setup_py(out_dir)

        # generate git repo files
        if for_git_repo:
            self.generate_file(
                join(out_dir, ".gitignore"), self.template_env.get_template("package/gitignore").render()
            )
            self.generate_file(
                join(out_dir, "README.md"),
                self.template_env.get_template("package/readme").render(package_name=package_name),
            )

        # generate package files
        if generate_main:
            self._generate_main(package_dir)
        self._generate_package_init(package_dir)
        self._generate_server(features, package_dir, lock_controller=lock_controller, auth_features=auth_features)
        self.generate_file(join(package_dir, "py.typed"), content="", allow_overwrite=True)

        # generate 'generated/'
        features_to_generate = features.copy()
        if lock_controller:
            features_to_generate.append(LockControllerFeature)
        if auth_features:
            features_to_generate.append(AuthenticationServiceFeature)
            features_to_generate.append(AuthorizationServiceFeature)
            features_to_generate.append(AuthorizationProviderServiceFeature)
        self.generate_generated_dir(features_to_generate, generated_dir)

        # generate 'feature_implementations/'
        self.generate_implementations(features, implementations_dir)
        if lock_controller:
            self.copy_default_implementation(LockControllerFeature, implementations_dir)
        if auth_features:
            self.copy_default_implementation(AuthenticationServiceFeature, implementations_dir)
            self.copy_default_implementation(AuthorizationServiceFeature, implementations_dir)
            self.copy_default_implementation(AuthorizationProviderServiceFeature, implementations_dir)
        self.generate_file(join(implementations_dir, "__init__.py"), "")

    def copy_default_implementation(self, feature: Feature, out_dir: str) -> None:
        feature_identifier = feature._identifier
        file_content = open(
            join(dirname(default_feature_implementations.__file__), f"{feature_identifier.lower()}_impl.py")
        ).read()
        file_content.replace(
            f"from sila2.features.{feature_identifier.lower()} import ",
            f"from ..generated.{feature_identifier.lower()} import",
        )
        self.generate_file(join(out_dir, f"{feature_identifier.lower()}_impl.py"), file_content)

    def generate_generated_dir(self, features: List[Feature], out_dir: str) -> None:
        self._generate_generated_init(out_dir)
        self._generate_client(features, out_dir)

        for feature in features:
            feature_dir = join(out_dir, feature._identifier.lower())
            self.generate_directory(feature_dir, allow_overwrite=True)
            feature_generator = FeatureGenerator(feature, overwrite=self.overwrite)
            feature_generator.generate_feature_files(feature_dir)
            self.generated_files.extend(feature_generator.generated_files)

    def generate_implementations(self, features: List[Feature], out_dir: str, *, prefix: str = "") -> None:
        for feature in features:
            feature_generator = FeatureGenerator(feature, overwrite=self.overwrite)
            feature_generator.generate_impl(out_dir, prefix=prefix)
            self.generated_files.extend(feature_generator.generated_files)

    def _generate_pyproject_toml(self, package_name: str, generate_main: bool, out_dir: str) -> None:
        self.generate_file(
            join(out_dir, "pyproject.toml"),
            self.template_env.get_template("package/pyproject_toml").render(
                package_name=package_name, generate_main=generate_main
            ),
        )

    def _generate_main(self, out_dir: str) -> None:
        self.generate_file(
            join(out_dir, "__main__.py"),
            self.template_env.get_template("package/main").render(),
        )

    def _generate_setup_py(self, out_dir: str) -> None:
        self.generate_file(join(out_dir, "setup.py"), self.template_env.get_template("package/setup_py").render())

    def _generate_package_init(self, out_dir: str) -> None:
        self.generate_file(join(out_dir, "__init__.py"), self.template_env.get_template("package/init").render())

    def _generate_server(
        self, features: List[Feature], out_dir: str, *, lock_controller: bool = False, auth_features: bool = False
    ) -> None:
        self.generate_file(
            join(out_dir, "server.py"),
            self.template_env.get_template("package/server").render(
                features=features,
                lock_controller=lock_controller,
                auth_features=auth_features,
            ),
        )

    def _generate_generated_init(self, out_dir: str) -> None:
        self.generate_file(
            join(out_dir, "__init__.py"), 'from .client import Client\n__all__ = ["Client"]', allow_overwrite=True
        )

    def _generate_client(self, features: Iterable[Feature], out_dir: str) -> None:
        self.generate_file(
            join(out_dir, "client.py"),
            self.template_env.get_template("package/client").render(features=tuple(features)),
        )
