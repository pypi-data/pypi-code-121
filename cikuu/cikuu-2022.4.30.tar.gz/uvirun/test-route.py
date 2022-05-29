#from uvirun import * 
import json,os,uvicorn,time
from fastapi import FastAPI
from starlette.responses import JSONResponse 
from starlette.routing import Route

async def homepage(request):
    return JSONResponse({"index":"HOme"}) 

async def about(request):
    return JSONResponse({"index":"about"}) 

routes = [
    Route("/", endpoint=homepage,methods=["GET"]),
    Route("/about", endpoint=about,methods=["POST"]),
]

app=FastAPI(routes=routes)

if __name__ == '__main__':
	uvicorn.run(app, host='0.0.0.0', port=80)
