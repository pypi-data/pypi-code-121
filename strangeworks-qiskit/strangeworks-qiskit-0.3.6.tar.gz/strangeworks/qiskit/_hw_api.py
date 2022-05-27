import uuid
from strangeworks import Client


class SWClient:
    def __init__(self, client: Client):
        self.__client = client
        self.__base_url = f"/qiskit"

    def get_backends(self):
        url = f"{self.__base_url}/backends"
        return self.__client.rest_client.get(url)

    def create_job(self, input, backend_name, **kwargs):
        # use a new result_id for each new job run
        strangeworks_result_id = (
            str(uuid.uuid4())
            if self.__client.result_id is None
            else self.__client.result_id
        )
        url = f"{self.__base_url}/create-job"
        circuit_type = type(input).__name__
        payload = {
            "input": input.to_dict(),
            "circuit_type": circuit_type,
            "backend_name": backend_name,
            "result_id": strangeworks_result_id,
        }
        payload.update(kwargs)
        account_slug = kwargs.get("account_slug", "")
        self.__client.rest_client.headers[
            "x-strangeworks-provider-account"
        ] = account_slug
        return self.__client.rest_client.post(url, json=payload)

    def cancel_job(self, job_id: str = "", result_id: str = None):
        url = f"{self.__base_url}/cancel-job"
        url += f"?&job_id={job_id}"
        if result_id is not None:
            url += f"&result_id={result_id}"
        self.__client.rest_client.delete(url)

    def fetch_job(self, job_id):
        url = f"{self.__base_url}/fetch-job"
        url += f"?job_id={job_id}"
        return self.__client.rest_client.get(url)

    def fetch_job_status(self, job_id):
        url = f"{self.__base_url}/fetch-job-status"
        url += f"?job_id={job_id}"
        return self.__client.rest_client.get(url)

    def fetch_backend_status(self, account_slug, backend_name):
        if account_slug:
            self.__client.rest_client.headers[
                "x-strangeworks-provider-account"
            ] = account_slug
        url = f"{self.__base_url}/backend/{backend_name}/status"
        return self.__client.rest_client.get(url)

    def fetch_backend_properties(self, account_slug, backend_name):
        if account_slug:
            self.__client.rest_client.headers[
                "x-strangeworks-provider-account"
            ] = account_slug
        url = f"{self.__base_url}/backend/{backend_name}/properties"
        return self.__client.rest_client.get(url)
