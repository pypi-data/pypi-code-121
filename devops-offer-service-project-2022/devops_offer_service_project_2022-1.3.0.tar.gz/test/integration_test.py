from sqlalchemy import create_engine
import requests
import json

db = create_engine('postgresql://postgres:postgres@localhost:5435/postgres')
OFFERS_URL = 'http://localhost:8002/api/offers'

def test_create_offer_missing_position():
    data = {
        'requirements': 'asd',
        'description': 'asd',
        'agent_application_link': 'asd'
    }
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
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
    res = requests.post(OFFERS_URL, json=data)
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'agent_application_link'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1


def reset_table(number_of_rows=0):
    with db.connect() as connection:
        connection.execute('delete from offers')
        for i in range(number_of_rows):
            connection.execute(' '.join('''
                insert into offers (date, position, requirements, description, agent_application_link)
                values (current_timestamp, %s, %s, %s, %s)
            '''.split()), (f'position {i+1}', f'requirements {i+1}', f'description {i+1}', f'agent_application_link {i+1}'))


def test_create_offer_valid():
    reset_table()
    data = {
        'position': 'position 1',
        'requirements': 'requirements 1',
        'description': 'description 1',
        'agent_application_link': 'agent_application_link 1'
    }
    res = requests.post(OFFERS_URL, json=data)
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body is None
    with db.connect() as connection:
        offers = list(connection.execute('select * from offers'))
    assert len(offers) == 1
    assert offers[0]['position'] == 'position 1'
    assert offers[0]['requirements'] == 'requirements 1'
    assert offers[0]['description'] == 'description 1'
    assert offers[0]['agent_application_link'] == 'agent_application_link 1'

def test_read_offers():
    reset_table(10)
    res = requests.get(OFFERS_URL)
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/offers?search=&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    assert len(body['results']) == 7
    for i in range(7):
        assert body['results'][i]['position'] == f'position {10-i}'
        assert body['results'][i]['requirements'] == f'requirements {10-i}'
        assert body['results'][i]['description'] == f'description {10-i}'
        assert body['results'][i]['agent_application_link'] == f'agent_application_link {10-i}'

def test_read_offers_with_offset():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?offset=7')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] == '/offers?search=&offset=0&limit=7'
    assert body['links']['next'] is None
    assert body['offset'] == 7
    assert body['limit'] == 7
    assert body['size'] == 3
    assert len(body['results']) == 3
    
def test_read_offers_with_limit():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?limit=10')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 10
    assert body['size'] == 10
    assert len(body['results']) == 10
    for i in range(10):
        assert body['results'][i]['position'] == f'position {10-i}'
        assert body['results'][i]['requirements'] == f'requirements {10-i}'
        assert body['results'][i]['description'] == f'description {10-i}'
        assert body['results'][i]['agent_application_link'] == f'agent_application_link {10-i}'

def test_search_offers_by_position():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?search=POSITION')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/offers?search=POSITION&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    assert len(body['results']) == 7
    for i in range(7):
        assert body['results'][i]['position'] == f'position {10-i}'
        assert body['results'][i]['requirements'] == f'requirements {10-i}'
        assert body['results'][i]['description'] == f'description {10-i}'
        assert body['results'][i]['agent_application_link'] == f'agent_application_link {10-i}'

def test_search_offers_by_requirements():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?search=REQUIREMENTS')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/offers?search=REQUIREMENTS&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    assert len(body['results']) == 7
    for i in range(7):
        assert body['results'][i]['position'] == f'position {10-i}'
        assert body['results'][i]['requirements'] == f'requirements {10-i}'
        assert body['results'][i]['description'] == f'description {10-i}'
        assert body['results'][i]['agent_application_link'] == f'agent_application_link {10-i}'

def test_search_offers_by_description():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?search=DESCRIPTION')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/offers?search=DESCRIPTION&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    assert len(body['results']) == 7
    for i in range(7):
        assert body['results'][i]['position'] == f'position {10-i}'
        assert body['results'][i]['requirements'] == f'requirements {10-i}'
        assert body['results'][i]['description'] == f'description {10-i}'
        assert body['results'][i]['agent_application_link'] == f'agent_application_link {10-i}'

def test_search_offer_by_agent_application_link():
    reset_table(10)
    res = requests.get(f'{OFFERS_URL}?search=AGENT_APPLICATION_LINK')
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 0
    assert len(body['results']) == 0
