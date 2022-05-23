from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase
import deeplabel.client


class Notebook(DeeplabelBase):
    notebook_id: str
    name: str
    content: str

    @classmethod
    def from_notebook_id(cls, notebook_id: str, client: "deeplabel.client.BaseClient") -> "Notebook":  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/notebooks", params={"notebookId": notebook_id})
        notebooks = resp.json()["data"]["notebooks"]
        if not len(notebooks):
            raise InvalidIdError(f"No notebook found for notebookId {notebook_id}")
        notebook: Notebook = cls(**notebooks[0], client=client)
        return notebook

    # def update(self, notebook_id: str, data: dict) -> dict:
    #     try:
    #         data["notebookId"] = notebook_id
    #         data["restriction"] = False
    #         res = requests.put(self.notebook_url,
    #                            json=data, headers=self.headers)
    #         notebook = res.json()["data"]
    #         return notebook
    #     except Exception as exc:
    #         print("update notebook failed", exc)
