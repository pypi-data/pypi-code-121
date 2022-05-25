from unittest.mock import patch, MagicMock

from hestia_earth.extend_bibliography.bibliography_apis.wos import extend_wos

wos_dir = 'hestia_earth.extend_bibliography.bibliography_apis.wos'


def fake_search(**kwargs):
    def search(*args):
        return [{'title': 'title', 'item': {}}]
    return search


def fake_create_biblio(**kwargs):
    return ({}, [])


def get_client(**kwargs):
    mock = MagicMock()
    mock.__enter__.return_value = 'client'
    return mock


@patch(wos_dir + '.wos_rest_client.create_biblio', return_value=fake_create_biblio())
@patch(wos_dir + '.wos_rest_client.exec_search', return_value=fake_search())
@patch(wos_dir + '.wos_rest_client.get_client', side_effect=get_client)
def test_extend_wos_rest(mock_get_client, mock_search, *args):
    extend_wos(['title'], wos_api_key='wos_api_key')
    mock_get_client.assert_called_once()
    mock_search.assert_called_once()


@patch(wos_dir + '.wos_soap_client.create_biblio', return_value=fake_create_biblio())
@patch(wos_dir + '.wos_soap_client.exec_search', return_value=fake_search())
@patch(wos_dir + '.wos_soap_client.get_client', side_effect=get_client)
def test_extend_wos_soap(mock_get_client, mock_search, *args):
    extend_wos(['title'], wos_api_user='wos_api_user', wos_api_pwd='wos_api_pwd')
    mock_get_client.assert_called_once()
    mock_search.assert_called_once()


@patch(wos_dir + '.wos_soap_client.get_client', return_value=())
def test_extend_wos_exception(*args):
    assert extend_wos(['title']) == ([], [])
