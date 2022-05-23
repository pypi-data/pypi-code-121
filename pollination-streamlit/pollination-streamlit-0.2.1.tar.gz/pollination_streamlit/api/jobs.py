import pathlib
import typing as t
from io import BytesIO

from queenbee.job import Job as QbJob

from ._base import APIBase


class JobsAPI(APIBase):

    def upload_artifact(self, owner: str, project: str, filepath: pathlib.Path, artifactpath: pathlib.Path) -> str:
        fp_string = filepath.as_posix()
        ap_string = artifactpath.as_posix()

        res = self.client.post(
            f'/projects/{owner}/{project}/artifacts',
            json={'key': ap_string}
        )

        files = {'file': (fp_string, open(fp_string, 'rb'))}
        res = self.client.session.post(
            url=res['url'], data=res['fields'], files=files)
        res.raise_for_status()

        return ap_string

    def create_job(self, owner: str, project: str, job: QbJob) -> str:
        res = self.client.post(
            path=f'/projects/{owner}/{project}/jobs',
            json=job.dict()
        )
        return res['id']

    def get_job(self, owner: str, project: str, job_id: str) -> t.List[dict]:
        return self.client.get(
            path=f'/projects/{owner}/{project}/jobs/{job_id}'
        )

    def get_job_artifact(self, owner: str, project: str, job_id: str, path: str) -> BytesIO:
        signed_url = self.client.get(
            path=f'/projects/{owner}/{project}/jobs/{job_id}/artifacts/download',
            params={'path': path}
        )
        return self.client.download_artifact(signed_url)

    def list_job_artifacts(self, owner: str, project: str, job_id: str, path: str = None) -> t.List[t.Dict[str, t.Any]]:
        return self.client.get(
            path=f'/projects/{owner}/{project}/jobs/{job_id}/artifacts',
            params={'path': path}
        )
