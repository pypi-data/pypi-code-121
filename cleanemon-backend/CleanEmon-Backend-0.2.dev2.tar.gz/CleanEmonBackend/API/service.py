import uvicorn


def run():
    uvicorn.run("CleanEmonBackend.API:api", reload=True)
