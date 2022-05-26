import uvicorn
from fastapi import FastAPI
from router import entities
from api_utils.database import conn

app = FastAPI(title='Entities.ly',
              description='APIs for base entities Apis',
              version='0.1')
app.include_router(entities.router_entities)


def run(host: str = '127.0.0.1', port: int = 8000):
    uvicorn.run(app=app, host=host, port=port)


@app.on_event("startup")
async def startup():
    if conn.is_closed():
        conn.connect()


@app.on_event("shutdown")
async def shutdown():
    print("Closing...")
    if not conn.is_closed():
        conn.close()
