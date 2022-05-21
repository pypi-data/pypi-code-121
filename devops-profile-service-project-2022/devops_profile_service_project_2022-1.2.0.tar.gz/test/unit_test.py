from profile_service.main import app, PROFILES_URL, PROFILE_URL, JWT_SECRET, JWT_ALGORITHM
from fastapi.testclient import TestClient
from mock import patch
from datetime import date
import json
import jwt

class TestDB:
    
    def connect(self):
        return self
    def execute(self, sql, params):
        return [{
            'id': 0,
            'first_name': 'asd',
            'last_name': 'asd',
            'email': 'asd',
            'phone_number': 'asd',
            'sex': 'asd',
            'birth_date': date.today(),
            'username': 'asd',
            'biography': 'asd',
            'private': True,
            'work_experiences': [],
            'educations': [],
            'skills': [],
            'interests': [],
            'connections': [1, 3, 5, 7, 8],
            'connection_requests': [2, 4, 6],
            'blocked_profiles': [9, 10],
            'block_post_notifications': False,
            'block_message_notifications': False
        }]
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, tb):
        pass

client = TestClient(app)
testDB = TestDB()

def generate_auth():
    return {'Authorization': jwt.encode({'id': 0}, JWT_SECRET, algorithm=JWT_ALGORITHM)}

def filter():
    return ' '.join('''
        lower(first_name) like %s or 
        lower(last_name) like %s or 
        lower(email) like %s or 
        lower(phone_number) like %s or 
        lower(sex) like %s or 
        lower(username) like %s or 
        lower(biography) like %s
    '''.split())

@patch('profile_service.main.db', testDB)
def test_read_profiles():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(PROFILES_URL, headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))
        
@patch('profile_service.main.db', testDB)
def test_read_profiles_with_offset():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?offset=7', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 7 limit 7                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_profiles_with_limit():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?limit=10', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 10                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_first_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=FIRST_NAME', headers=generate_auth())
        assert res.status_code == 200        
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_last_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=LAST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_email():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=EMAIL', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%email%', '%email%', '%email%', '%email%', '%email%', '%email%', '%email%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_phone_number():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=PHONE_NUMBER', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_sex():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=SEX', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_username():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=USERNAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%username%', '%username%', '%username%', '%username%', '%username%', '%username%', '%username%'))

@patch('profile_service.main.db', testDB)
def test_search_profiles_by_biography():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}?search=BIOGRAPHY', headers=generate_auth())
        assert res.status_code == 200        
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and true and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%'))

@patch('profile_service.main.db', testDB)
def test_read_public_profiles():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_public_profiles_with_offset():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?offset=7', headers=generate_auth())
        assert res.status_code == 200        
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 7 limit 7                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_public_profiles_with_limit():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?limit=10', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 10                          
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_first_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=FIRST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_last_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=LAST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_email():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=EMAIL', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%email%', '%email%', '%email%', '%email%', '%email%', '%email%', '%email%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_phone_number():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=PHONE_NUMBER', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_sex():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=SEX', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_username():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=USERNAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%username%', '%username%', '%username%', '%username%', '%username%', '%username%', '%username%'))

@patch('profile_service.main.db', testDB)
def test_search_public_profiles_by_biography():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/public?search=BIOGRAPHY', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and private=false and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%'))


@patch('profile_service.main.db', testDB)
def test_read_connections():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_connections_with_offset():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?offset=7', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 7 limit 7                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))


@patch('profile_service.main.db', testDB)
def test_read_connections_with_limit():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?limit=10', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 10                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_first_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=FIRST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_last_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=LAST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_email():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=EMAIL', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%email%', '%email%', '%email%', '%email%', '%email%', '%email%', '%email%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_phone_number():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=PHONE_NUMBER', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_sex():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=SEX', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_username():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=USERNAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%username%', '%username%', '%username%', '%username%', '%username%', '%username%', '%username%'))

@patch('profile_service.main.db', testDB)
def test_search_connections_by_biography():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connections?search=BIOGRAPHY', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (1, 3, 5, 7, 8) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%'))

@patch('profile_service.main.db', testDB)
def test_read_connection_requests():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_connection_requests_with_offset():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?offset=7', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 7 limit 7                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_read_connection_requests_with_limit():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?limit=10', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 10                        
        '''.split()), ('%%', '%%', '%%', '%%', '%%', '%%', '%%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_first_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=FIRST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%', '%first_name%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_last_name():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=LAST_NAME', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%', '%last_name%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_email():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=EMAIL', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%email%', '%email%', '%email%', '%email%', '%email%', '%email%', '%email%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_phone_number():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=PHONE_NUMBER', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%', '%phone_number%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_sex():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=SEX', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%', '%sex%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_username():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=USERNAME', headers=generate_auth())
        assert res.status_code == 200        
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%username%', '%username%', '%username%', '%username%', '%username%', '%username%', '%username%'))

@patch('profile_service.main.db', testDB)
def test_search_connection_requests_by_biography():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
        res = client.get(f'{PROFILES_URL}/connection_requests?search=BIOGRAPHY', headers=generate_auth())
        assert res.status_code == 200
        db_spy.assert_called()
        db_spy.assert_called_with(' '.join(f'''
            select * from profiles where id!=0 and id in (2, 4, 6) and ({filter()}) order by id offset 0 limit 7                        
        '''.split()), ('%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%', '%biography%'))
