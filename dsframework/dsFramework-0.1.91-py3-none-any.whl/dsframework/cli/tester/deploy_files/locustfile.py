from locust import HttpUser, task
import pandas as pd
import numpy as np

from server.token_generator import tokenGenerator

##
# @file
# @brief Stress testing server using locust package.

t = tokenGenerator()
jwtToken = t.generateToken('STG_Conf')
global_headers = {
    'x-token': 'fake-super-secret-token',
    'Authorization': 'Bearer ' + jwtToken
}


class payloadUser(HttpUser):
    """! payloadUser class implements HttpUser base class. It is used to stress test a server, by sending repeated
    requests to the server, using locust package.

    Running a test:

    -# Install package, using:
        - pip install locust

    -# Create a sample dataset that reflects real data variety.
        - Save it in sample.csv file.
        - For example:
            @code {.py}
            titles_history,pred
            "[{"title":"Software Engineer","order":1,"desc":"","company":"","company_id":-1,"company_size":0},
            {"title":"Senior Software Engineer","order":2,"desc":"","company":"","company_id":-1,"company_size":0}]",0
            "[{"title":"verantwoordelijk persoon A. I.","order":1,"desc":"","company":"","company_id":-1,
            "company_size":0},{"title":"GDP responsible person","order":2,"desc":"","company":"","company_id":-1,
            "company_size":0}]",0
            @endcode
    -# Make a note of the expected load on the server - for example 2 requests per second.

    -# Run locust,
        - Set the following parameters:
            - --host - Host to load test in the following format: http://example.com
            - --users - Number of concurrent Locust users, we mostly test on 50, 100 and 200 users.
            - --spawn-rate - The rate per second in which users are spawned
        - locust -f locustfile.py --host={your-host} --users={number-of-users} --spawn-rate={your-spawn-rate}

    -# Access locust web-interface (gets created when locust runs), for example:
        - http://0.0.0.0:8089
        - Locus will display our selected parameters (modify if required).
    -# Start process:
        - Click 'Start Swarming' button.
    -# Statistics will show on screen:
        - Monitor the RPS (Results per second).
        - Make sure that the server can handle the expected load (i.e ~2 requests per second)
        - Take note of the maximum RPS that the server can handle before failures start to build up.
        If they do not match the expected results, consider modifying machine resources.
    -# Stop the test.
    -# Failures tab:
        - List of errors.
    -# Charts tab:
        - Shows the course of the test.
        - Download a pdf report and attached to release notes or PR notes.
    -# Things to keep in mind:
        - PC running the test - can affect the results.
        - Test for every new PR to see if results compromised.

    """

    def __init__(self, *args, **kwargs):
        """! payloadUser Initializer.

        Loads sample dataset from sample.csv file. """

        ##
        # @hidecallgraph @hidecallergraph
        super().__init__(*args, **kwargs)
        ## Sample dataset
        self.df = pd.read_csv("sample.csv", sep='\t')
        self.df.replace(np.nan, '', regex=True)

    def get_random_row(self):
        """Returns a random row from the sample dataset"""
        s = self.df.sample().to_dict('list')
        d = dict((k.lower(), v[0]) for k, v in s.items())
        return d

    @task
    def get_diagnosis_with_valid_payload(self):
        """The main method for stress testing, wrapped with locust @task decorator,
        it runs in a loop handled by locust."""
        headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
        payload = self.get_random_row()
        self.client.post("/predict", json=payload, headers=headers)
