from profile_service.main import JWT_SECRET, JWT_ALGORITHM
from sqlalchemy import create_engine
from kafka import KafkaProducer

import pytest
import requests
import json
import time
import jwt
import datetime

PROFILES_URL = 'http://localhost:8001/api/profiles'
PROFILE_URL = 'http://localhost:8001/api/profile'
NOTIFICATIONS_URL = 'http://localhost:8001/api/notifications'
db = create_engine('postgresql://postgres:postgres@localhost:5434/postgres')
kafka_producer = None

@pytest.fixture(scope='session', autouse=True)
def do_something(request):
    time.sleep(30)
    global kafka_producer
    kafka_producer = KafkaProducer(bootstrap_servers='localhost:29092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    

def reset_table(number_of_rows=0):
    with db.connect() as connection:
        connection.execute('delete from profiles')
        for i in range(number_of_rows):
            connection.execute(f'''
                insert into profiles (id, first_name, last_name, email, phone_number, sex, birth_date, username, biography, private)
                values ({i+1}, 'first_name {i+1}', 'last_name {i+1}', 'email {i+1}', 'phone_number {i+1}', 
                'sex {i+1}', current_date, 'username {i+1}', 'biography {i+1}', {'true' if i%2==0 else 'false'})
            ''')

def reset_notifications_table(number_of_rows=0):
    with db.connect() as connection:
        connection.execute('delete from notifications')
        for i in range(number_of_rows):
            connection.execute(f"insert into notifications (recipient_id, message) values ({i}, 'message {i+1}')")

def reset_user():
    with db.connect() as connection:
        connection.execute(f'''
            insert into profiles (id, first_name, last_name, email, phone_number, sex, birth_date, username, biography, private, connections, connection_requests, blocked_profiles)
            values (0, 'asd', 'asd', 'asd', 'asd', 'asd', current_date, 'asd', 'asd', true, '[1, 3, 5, 7, 8]', '[2, 4, 6]', '[9, 10]')
        ''')

def generate_auth():
    return {'Authorization': jwt.encode({'id': 0}, JWT_SECRET, algorithm=JWT_ALGORITHM)}

def check_profiles(profiles: list, limit=7, offset_check=lambda x: x+1):
    assert len(profiles) == limit
    for i in range(limit):
        assert profiles[i]['id'] == offset_check(i)

        assert profiles[i]['first_name'] == f'first_name {offset_check(i)}'
        assert profiles[i]['last_name'] == f'last_name {offset_check(i)}'
        assert profiles[i]['email'] == f'email {offset_check(i)}'
        assert profiles[i]['phone_number'] == f'phone_number {offset_check(i)}'
        assert profiles[i]['sex'] == f'sex {offset_check(i)}'
        assert profiles[i]['username'] == f'username {offset_check(i)}'
        assert profiles[i]['biography'] == f'biography {offset_check(i)}'
        assert profiles[i]['private'] == (offset_check(i) % 2 != 0)
        
        assert profiles[i]['work_experiences'] == []
        assert profiles[i]['educations'] == []
        assert profiles[i]['skills'] == []
        assert profiles[i]['interests'] == []
        assert profiles[i]['connections'] == []
        assert profiles[i]['connection_requests'] == []
        assert profiles[i]['blocked_profiles'] == []
        
        assert not profiles[i]['block_post_notifications']
        assert not profiles[i]['block_message_notifications']

def test_read_profiles():
    reset_table(10)
    reset_user()
    res = requests.get(PROFILES_URL, headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])
        
def test_read_profiles_with_offset():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?offset=7', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] == '/profiles?search=&offset=0&limit=7'
    assert body['links']['next'] is None
    assert body['offset'] == 7
    assert body['limit'] == 7
    assert body['size'] == 3
    check_profiles(body['results'], 3, lambda x: 8+x)

def test_read_profiles_with_limit():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?limit=10', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 10
    assert body['size'] == 10
    check_profiles(body['results'], 10)

def test_search_profiles_by_first_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=FIRST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=FIRST_NAME&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_last_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=LAST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=LAST_NAME&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_email():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=EMAIL', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=EMAIL&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_phone_number():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=PHONE_NUMBER', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=PHONE_NUMBER&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_sex():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=SEX', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=SEX&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_username():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=USERNAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=USERNAME&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def test_search_profiles_by_biography():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}?search=BIOGRAPHY', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] == '/profiles?search=BIOGRAPHY&offset=7&limit=7'
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 7
    check_profiles(body['results'])

def check_public_profiles(profiles: list):
    assert len(profiles) == 5
    for i in range(len(profiles)):
        assert not profiles[i]['private']
        assert profiles[i]['id'] == (i+1) * 2

def test_read_public_profiles():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])
        
def test_read_public_profiles_with_offset():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?offset=7', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] == '/profiles/public?search=&offset=0&limit=7'
    assert body['links']['next'] is None
    assert body['offset'] == 7
    assert body['limit'] == 7
    assert body['size'] == 0
    assert len(body['results']) == 0

def test_read_public_profiles_with_limit():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?limit=10', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 10
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_first_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=FIRST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_last_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=LAST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_email():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=EMAIL', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_phone_number():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=PHONE_NUMBER', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_sex():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=SEX', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_username():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=USERNAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def test_search_public_profiles_by_biography():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/public?search=BIOGRAPHY', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_public_profiles(body['results'])

def check_connections(profiles: list):
    assert len(profiles) == 5
    assert profiles[0]['id'] == 1
    assert profiles[1]['id'] == 3
    assert profiles[2]['id'] == 5
    assert profiles[3]['id'] == 7
    assert profiles[4]['id'] == 8

def test_read_connections():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_read_connections_with_offset():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?offset=7', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] == '/profiles/connections?search=&offset=0&limit=7'
    assert body['links']['next'] is None
    assert body['offset'] == 7
    assert body['limit'] == 7
    assert body['size'] == 0
    assert len(body['results']) == 0

def test_read_connections_with_limit():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?limit=10', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 10
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_first_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=FIRST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_last_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=LAST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_email():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=EMAIL', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_phone_number():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=PHONE_NUMBER', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_sex():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=SEX', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_username():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=USERNAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def test_search_connections_by_biography():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connections?search=BIOGRAPHY', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 5
    check_connections(body['results'])

def check_connection_requests(profiles: list):
    assert len(profiles) == 3
    assert profiles[0]['id'] == 2
    assert profiles[1]['id'] == 4
    assert profiles[2]['id'] == 6

def test_read_connection_requests():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_read_connection_requests_with_offset():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?offset=7', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] == '/profiles/connection_requests?search=&offset=0&limit=7'
    assert body['links']['next'] is None
    assert body['offset'] == 7
    assert body['limit'] == 7
    assert body['size'] == 0
    assert len(body['results']) == 0

def test_read_connection_requests_with_limit():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?limit=10', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 10
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_first_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=FIRST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_last_name():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=LAST_NAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_email():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=EMAIL', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_phone_number():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=PHONE_NUMBER', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_sex():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=SEX', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_username():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=USERNAME', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_search_connection_requests_by_biography():
    reset_table(10)
    reset_user()
    res = requests.get(f'{PROFILES_URL}/connection_requests?search=BIOGRAPHY', headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['links']['prev'] is None
    assert body['links']['next'] is None
    assert body['offset'] == 0
    assert body['limit'] == 7
    assert body['size'] == 3
    check_connection_requests(body['results'])

def test_read_profile():
    reset_table()
    reset_user()
    res = requests.get(PROFILE_URL, headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body['id'] == 0
    assert body['first_name'] == 'asd'
    assert body['last_name'] == 'asd'
    assert body['email'] == 'asd'
    assert body['phone_number'] == 'asd'
    assert body['sex'] == 'asd'
    assert body['username'] == 'asd'
    assert body['biography'] == 'asd'
    assert body['private']
    assert body['work_experiences'] == []
    assert body['educations'] == []
    assert body['skills'] == []
    assert body['interests'] == []
    assert body['connections'] == [1, 3, 5, 7, 8]
    assert body['connection_requests'] == [2, 4, 6]
    assert body['blocked_profiles'] == [9, 10]
    assert not body['block_post_notifications']
    assert not body['block_message_notifications']
    
def test_update_profile_missing_first_name():
    data = {
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'first_name'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_first_name():
    data = {
        'first_name': None,
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'first_name'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_first_name():
    data = {
        'first_name': '',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'first_name'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

def test_update_profile_missing_last_name():
    data = {
        'first_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'last_name'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_last_name():
    data = {
        'first_name': 'asd',
        'last_name': None,
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'last_name'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_last_name():
    data = {
        'first_name': 'asd',
        'last_name': '',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'last_name'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1

def test_update_profile_missing_email():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'email'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_email():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': None,
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'email'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_email():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': '',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'email'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1


def test_update_profile_missing_phone_number():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'phone_number'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_phone_number():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': None,
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'phone_number'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_phone_number():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': '',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'phone_number'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1
    
    
def test_update_profile_missing_sex():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'sex'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_sex():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': None,
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'sex'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_sex():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': '',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'sex'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1
    
def test_update_profile_missing_birth_date():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'birth_date'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_birth_date():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': None,
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'birth_date'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_birth_date():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '',
        'username': 'asd',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'birth_date'
    assert body['detail'][0]['msg'] == 'invalid date format'
    assert body['detail'][0]['type'] == 'value_error.date'


def test_update_profile_missing_username():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'username'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_username():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': None,
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'username'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_username():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': '',
        'biography': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'username'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1


def test_update_profile_missing_biography():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'biography'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_biography():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': None,
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'biography'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_biography():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': '',
        'private': True
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'biography'
    assert body['detail'][0]['msg'] == 'ensure this value has at least 1 characters'
    assert body['detail'][0]['type'] == 'value_error.any_str.min_length'
    assert body['detail'][0]['ctx']['limit_value'] == 1


def test_update_profile_missing_private():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd'
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'private'
    assert body['detail'][0]['msg'] == 'field required'
    assert body['detail'][0]['type'] == 'value_error.missing'

def test_update_profile_null_private():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': None
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'private'
    assert body['detail'][0]['msg'] == 'none is not an allowed value'
    assert body['detail'][0]['type'] == 'type_error.none.not_allowed'

def test_update_profile_empty_private():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': ''
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'private'
    assert body['detail'][0]['msg'] == 'value could not be parsed to a boolean'
    assert body['detail'][0]['type'] == 'type_error.bool'

def test_update_profile_empty_work_experiences():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True,
        'work_experiences': ''
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'work_experiences'
    assert body['detail'][0]['msg'] == 'value is not a valid list'
    assert body['detail'][0]['type'] == 'type_error.list'

def test_update_profile_empty_educations():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True,
        'educations': ''
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'educations'
    assert body['detail'][0]['msg'] == 'value is not a valid list'
    assert body['detail'][0]['type'] == 'type_error.list'

def test_update_profile_empty_skills():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True,
        'skills': ''
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'skills'
    assert body['detail'][0]['msg'] == 'value is not a valid list'
    assert body['detail'][0]['type'] == 'type_error.list'

def test_update_profile_empty_interests():
    data = {
        'first_name': 'asd',
        'last_name': 'asd',
        'email': 'asd',
        'phone_number': 'asd',
        'sex': 'asd',
        'birth_date': '2012-12-12',
        'username': 'asd',
        'biography': 'asd',
        'private': True,
        'interests': ''
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'interests'
    assert body['detail'][0]['msg'] == 'value is not a valid list'
    assert body['detail'][0]['type'] == 'type_error.list'

def test_update_profile_valid():
    reset_table()
    reset_user()
    data = {
        'first_name': 'qwe',
        'last_name': 'qwe',
        'email': 'qwe',
        'phone_number': 'qwe',
        'sex': 'qwe',
        'birth_date': '2012-12-12',
        'username': 'qwe',
        'biography': 'qwe',
        'private': False,
        'educations': None,
        'skills': [],
        'interests': [{'name': 'interest 1'}]
    }
    res = requests.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 200
    body = json.loads(res.text)
    assert body is None

    with db.connect() as connection:
        user = list(connection.execute('select * from profiles where id=0'))[0]    
    assert user['id'] == 0
    assert user['first_name'] == 'qwe'
    assert user['last_name'] == 'qwe'
    assert user['email'] == 'qwe'
    assert user['phone_number'] == 'qwe'
    assert user['sex'] == 'qwe'
    assert user['username'] == 'qwe'
    assert user['biography'] == 'qwe'
    assert not user['private']
    assert user['work_experiences'] == []
    assert user['educations'] == []
    assert user['skills'] == []
    assert user['interests'] == [{'name': 'interest 1'}]
    assert user['connections'] == [1, 3, 5, 7, 8]
    assert user['connection_requests'] == [2, 4, 6]
    assert user['blocked_profiles'] == [9, 10]
    assert not user['block_post_notifications']
    assert not user['block_message_notifications']