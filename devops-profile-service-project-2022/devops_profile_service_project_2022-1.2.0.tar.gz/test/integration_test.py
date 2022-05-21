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
