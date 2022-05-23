import typing as t
from io import BytesIO

from ._base import APIBase


class RunsAPI(APIBase):

    def _run_results_request(self, owner: str, project: str, job_id: str, page: int = 1) -> t.List[t.List[dict]]:
        res = self.client.get(
            path=f'/projects/{owner}/{project}/results',
            params={'job_id': job_id, 'page': page}
        )
        data = res.get('resources', {})
        next_page = res.get('next_page')
        if next_page is not None:
            data.extend(self._run_results_request(
                owner, project, job_id, next_page))
        return data

    def get_runs(self, owner: str, project: str, job_id: str) -> t.List[t.List[dict]]:
        return self._run_results_request(owner, project, job_id)

    def get_run(self, owner: str, project: str, run_id: str) -> t.List[dict]:
        return self.client.get(
            path=f'/projects/{owner}/{project}/runs/{run_id}'
        )

    def download_zipped_run_output(self, owner: str, project: str, run_id: str, output_name: str) -> BytesIO:
        signed_url = self.client.get(
            path=f'/projects/{owner}/{project}/runs/{run_id}/outputs/{output_name}',
        )
        return self.client.download_artifact(signed_url)
