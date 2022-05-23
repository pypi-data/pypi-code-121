import uvicorn
from fastapi import FastAPI
from api_utils.database import conn
import router

app = FastAPI(title='Data.ly',
              description='APIs for base rankset data Apis',
              version='0.1')
app.include_router(router.data.router_data)


def run(host: str = '127.0.0.1', port: int = 8001):
    uvicorn.run(app=app, host=host, port=port)


@app.on_event("startup")
async def startup():
    print("Connect to db instance...")


@app.on_event("shutdown")
async def shutdown():
    print("Closing db instance...")
    conn.close_connection()
