from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi_contrib.conf import settings
from sqlalchemy import create_engine
from kafka import KafkaProducer
from pydantic import BaseModel, Field
from typing import Optional, List
from jaeger_client import Config
from opentracing.scope_managers.asyncio import AsyncioScopeManager
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info

import uvicorn
import time
import json


app = FastAPI(title='Offer Service API')
db = create_engine('postgresql://postgres:postgres@offer_service_db:5432/postgres')
kafka_producer = None

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
        service_name="offer_service",
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

OFFERS_URL = '/api/offers'


class Offer(BaseModel):
    id: Optional[int] = Field(description='Offer ID')
    position: str = Field(description='Offer Position', min_length=1)
    requirements: str = Field(description='Offer Requirements', min_length=1)
    description: str = Field(description='Offer Description', min_length=1)
    agent_application_link: str = Field(description='Offer Agent Application Link', min_length=1)


class NavigationLinks(BaseModel):
    base: str = Field('http://localhost:9000/api', description='API base URL')
    prev: Optional[str] = Field(None, description='Link to the previous page')
    next: Optional[str] = Field(None, description='Link to the next page')


class Response(BaseModel):
    results: List[Offer]
    links: NavigationLinks
    offset: int
    limit: int
    size: int

def register_kafka_producer():
    global kafka_producer
    while True:
        try:
            kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            break
        except:
            time.sleep(3)   

def record_action(status: int, message: str, span):
    print("{0:10}{1}".format('ERROR:' if status >= 400 else 'INFO:', message))
    span.set_tag('http_status', status)
    span.set_tag('message', message)

def record_event(type: str, data: dict):
    kafka_producer.send('events', {
        'type': type,
        'data': data
    })

@app.post(OFFERS_URL)
def create_offer(offer: Offer):
    with app.tracer.start_span('Create Offer Request') as span:
        try:
            span.set_tag('http_method', 'POST')
            db.execute('insert into offers (position, requirements, description, agent_application_link) values (%s, %s, %s, %s)', 
                                (offer.position, offer.requirements, offer.description, offer.agent_application_link))

            record_action(200, 'Request successful', span)
            record_event('Job Offer Created', dict(offer))
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


def search_query(search: str):
    return 'lower(position) like %s or lower(requirements) like %s or lower(description) like %s', (f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%')


@app.get(OFFERS_URL)
def read_offers(search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    with app.tracer.start_span('Read Offers Request') as span:
        try:
            span.set_tag('http_method', 'GET')
            query, params = search_query(search)
            total_offers = len(list(db.execute(f'select * from offers where {query}', params)))
            offers = db.execute(f'select * from offers where {query} order by id desc offset {offset} limit {limit}', params)

            prev_link = f'/offers?search={search}&offset={offset-limit}&limit={limit}' if offset - limit >= 0 else None
            next_link = f'/offers?search={search}&offset={offset+limit}&limit={limit}' if offset + limit < total_offers else None
            links = NavigationLinks(prev=prev_link, next=next_link)
            results = [Offer.parse_obj(offer) for offer in offers]

            record_action(200, 'Request successful', span)
            return Response(results=results, links=links, offset=offset, limit=limit, size=len(results))
        except Exception as e:
            record_action(500, 'Request failed', span)
            raise e


def run_service():
    register_kafka_producer()
    uvicorn.run(app, host='0.0.0.0', port=8002)


if __name__ == '__main__':
    run_service()
