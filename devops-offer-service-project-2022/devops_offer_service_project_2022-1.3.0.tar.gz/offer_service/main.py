import uvicorn

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


app = FastAPI(title='Offer Service API')
db = create_engine('postgresql://postgres:postgres@offer_service_db:5432/postgres')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:4200'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

OFFERS_URL = '/api/offers'


class Offer(BaseModel):
    id: Optional[int] = Field(description='Offer ID')
    date: Optional[datetime] = Field(description='Offer Date')
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


@app.post(OFFERS_URL)
def create_offer(offer: Offer):
    with db.connect() as connection:
        connection.execute('insert into offers (date, position, requirements, description, agent_application_link) values (current_timestamp, %s, %s, %s, %s)', 
                           (offer.position, offer.requirements, offer.description, offer.agent_application_link))


def search_query(search: str):
    return 'lower(position) like %s or lower(requirements) like %s or lower(description) like %s', (f'%{search.lower()}%', f'%{search.lower()}%', f'%{search.lower()}%')


@app.get(OFFERS_URL)
def read_offers(search: str = Query(''), offset: int = Query(0), limit: int = Query(7)):
    query, params = search_query(search)
    with db.connect() as connection:
        total_offers = len(list(connection.execute(f'select * from offers where {query}', params)))
        offers = connection.execute(f'select * from offers where {query} order by date desc offset {offset} limit {limit}', params)

    prev_link = f'/offers?search={search}&offset={offset-limit}&limit={limit}' if offset - limit >= 0 else None
    next_link = f'/offers?search={search}&offset={offset+limit}&limit={limit}' if offset + limit < total_offers else None
    links = NavigationLinks(prev=prev_link, next=next_link)
    results = [Offer.parse_obj(offer) for offer in offers]

    return Response(results=results, links=links, offset=offset, limit=limit, size=len(results))


def run_service():
    uvicorn.run(app, host='0.0.0.0', port=8002)


if __name__ == '__main__':
    run_service()
