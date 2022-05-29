from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_contrib.conf import settings
from sqlalchemy import create_engine
from kafka import KafkaConsumer
from pydantic import BaseModel, Field
from typing import Optional, List
from jaeger_client import Config
from opentracing.scope_managers.asyncio import AsyncioScopeManager
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info

import uvicorn
import datetime
import time
import json
import jwt
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

def setup_opentracing(app):
    config = Config(
        config={
            "local_agent": {
                "reporting_host": settings.jaeger_host,
                "reporting_port": settings.jaeger_port
            },
            "sampler": {
                "type": settings.jaeger_sampler_type,
                "param": settings.jaeger_sampler_rate,
            },
            "trace_id_header": settings.trace_id_header
        },
        service_name="profile_service",
        validate=True,
        scope_manager=AsyncioScopeManager()
    )

    app.state.tracer = config.initialize_tracer()
    app.tracer = app.state.tracer

setup_opentracing(app)

def http_404_requests():
    METRIC = Counter(
        "http_404_requests",
        "Number of times a 404 request has occured.",
        labelnames=("path",)
    )

    def instrumentation(info: Info):
        if info.response.status_code == 404:
            METRIC.labels(info.request.url).inc()

    return instrumentation

def http_unique_users():
    METRIC = Counter(
        "http_unique_users",
        "Number of unique http users.",
        labelnames=("user",)
    )

    def instrumentation(info: Info):
        try:
            user = f'{info.request.client.host} {info.request.headers["User-Agent"]}'
        except:
            user = f'{info.request.client.host} Unknown'
        METRIC.labels(user).inc()

    return instrumentation


instrumentator = Instrumentator(excluded_handlers=["/metrics"])
instrumentator.add(metrics.default())
instrumentator.add(metrics.combined_size())
instrumentator.add(http_404_requests())
instrumentator.add(http_unique_users())
instrumentator.instrument(app).expose(app)

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
    birth_date: datetime.date = Field(description='Birth Date')
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

def record_action(status: int, message: str, span):
    print("{0:10}{1}".format('ERROR:' if status >= 400 else 'INFO:', message))
    span.set_tag('http_status', status)
    span.set_tag('message', message)

def get_user(id: int):
    return Profile.parse_obj(dict(list(db.execute('select * from profiles where id=%s', (id,)))[0]))

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
    if type == '':
        entities = 'Profiles'
    elif type == '/public':
        entities = 'Public Profiles'
    elif type == '/connections':
        entities = 'Connections'
    else:
        entities = 'Connection Requests'
    with app.tracer.start_span(f'Read {entities} Request') as span:
        try:
            span.set_tag('http_method', 'GET')
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

            total_profiles = len(list(db.execute(f'select * from profiles where id!={current_user_id} and {filter} and ({query})', params)))
            profiles = list(db.execute(f'select * from profiles where id!={current_user_id} and {filter} and ({query}) order by id offset {offset} limit {limit}', params))

            prev_link = f'/profiles{type}?search={search}&offset={offset - limit}&limit={limit}' if offset - limit >= 0 else None
            next_link = f'/profiles{type}?search={search}&offset={offset + limit}&limit={limit}' if offset + limit < total_profiles else None
            links = NavigationLinks(prev=prev_link, next=next_link)
            results = [Profile.parse_obj(dict(profile)) for profile in profiles]
            
            record_action(200, 'Request successful', span)
            return ProfileResponse(results=results, links=links, offset=offset, limit=limit, size=len(results))
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


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

@app.get(PROFILE_URL)
def read_profile(request: Request):
    with app.tracer.start_span('Read Profile Request') as span:
        try:
            span.set_tag('http_method', 'GET')

            record_action(200, 'Request successful', span)
            return get_current_user(request)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


@app.put(PROFILE_URL)
def update_profile(request: Request, profile: Profile):
    with app.tracer.start_span('Update Profile Request') as span:
        try:
            span.set_tag('http_method', 'PUT')
            current_user = get_current_user(request)

            db.execute(' '.join(f'''
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
                where id={current_user.id}
            '''.split()), (profile.first_name, profile.last_name, profile.email, profile.phone_number, 
                    profile.sex, profile.birth_date, profile.username, profile.biography, profile.private,
                    str(profile.work_experiences or []).replace("'", '"'), str(profile.educations or []).replace("'", '"'), 
                    str(profile.skills or []).replace("'", '"'), str(profile.interests or []).replace("'", '"'),
                    profile.block_post_notifications or False, profile.block_message_notifications or False))
        
            record_action(200, 'Request successful', span)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


@app.put(PROFILE_URL + '/connect/{profile_id}')
def connect(request: Request, profile_id: int):
    with app.tracer.start_span('Connect Profile Request') as span:
        try:
            span.set_tag('http_method', 'PUT')
            current_user = get_current_user(request)
            connection_user = get_user(profile_id)
            if profile_id in dict(current_user)['blocked_profiles']:
                record_action(400, 'Request failed - Cannot connect to blocked profile', span)
                raise HTTPException(status_code=400, detail='Cannot connect to blocked profile')

            if connection_user.private:
                db.execute(f'''
                    update profiles 
                    set connections='{list(filter(lambda x: x != profile_id, current_user.connections))}',
                    connection_requests='{list(filter(lambda x: x != profile_id, current_user.connection_requests))}',
                    blocked_profiles='{list(filter(lambda x: x != profile_id, current_user.blocked_profiles))}'
                    where id={current_user.id}
                ''')
                db.execute(f'''
                    update profiles 
                    set connections='{list(filter(lambda x: x != current_user.id, connection_user.connections))}',
                    connection_requests='{sorted(list(set(connection_user.connection_requests + [current_user.id])))}',
                    blocked_profiles='{list(filter(lambda x: x != current_user.id, connection_user.blocked_profiles))}'
                    where id={connection_user.id}
                ''')
            else:
                db.execute(f'''
                    update profiles 
                    set connections='{sorted(list(set(current_user.connections + [profile_id])))}',
                    connection_requests='{list(filter(lambda x: x != profile_id, current_user.connection_requests))}',
                    blocked_profiles='{list(filter(lambda x: x != profile_id, current_user.blocked_profiles))}'
                    where id={current_user.id}
                ''')
                db.execute(f'''
                    update profiles 
                    set connections='{sorted(list(set(connection_user.connections + [current_user.id])))}',
                    connection_requests='{list(filter(lambda x: x != current_user.id, connection_user.connection_requests))}',
                    blocked_profiles='{list(filter(lambda x: x != current_user.id, connection_user.blocked_profiles))}'
                    where id={connection_user.id}
                ''')

            record_action(200, 'Request successful', span)
            return get_current_user(request)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


@app.put(PROFILE_URL + '/accept/{profile_id}')
def accept(request: Request, profile_id: int):
    with app.tracer.start_span('Accept Profile Request') as span:
        try:
            span.set_tag('http_method', 'PUT')
            current_user = get_current_user(request)
            connection_user = get_user(profile_id)

            db.execute(f'''
                update profiles 
                set connections='{sorted(list(set(current_user.connections + [profile_id])))}',
                connection_requests='{list(filter(lambda x: x != profile_id, current_user.connection_requests))}',
                blocked_profiles='{list(filter(lambda x: x != profile_id, current_user.blocked_profiles))}'
                where id={current_user.id}
            ''')
            db.execute(f'''
                update profiles 
                set connections='{sorted(list(set(connection_user.connections + [current_user.id])))}',
                connection_requests='{list(filter(lambda x: x != current_user.id, connection_user.connection_requests))}',
                blocked_profiles='{list(filter(lambda x: x != current_user.id, connection_user.blocked_profiles))}'
                where id={connection_user.id}
            ''')
            
            record_action(200, 'Request successful', span)
            return get_current_user(request)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


@app.put(PROFILE_URL + '/reject/{profile_id}')
def reject(request: Request, profile_id: int):
    with app.tracer.start_span('Reject Profile Request') as span:
        try:
            span.set_tag('http_method', 'PUT')
            current_user = get_current_user(request)
            connection_user = get_user(profile_id)

            db.execute(f'''
                update profiles 
                set connections='{list(filter(lambda x: x != profile_id, current_user.connections))}',
                connection_requests='{list(filter(lambda x: x != profile_id, current_user.connection_requests))}',
                blocked_profiles='{list(filter(lambda x: x != profile_id, current_user.blocked_profiles))}'
                where id={current_user.id}
            ''')
            db.execute(f'''
                update profiles 
                set connections='{list(filter(lambda x: x != current_user.id, connection_user.connections))}',
                connection_requests='{list(filter(lambda x: x != current_user.id, connection_user.connection_requests))}',
                blocked_profiles='{list(filter(lambda x: x != current_user.id, connection_user.blocked_profiles))}'
                where id={connection_user.id}
            ''')

            record_action(200, 'Request successful', span)
            return get_current_user(request)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e            



@app.put(PROFILE_URL + '/block/{profile_id}')
def block(request: Request, profile_id: int):
    with app.tracer.start_span('Block Profile Request') as span:
        try:
            span.set_tag('http_method', 'PUT')
            current_user = get_current_user(request)
            connection_user = get_user(profile_id)

            db.execute(f'''
                update profiles 
                set connections='{list(filter(lambda x: x != profile_id, current_user.connections))}',
                connection_requests='{list(filter(lambda x: x != profile_id, current_user.connection_requests))}',
                blocked_profiles='{sorted(list(set(current_user.blocked_profiles + [profile_id])))}'
                where id={current_user.id}
            ''')
            db.execute(f'''
                update profiles 
                set connections='{list(filter(lambda x: x != current_user.id, connection_user.connections))}',
                connection_requests='{list(filter(lambda x: x != current_user.id, connection_user.connection_requests))}',
                blocked_profiles='{sorted(list(set(connection_user.blocked_profiles + [current_user.id])))}'
                where id={connection_user.id}
            ''')

            record_action(200, 'Request successful', span)
            return get_current_user(request)
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e            


@app.get(NOTIFICATIONS_URL)
def read_notifications(request: Request, search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    with app.tracer.start_span('Read Notifications Request') as span:
        try:
            span.set_tag('http_method', 'GET')
            current_user_id = get_current_user(request).id
            total_notifications = len(list(db.execute(f'select * from notifications where recipient_id={current_user_id} and lower(message) like %s', (f'%{search.lower()}%',))))
            notifications = list(db.execute(f'select * from notifications where recipient_id={current_user_id} and lower(message) like %s order by id desc offset {offset} limit {limit}', (f'%{search.lower()}%',)))
            
            prev_link = f'/notifications?search={search}&offset={offset - limit}&limit={limit}' if offset - limit >= 0 else None
            next_link = f'/notifications?search={search}&offset={offset + limit}&limit={limit}' if offset + limit < total_notifications else None
            links = NavigationLinks(prev=prev_link, next=next_link)
            results = [Notification.parse_obj(dict(notification)) for notification in notifications]
            
            record_action(200, 'Request successful', span)
            return NotificationResponse(results=results, links=links, offset=offset, limit=limit, size=len(results))
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e            


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
                db.execute('insert into profiles (id, first_name, last_name, email, phone_number, sex, birth_date, username, biography, private) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
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
     
                if notification['type'] == 'post':
                    recipients = list(db.execute(f'select * from profiles where id={notification["user_id"]}'))[0].connections
                    for user_id in recipients:
                        block_post_notifications = list(db.execute(f'select * from profiles where id={user_id}'))[0].block_post_notifications
                        if block_post_notifications:
                            recipients = list(filter(lambda x: x != user_id, recipients))
                else:
                    block_message_notifications = list(db.execute(f'select * from profiles where id={notification["user_id"]}'))[0].block_message_notifications
                    recipients = [notification['user_id']] if not block_message_notifications else []                            

                for recipient_id in recipients:
                    db.execute(f'insert into notifications (recipient_id, message) values ({recipient_id}, %s)', (notification['message'],))
            except:
                pass

    threading.Thread(target=poll).start()


def run_service():
    register_profiles_consumer()
    register_notifications_consumer()
    uvicorn.run(app, host='0.0.0.0', port=8001)


if __name__ == '__main__':
    run_service()
