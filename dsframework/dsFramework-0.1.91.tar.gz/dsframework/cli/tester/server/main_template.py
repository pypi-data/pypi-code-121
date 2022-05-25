from typing import Union, List

import logging
import sys
from pythonjsonlogger import jsonlogger

##  Logger setup
root = logging.getLogger()
root.setLevel(logging.INFO)
## Redirect logging to sys.stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
## Assign logger a json formatter to output log data as json.
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger(__name__)

import os
import json
import uvicorn
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from pipeline.pipeline import generatedProjectNamePipeline
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from tester.test_schema.test_input import TestInputRequest
from tester.test_schema.test_output import TestOutputResponse
from tester.general_tester import generatedProjectNameGeneralTester


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token": # todo: please replace with realistic token
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_env():
    # Don't allow usage of an endpoint on production environment
    if os.environ.get('SPRING_PROFILES_ACTIVE') == 'production':
        raise HTTPException(status_code=404, detail="Endpoint not available")


def load_allowed_cors_origins():
    allowed_origins = []
    cors_origin_list_path = 'server/cors_allowed_origins.json'
    if os.path.exists(cors_origin_list_path):
        with open(cors_origin_list_path) as f:
            allowed_origins = json.load(f)

    return allowed_origins


def get_host(request: Request):
    """! Try to obtain information about the requesting host / service
        Args:
            request: Request -> Incoming request
        Returns:
            host: Obtained host
            service_account: Obtained service account
    """
    x_forwarded_for = request.headers.get('x-forwarded-for')
    x_goog_authenticated_user_email = request.headers.get('x-goog-authenticated-user-email')
    service_account = ''
    host = ''
    try:
        if x_goog_authenticated_user_email:
            service_account = x_goog_authenticated_user_email.replace('accounts.google.com:', '')
        if x_forwarded_for:
            host = x_forwarded_for
    except Exception as e:
        print(f'Attempt to get headers from: {request.headers} failed. Error: {e}')
        pass
    return host, service_account


## Instantiate FastAPI()
app = FastAPI()
## Allowed cors origins
origins = load_allowed_cors_origins()
## Methods allowed, for FastAPI()
methods = ["*"]
## Headers allowed, for FastAPI()
headers = ["*"]
## Credentials required, bool.
credentials = True
##
# @var allow_origins
# Cors allowed origins.
# @var allow_credentials
# Allowed credentials by FastAPI()
# @var allow_methods
# Allowed methods by FastAPI()
# @var allow_headers
# Allowed headers by FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=methods,
    allow_headers=headers,
)
## Initialized a pipeline for /predict /parse endpoints.
pipeline = generatedProjectNamePipeline()
# from server.pool import InstancePool
# pipelines = [generatedProjectNamePipeline() for i in range(3)]
# app.pipelines = InstancePool(pipelines)


@app.post('/predict', dependencies=[Depends(get_token_header)])
def predict(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    """! Predict api endpoint, is designed to support predict projects such as
    scoops classification, valid user email etc.

    Use by post request, for example:

        headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
        url = http://localhost:8080/predict
        data = {}  # The data to run by model.
        response = requests.post(url, json=data, headers=headers)

    """
    requesting_host, requesting_sa = get_host(request)
    data = body.dict()
    # logger.info({"message": "predict invoked", "data": json.dumps(data)})
    # print('data', data)

    # call model here
    try:
        output: generatedProjectNameOutputs = pipeline.execute(**data)
        logger.info("INFO predict invoked", extra={"input": data, "output": output.dict(),
                                                   "from_host": requesting_host, "from_service_account": requesting_sa})
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': ex}}
        logger.error("ERROR predict invoked", extra={"input": data, "output": output,
                                                     "from_host": requesting_host,
                                                     "from_service_account": requesting_sa})
    # call model here
    return output


@app.post('/parse', dependencies=[Depends(get_token_header)])
def parse(body: generatedProjectNameInputs, request: Request) -> List[generatedProjectNameOutputs]:
    """! Parse api endpoint, is designed to support parse projects such as trex, bio parser, sig parser etc.

    Use by post request, for example:

        headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
        url = http://localhost:8080/parse
        data = {}  # The data to run by model.
        response = requests.post(url, json=data, headers=headers)

    """
    requesting_host, requesting_sa = get_host(request)
    data = body.dict()
    # logger.info({"message": "parse invoked", "data": json.dumps(data)})
    # print('data', data)

    # call model here
    try:
        output: generatedProjectNameOutputs = pipeline.execute(**data)
        logger.info("INFO parse invoked", extra={"input": data, "output": output.dict(),
                                                 "from_host": requesting_host, "from_service_account": requesting_sa})
    except Exception as ex:
        logger.exception(msg=data, exc_info=True)
        output = {'error': {'request': ex}}
        logger.error("ERROR parse invoked", extra={"input": data, "output": output,
                                                   "from_host": requesting_host, "from_service_account": requesting_sa})
    # call model here
    return output


## Fetch the proper tester for the project
model_tester = generatedProjectNameGeneralTester()


@app.post('/test', dependencies=[Depends(get_token_header), Depends(verify_env)], include_in_schema=False)
def test(input_request: TestInputRequest) -> List[TestOutputResponse]:
    """! This is the main endpoint for testing.

        Args:
            input_request: Request as received from the DSP
        Returns:
            A list of responses, to be sent back to the DSP

    Every project starts with a default mock response service, in order to enable DSP integration (when the working
    testing functions are ready and implemented in the tester/general_tester.py),
    replace the mock service with the real one, in practice just remark the following line:

        response = model_tester.create_mock_response(input_request)

    and remove remark quotes from the following block of code:

        model_tester.save_meta_data(input_request)
        response = []
        # Until this model will support batches, work sequentially. Once it does, pass the full list of rows.
        for request_row in input_request.rows:
            input_list = [request_row]
            tester_output = model_tester.test_batch(input_list)
            response.append(tester_output[0])

    """
    response = model_tester.create_mock_response(input_request)

    """    
    model_tester.save_meta_data(input_request)
    response = []
    # Until this model will support batches, work sequentially. Once it does, pass the full list of rows.
    for request_row in input_request.rows:
        input_list = [request_row]
        tester_output = model_tester.test_batch(input_list)
        response.append(tester_output[0])
    """
    return response


@app.get("/livenessprobe")
def liveness_probe():
    """! Endpoint used to test server liveness

        Usage:
            http://localhost:8080/livenessprobe

        Returns:
            server response: {"alive": True} - On success

    """
    return {"alive": True}


@app.get("/readinessprobe")
def readiness_probe():
    """! Endpoint used to test server readiness

        Usage:
            http://localhost:8080/readinessprobe

        Returns:
            server response: {"ready": True} - On success

        """
    return {"ready": True}


if __name__ == '__main__':
    # Runs the server
    ##
    # @var host
    # IP Address
    # @var port
    # Port number
    uvicorn.run(app, host='0.0.0.0', port=8080)

