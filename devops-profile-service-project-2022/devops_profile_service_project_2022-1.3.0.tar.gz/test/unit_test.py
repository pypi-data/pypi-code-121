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

@patch('profile_service.main.db', testDB)
def test_read_profile():
    res = client.get(PROFILE_URL, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
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
    res = client.put(PROFILE_URL, json=data, headers=generate_auth())
    assert res.status_code == 422
    body = json.loads(res.text)
    assert body['detail'][0]['loc'][0] == 'body'
    assert body['detail'][0]['loc'][1] == 'interests'
    assert body['detail'][0]['msg'] == 'value is not a valid list'
    assert body['detail'][0]['type'] == 'type_error.list'

@patch('profile_service.main.db', testDB)
def test_update_profile_valid():
    with patch.object(testDB, 'execute', wraps=testDB.execute) as db_spy:        
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
        res = client.put(PROFILE_URL, json=data, headers=generate_auth())
        assert res.status_code == 200
        body = json.loads(res.text)
        assert body is None
        db_spy.assert_called()
        db_spy.assert_any_call(' '.join('''
            update profiles 
            set first_name=%s, 
            last_name=%s, 
            email=%s, 
            phone_number=%s, 
            sex=%s, 
            birth_date=%s, 
            username=%s, 
            biography=%s, 
            private=%s, 
            work_experiences=%s, 
            educations=%s, 
            skills=%s, 
            interests=%s,
            block_post_notifications=%s,
            block_message_notifications=%s
            where id=0
        '''.split()), ('qwe', 'qwe', 'qwe', 'qwe', 'qwe', date(2012, 12, 12), 'qwe', 'qwe', False, '[]', '[]', '[]', '[{"name": "interest 1"}]', False, False))
