import os

import uvicorn
from clippie.api.api import router as api_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def get_application():
    application = FastAPI()
    application.include_router(api_router)

    origins = [
        "http://localhost:3000",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application

app = get_application()

def run():
    server_port = os.getenv("PORT") or 8000
    uvicorn.run("clippie.main:app", host="0.0.0.0", port=server_port, reload=True)


if __name__ == "__main__":
    run()
    