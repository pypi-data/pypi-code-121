from offer_service.main import app, OFFERS_URL
from fastapi.testclient import TestClient
from mock import patch
import json

class TestDB:
    def execute(self, sql, params):
        return []
    
class TestKP:
    def send(self, topic, data):
        pass

client = TestClient(app)
testDB = TestDB()
testKP = TestKP()

def fix_whitespaces(text: str):
    return ' '.join(text.split())

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
@patch('offer_service.main.kafka_producer', testKP)
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
        spy.assert_called_once_with('insert into offers (position, requirements, description, agent_application_link) values (%s, %s, %s, %s)', ('position 1', 'requirements 1', 'description 1', 'agent_application_link 1'))

@patch('offer_service.main.db', testDB)
def test_read_offers():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(OFFERS_URL)
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 7
        '''), ('%%', '%%', '%%'))

@patch('offer_service.main.db', testDB)
def test_read_offers_with_offset():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?offset=7')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] == '/offers?search=&offset=0&limit=7'
        assert body['links']['next'] is None
        assert body['offset'] == 7
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 7 limit 7
        '''), ('%%', '%%', '%%'))

@patch('offer_service.main.db', testDB)
def test_read_offers_with_limit():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?limit=10')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 10
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 10
        '''), ('%%', '%%', '%%'))

@patch('offer_service.main.db', testDB)
def test_search_offers_by_position():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?search=POSITION')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 7
        '''), ('%position%', '%position%', '%position%'))

@patch('offer_service.main.db', testDB)
def test_search_offers_by_requirements():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?search=REQUIREMENTS')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 7
        '''), ('%requirements%', '%requirements%', '%requirements%'))

@patch('offer_service.main.db', testDB)
def test_search_offers_by_description():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?search=DESCRIPTION')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 7
        '''), ('%description%', '%description%', '%description%'))

@patch('offer_service.main.db', testDB)
def test_search_offer_by_agent_application_link():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as spy:        
        res = client.get(f'{OFFERS_URL}?search=AGENT_APPLICATION_LINK')
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body['links']['prev'] is None
        assert body['links']['next'] is None
        assert body['offset'] == 0
        assert body['limit'] == 7
        assert body['size'] == 0
        assert len(body['results']) == 0
        spy.assert_called()
        spy.assert_called_with(fix_whitespaces('''
            select * from offers
            where lower(position) like %s or lower(requirements) like %s or lower(description) like %s
            order by id desc offset 0 limit 7
        '''), ('%agent_application_link%', '%agent_application_link%', '%agent_application_link%'))
