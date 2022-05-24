import os

from hyperscience import (
    ApiController,
    Configuration,
    ContentType,
    CredentialsProvider,
    EnvironmentCredentialsProvider,
    HyperscienceLogging,
)
from hyperscience.api import DataSupportedMediaType
from hyperscience.api import PayloadSupportedMediaType


def _json_submission_request_body_file_decoded():
    return {
        "metadata": {},
        "machine_only": True,
        "goal_duration_minutes": 5,
        "single_document_per_page": True,
        "restrictions": [],
        "source_routing_tags": ["tag1", "tag2"],
        "files": [
            {
                "file_content_base64": "data:image/png;base64,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",
                "filename": "image.png"
            }
        ],
        "cases": [
            {
                "external_case_id": "case_1",
                "filenames": ["image.png"]
            }
        ]
    }


if __name__ == "__main__":
    # # Setting log level explicitly. Default level is error!
    # HyperscienceLogging().set_hyperscience_logging_level('DEBUG')

    '''
    Credentials support providing credentials using the following options:
        a. CredentialsProvider - explicitly providing client_id and client_secret
        b. EnvironmentCredentialsProvider - using env vars HS_CLIENT_ID and HS_CLIENT_SECRET
    '''
    # # a. CredentialsProvider
    # credentials = CredentialsProvider('client_id', 'client_secret')

    # b. EnvironmentCredentialsProvider
    credentials = EnvironmentCredentialsProvider()

    '''
    Configuration can be instantiated using the following options:
        a. using default configuration
        b. initializing from json file
        c. initializing from json string
        d. explicitly overriding properties
    Sample json file format:
    {
         "auth_server": "login.hyperscience.net",
         "hs_domain": "cloud.hyperscience.net"
    }
    '''
    # a. default configuration
    configuration = Configuration('cloud.hyperscience.net')

    # # b. using json file
    # current_dir = os.path.abspath(os.path.dirname(__file__))
    # config_path = os.path.join(current_dir, 'resources/config.json')
    # configuration = Configuration.from_file(config_path)

    # # c. using json string
    # config = '{ "auth_server": "login.hyperscience.net", "hs_domain": "cloud.hyperscience.net" }'
    # configuration = Configuration.from_json_string(config)

    # # d. overriding properties in configuration
    # configuration = Configuration('hs_domain_value')
    # # or
    # configuration = Configuration('hs_domain_value', 'auth_server_value')

    '''
    Different ways to instantiate ApiController: 
        a. Using default EnvironmentCredentialsProvider
        b. Using default Configuration provide Credentials explicitly 
    '''
    # # a. Using default credentials provider (EnvironmentCredentialsProvider)
    # api_controller = ApiController(configuration)

    # # b. Provided Credentials and Configuration
    api_controller = ApiController(configuration, credentials)

    # Simple get request
    res = api_controller.get('api/v5/healthcheck')
    print(res, res.content)

    # # Get request with query params provided in dictionary
    # query_params = {'state': 'complete'}
    # res = api_controller.get('/api/v5/submissions', query_params)
    # print(res, res.content)

    # # Get request with query params provided in List[Tuple] format
    # query_params = [('state', 'complete')]
    # res = api_controller.get('/api/v5/submissions', query_params)
    # print(res, res.content)

    # # Post request with MultipartFormData content-type to upload files from local server
    # # with dictionary (unique keys)
    # data = {'file': '/absolute/path/to/file.pdf', 'machine_only': True}
    # res = api_controller.post('/api/v5/submissions', data, DataSupportedMediaType.MULTIPART_FORM_DATA)
    # print(res, res.content)

    # # Post request with MultipartFormData content-type to upload files from local server
    # # with List[Tuple] (multiple identical keys, e.g. multiple files)
    # data = [
    #     ('file', '/absolute/path/to/file.pdf'),
    #     ('file', '/absolute/path/to/file2.pdf'),
    #     ('machine_only', True),
    # ]
    # res = api_controller.post('/api/v5/submissions', data, DataSupportedMediaType.MULTIPART_FORM_DATA)
    # print(res, res.content)

    # # Post request with WwwFormUrlEncoded content-type to submit files from remote servers
    # # with List[Tuple] (multiple identical keys, e.g. multiple files)
    # data = [
    #     ('file', 'https://www.dropbox.com/demo-long.pdf'),
    #     (
    #         'file',
    #         's3://hyperscience/bucket/form1.pdf',
    #     ),
    #     ('machine_only', True),
    # ]
    # res = api_controller.post('/api/v5/submissions', data, DataSupportedMediaType.FORM_URL_ENCODED)
    # print(res, res.content)

    # # Post request with implicit WwwFormUrlEncoded content-type to submit files from remote servers
    # # with dictionary (unique keys)
    # data = {
    #     'file': 'https://www.dropbox.com/demo-long.pdf',
    #     'machine_only': True,
    # }
    # res = api_controller.post('/api/v5/submissions', data)
    # print(res, res.content)

    # # Post request with WwwFormUrlEncoded content-type to submit files from remote servers
    # # with dictionary (unique keys)
    # data = {
    #     'file': 'https://www.dropbox.com/demo-long.pdf',
    #     'machine_only': True,
    # }
    # res = api_controller.post('/api/v5/submissions', data, DataSupportedMediaType.FORM_URL_ENCODED)
    # print(res, res.content)

    # # Post request with ApplicationJson content-type to submit base 64 encoded files from remote servers
    # # with dictionary (unique keys)
    # res = api_controller.post(
    #     '/api/v5/submissions',
    #     _json_submission_request_body_file_decoded(),
    #     PayloadSupportedMediaType.APPLICATION_JSON
    # )
    # print(res, res.content)
