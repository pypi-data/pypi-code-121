import pytest

from auto_pytest_mg.mg_ast import MGAST

MODULE_PATH = "auto_pytest_mg.mg_ast"


@pytest.fixture
def mock_ast(mocker):
    mock_ast_ = mocker.patch(f"{MODULE_PATH}.ast")
    return mock_ast_


@pytest.fixture
def mock_itertools(mocker):
    mock_itertools_ = mocker.patch(f"{MODULE_PATH}.itertools")
    return mock_itertools_


@pytest.fixture
def mock_list(mocker):
    mock_list_ = mocker.patch(f"{MODULE_PATH}.List")
    return mock_list_


@pytest.fixture
def mock_dataclass(mocker):
    mock_dataclass_ = mocker.patch(f"{MODULE_PATH}.dataclass")
    return mock_dataclass_


@pytest.fixture
def mock_path(mocker):
    mock_path_ = mocker.patch(f"{MODULE_PATH}.Path")
    return mock_path_


@pytest.fixture
def mock_console(mocker):
    mock_console_ = mocker.patch(f"{MODULE_PATH}.console")
    return mock_console_


@pytest.fixture
def mock_mg_class(mocker):
    mock_mg_class_ = mocker.patch(f"{MODULE_PATH}.MGClass")
    return mock_mg_class_


@pytest.fixture
def mock_mg_function(mocker):
    mock_mg_function_ = mocker.patch(f"{MODULE_PATH}.MGFunction")
    return mock_mg_function_


@pytest.fixture
def mock_mg_import(mocker):
    mock_mg_import_ = mocker.patch(f"{MODULE_PATH}.MGImport")
    return mock_mg_import_


@pytest.fixture
def mock_mg_import_from(mocker):
    mock_mg_import_from_ = mocker.patch(f"{MODULE_PATH}.MGImportFrom")
    return mock_mg_import_from_


@pytest.fixture
def mgast(mocker):
    file_path = mocker.MagicMock()
    imports = mocker.MagicMock()
    classes = mocker.MagicMock()
    imports_from = mocker.MagicMock()
    functions = mocker.MagicMock()
    return MGAST(
        file_path=file_path,
        imports=imports,
        classes=classes,
        imports_from=imports_from,
        functions=functions,
    )


class TestMGAST:
    def test__init__(self, mocker):
        file_path = mocker.MagicMock()
        imports = mocker.MagicMock()
        classes = mocker.MagicMock()
        imports_from = mocker.MagicMock()
        functions = mocker.MagicMock()

        mgast_ = MGAST(
            file_path=file_path,
            imports=imports,
            classes=classes,
            imports_from=imports_from,
            functions=functions,
        )

    def test_from_file(self, mocker, mg, mgast):
        file_path = mocker.MagicMock()
        mg.generate_uut_mocks_with_asserts(mgast.from_file)

        result = mgast.from_file(file_path=file_path)

    def test_write_mg_test_file(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.write_mg_test_file)

        result = mgast.write_mg_test_file()

    def test_mg_test_file_path(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.mg_test_file_path)

        result = mgast.mg_test_file_path

    def test_dotted_module_path(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.dotted_module_path)

        result = mgast.dotted_module_path

    def test_mg_test_file_text(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.mg_test_file_text)

        result = mgast.mg_test_file_text

    def test_import_lines_text(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.import_lines_text)

        result = mgast.import_lines_text

    def test_import_fixtures(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.import_fixtures)

        result = mgast.import_fixtures

    def test_import_from_fixtures(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.import_from_fixtures)

        result = mgast.import_from_fixtures

    def test_class_fixtures(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.class_fixtures)

        result = mgast.class_fixtures

    def test_class_tests(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.class_tests)

        result = mgast.class_tests

    def test_function_tests(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.function_tests)

        result = mgast.function_tests

    def test_module_path_constant(self, mocker, mg, mgast):
        mg.generate_uut_mocks_with_asserts(mgast.module_path_constant)

        result = mgast.module_path_constant
