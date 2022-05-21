from offer_service.main import app, OFFERS_URL
from fastapi.testclient import TestClient
from mock import patch
import json

class TestDB:
    
    def connect(self):
        return self
    def execute(self, sql, params):
        return []
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, tb):
        pass
    
client = TestClient(app)
testDB = TestDB()

@patch('offer_service.main.db', testDB)
def test_create_offer_missing_position():
    data = {
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'position'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

@patch('offer_service.main.db', testDB)
def test_create_offer_null_position():
    data = {
        'position': None,
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'position'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

@patch('offer_service.main.db', testDB)
def test_create_offer_empty_position():
    data = {
        'position': '',
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'position'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

@patch('offer_service.main.db', testDB)
def test_create_offer_missing_requirements():
    data = {
        'position': 'asd',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'requirements'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

@patch('offer_service.main.db', testDB)
def test_create_offer_null_requirements():
    data = {
        'position': 'asd',
        'requirements': None,
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'requirements'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

@patch('offer_service.main.db', testDB)
def test_create_offer_empty_requirements():
    data = {
        'position': 'asd',
        'requirements': '',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'requirements'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

@patch('offer_service.main.db', testDB)
def test_create_offer_missing_description():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'description'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

@patch('offer_service.main.db', testDB)
def test_create_offer_null_description():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'description': None,
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'description'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

@patch('offer_service.main.db', testDB)
def test_create_offer_empty_description():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'description': '',
        'agent_application_link': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'description'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

@patch('offer_service.main.db', testDB)
def test_create_offer_missing_agent_application_link():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'description': 'asd'
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'agent_application_link'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

@patch('offer_service.main.db', testDB)
def test_create_offer_null_agent_application_link():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': None
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'agent_application_link'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

@patch('offer_service.main.db', testDB)
def test_create_offer_empty_agent_application_link():
    data = {
        'position': 'asd',
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': ''
    }
    res = client.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'agent_application_link'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

@patch('offer_service.main.db', testDB)
def test_create_offer_valid():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        data = {
            'position': 'position 1',
            'requirements': 'requirements 1',
            'description': 'description 1',
            'agent_application_link': 'agent_application_link 1'
        }
        res = client.post(OFFERS_URL, json=data)
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body is None
        spy.assert_called_once()
        spy.assert_called_once_with(' '.join('''
            insert into offers (date, position, requirements, description, agent_application_link)
            values (current_timestamp, %s, %s, %s, %s)
        '''.split()), ('position 1', 'requirements 1', 'description 1', 'agent_application_link 1'))

