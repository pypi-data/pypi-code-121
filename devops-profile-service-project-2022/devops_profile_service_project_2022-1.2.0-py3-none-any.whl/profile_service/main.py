from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from kafka import KafkaConsumer
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

import uvicorn
import json
import jwt
import time
import threading

app = FastAPI(title='Profile Service API')
db = create_engine('postgresql://postgres:postgres@profile_service_db:5432/postgres')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

PROFILES_URL = '/api/profiles'
PROFILE_URL = '/api/profile'
NOTIFICATIONS_URL = '/api/notifications'
JWT_SECRET = 'auth_service_secret'
JWT_ALGORITHM = 'HS256'

class Profile(BaseModel):
    id: Optional[int] = Field(description='Profile ID')
    first_name: str = Field(description='First Name', min_length=1)
    last_name: str = Field(description='Last Name', min_length=1)
    email: str = Field(description='Email', min_length=1)
    phone_number: str = Field(description='Phone Number', min_length=1)
    sex: str = Field(description='Sex', min_length=1)
    birth_date: date = Field(description='Birth Date')
    username: str = Field(description='Username', min_length=1)
    biography: str = Field(description='Biography', min_length=1)
    private: bool = Field(description='Flag if profile is private')
    work_experiences: Optional[list] = Field(description='Work Experiences')
    educations: Optional[list] = Field(description='Educations')
    skills: Optional[list] = Field(description='Skills')
    interests: Optional[list] = Field(description='Interests')
    connections: Optional[list] = Field(description='Connection IDs')
    connection_requests: Optional[list] = Field(description='Connection Request IDs')
    blocked_profiles: Optional[list] = Field(description='Blocked Profile IDs')
    block_post_notifications: Optional[bool] = Field(description='Flag if profile blocked post notifications')
    block_message_notifications: Optional[bool] = Field(description='Flag if profile blocked message notifications')

class Notification(BaseModel):
    id: int = Field(description='Notification ID')
    recipient_id: int = Field(description='Notification recipient ID')
    message: str = Field(description='Notification message')

class NavigationLinks(BaseModel):
    base: str = Field('http://localhost:9000/api', description='API base URL')
    prev: Optional[str] = Field(None, description='Link to the previous page')
    next: Optional[str] = Field(None, description='Link to the next page')

class ProfileResponse(BaseModel):
    results: List[Profile]
    links: NavigationLinks
    offset: int
    limit: int
    size: int

class NotificationResponse(BaseModel):
    results: List[Notification]
    links: NavigationLinks
    offset: int
    limit: int
    size: int


def get_user(id: int):
    with db.connect() as connection:
        return Profile.parse_obj(dict(list(connection.execute('select * from profiles where id=%s', (id,)))[0]))

def get_current_user(request: Request):
    try:
        return get_user(jwt.decode(request.headers['Authorization'], JWT_SECRET, algorithms=[JWT_ALGORITHM])['id'])
    except:
        return None

def search_query(search: str):
    return ' '.join('''
        lower(first_name) like %s or 
        lower(last_name) like %s or 
        lower(email) like %s or 
        lower(phone_number) like %s or 
        lower(sex) like %s or 
        lower(username) like %s or 
        lower(biography) like %s
    '''.split()), (f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%')

def search_profiles(request: Request, search: str, offset: int, limit: int, type: str = ''):
    current_user = get_current_user(request)
    current_user_id = current_user.id if current_user else 0
    query, params = search_query(search)

    if type == '':
        filter = 'true'
    elif type == '/public':
        filter = 'private=false'
    else:
        filter_list = current_user.connections if type == '/connections' else current_user.connection_requests
        filter = f"id in {str(filter_list).replace('[', '(').replace(']', ')')}" if filter_list else 'false'

    with db.connect() as connection:
        total_profiles = len(list(connection.execute(f'select * from profiles where id!={current_user_id} and {filter} and ({query})', params)))
        profiles = list(connection.execute(f'select * from profiles where id!={current_user_id} and {filter} and ({query}) order by id offset {offset} limit {limit}', params))

    prev_link = f'/profiles{type}?search={search}&offset={offset - limit}&limit={limit}' if offset - limit >= 0 else None
    next_link = f'/profiles{type}?search={search}&offset={offset + limit}&limit={limit}' if offset + limit < total_profiles else None
    links = NavigationLinks(prev=prev_link, next=next_link)
    results = [Profile.parse_obj(dict(profile)) for profile in profiles]
    return ProfileResponse(results=results, links=links, offset=offset, limit=limit, size=len(results))

@app.get(PROFILES_URL)
def read_profiles(request: Request, search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    return search_profiles(request, search, offset, limit)

@app.get(f'{PROFILES_URL}/public')
def read_public_profiles(request: Request, search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    return search_profiles(request, search, offset, limit, '/public')

@app.get(f'{PROFILES_URL}/connections')
def read_connections(request: Request, search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    return search_profiles(request, search, offset, limit, '/connections')

@app.get(f'{PROFILES_URL}/connection_requests')
def read_connection_requests(request: Request, search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    return search_profiles(request, search, offset, limit, '/connection_requests')


def register_profiles_consumer():
    def poll():
        while True:
            try:
                consumer = KafkaConsumer('profiles', bootstrap_servers=['kafka:9092'])
                break
            except:
                time.sleep(3)

        for data in consumer:
            try:
                profile = Profile.parse_obj(json.loads(data.value.decode('utf-8')))
                with db.connect() as connection:
                    connection.execute('insert into profiles (id, first_name, last_name, email, phone_number, sex, birth_date, username, biography, private) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        (profile.id, profile.first_name, profile.last_name, profile.email, profile.phone_number, profile.sex, profile.birth_date, profile.username, profile.biography, profile.private))
            except:
                pass

    threading.Thread(target=poll).start()

def register_notifications_consumer():
    def poll():
        while True:
            try:
                consumer = KafkaConsumer('notifications', bootstrap_servers=['kafka:9092'])
                break
            except:
                time.sleep(3)

        for data in consumer:
            try:
                notification = json.loads(data.value.decode('utf-8'))       
     
                with db.connect() as connection:
                    if notification['type'] == 'post':
                        recipients = list(connection.execute(f'select * from profiles where id={notification["user_id"]}'))[0].connections
                        for user_id in recipients:
                            block_post_notifications = list(connection.execute(f'select * from profiles where id={user_id}'))[0].block_post_notifications
                            if block_post_notifications:
                                recipients = list(filter(lambda x: x != user_id, recipients))
                    else:
                        block_message_notifications = list(connection.execute(f'select * from profiles where id={notification["user_id"]}'))[0].block_message_notifications
                        recipients = [notification['user_id']] if not block_message_notifications else []                            

                    for recipient_id in recipients:
                        connection.execute(f'insert into notifications (recipient_id, message) values ({recipient_id}, %s)', (notification['message'],))
            except:
                pass

    threading.Thread(target=poll).start()


def run_service():
    register_profiles_consumer()
    register_notifications_consumer()
    uvicorn.run(app, host='0.0.0.0', port=8001)


if __name__ == '__main__':
    run_service()
