from unittest.mock import patch, MagicMock

from hestia_earth.extend_bibliography.bibliography_apis.mendeley import get_client, extend_mendeley

mendeley_dir = 'hestia_earth.extend_bibliography.bibliography_apis.mendeley'


def fake_search(**kwargs):
    def search(*args):
        return [{'title': 'title', 'item': {}}]
    return search


def fake_create_biblio(**kwargs):
    return ({}, [])


def fake_get_client(**kwargs):
    mock = MagicMock()
    mock.__enter__.return_value = mock
    return mock


@patch(mendeley_dir + '.mendeley_sdk_client.get_client', side_effect=fake_get_client)
@patch(mendeley_dir + '.mendeley_api_client.get_client', side_effect=fake_get_client)
def test_get_client(mock_api_client, mock_sdk_client):
    get_client(10)
    mock_sdk_client.assert_called_once()
    mock_api_client.assert_not_called()

    mock_sdk_client.reset_mock()
    mock_api_client.reset_mock()

    get_client(10, mendeley_api_url='mendeley_api_url')
    mock_sdk_client.assert_not_called()
    mock_api_client.assert_called_once()

    mock_sdk_client.reset_mock()
    mock_api_client.reset_mock()

    get_client(100)
    mock_sdk_client.assert_called_once()
    mock_api_client.assert_not_called()

    mock_sdk_client.reset_mock()
    mock_api_client.reset_mock()

    get_client(100, mendeley_api_url='mendeley_api_url')
    mock_sdk_client.assert_called_once()
    mock_api_client.assert_not_called()


@patch(mendeley_dir + '.mendeley_sdk_client.create_biblio', return_value=fake_create_biblio())
@patch(mendeley_dir + '.mendeley_sdk_client.exec_search', return_value=fake_search())
@patch(mendeley_dir + '.mendeley_sdk_client.get_client', side_effect=fake_get_client)
def test_extend_mendeley_sdk(mock_get_client, mock_search, *args):
    (functions, client) = get_client(1)
    extend_mendeley(functions, client, ['title'], 'title')
    mock_get_client.assert_called_once()
    mock_search.assert_called_once()


@patch(mendeley_dir + '.mendeley_api_client.create_biblio', return_value=fake_create_biblio())
@patch(mendeley_dir + '.mendeley_api_client.exec_search', return_value=fake_search())
@patch(mendeley_dir + '.mendeley_api_client.get_client', side_effect=fake_get_client)
def test_extend_mendeley_api(mock_get_client, mock_search, *args):
    (functions, client) = get_client(1, mendeley_api_url='mendeley_api_url')
    extend_mendeley(functions, client, ['title'], 'title')
    mock_get_client.assert_called_once()
    mock_search.assert_called_once()


@patch(mendeley_dir + '.mendeley_api_client.get_client', return_value=())
def test_extend_mendeley_exception(*args):
    (functions, client) = get_client(1, mendeley_api_url='mendeley_api_url')
    assert extend_mendeley(functions, client, ['title'], 'title') == ([], [])
