# standard library (this section is auto-gen from isort; see .isort.cfg)
import json

# vendor (this section is auto-gen from isort; see .isort.cfg)
import base64
import io
import requests
import tempfile


class Consent:
    def __init__(self, host: str, port: int, api_key: str = None):
        self.url = f"http://{host}:{port}/v1/"
        self.api_key = api_key

    def _get(self, endpoint: str, params: dict = None) -> dict:
        resp = requests.get(f"{self.url}{endpoint}", params=params, headers=self._generate_header())
        return json.loads(resp.text)

    def _generate_header(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _handle_image(self, image) -> str:
        if isinstance(image, str):
            with open(image, "rb") as file:
                return base64.b64encode(file.read()).decode("ascii")
        elif isinstance(image, bytes):
            return base64.b64encode(image).decode("ascii")
        elif isinstance(image, (io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader)):
            return base64.b64encode(image.read()).decode("ascii")
        else:
            raise Exception("Image format is unsupported")

    def _paginate_get(self, endpoint: str) -> dict:
        token = ""
        while token is not None:
            resp = self._get(f"{endpoint}", params={"page_token": token})
            token = resp["data"]["next_page_token"]
            yield resp

    def _paginate_results(self, endpoint: str, res: dict) -> dict:
        yield res
        token = res["data"]["next_page_token"]
        while token is not None:
            id = res["id"]
            res = self._get(f"{endpoint}/{id}", params={"page_token": token})
            token = res["data"]["next_page_token"]
            yield res

    def _patch(self, endpoint: str, data: dict = None) -> dict:
        resp = requests.patch(f"{self.url}{endpoint}", data=data, headers=self._generate_header())
        return json.loads(resp.text)

    def _post(self, endpoint: str, json_data: dict = None, data: dict = None) -> dict:
        resp = requests.post(f"{self.url}{endpoint}", json=json_data, data=data, headers=self._generate_header())
        return json.loads(resp.text)

    def compare_images(self, image_a, image_b) -> dict:
        """
        Compares two images and returns the similarity

        :param image_a: Image a
        :type: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader
        :param image_b: Image b
        :type: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader

        :return: Dictionary
        :rtype: dict
        """
        image_a_base64 = self._handle_image(image_a)
        image_b_base64 = self._handle_image(image_b)
        return self._post("compare_images", data={"image_a": image_a_base64, "image_b": image_b_base64})

    def create_collection(self, collection_name: str) -> dict:
        """
        Create a new collection

        :param collection_name: Collection Name
        :type collection_name: str
        :return: Dictionary
        :rtype: dict
        """
        return self._post(f"collections", json_data={"collection_name": collection_name})

    def create_image(self, collection_name: str, image, image_metadata: json = None) -> dict:
        """Create an image

        :param collection_name: Collection Name
        :type collection_name: str
        :param image: Image
        :type image: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader
        :param image_metadata: Image metadata, defaults to None
        :type image_metadata: json, optional
        :return: Dictionary
        :rtype: dict
        """
        image_base64 = self._handle_image(image)
        return self._post(f"collections/{collection_name}/images", data={"image": image_base64, "image_metadata": image_metadata})

    def detect_image(self, image, all_faces: bool = False) -> dict:
        """Detect an image

        :param image: Image
        :type image: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader
        :param all_faces: Detect all faces, defaults to False
        :type all_faces: bool, optional
        :return: Dictionary
        :rtype: dict
        :yield: 10 results
        :rtype: Iterator[dict]
        """
        endpoint = "detect_image"
        image_base64 = self._handle_image(image)
        res = self._post(endpoint, data={"image": image_base64, "all_faces": all_faces})
        yield from self._paginate_results(endpoint, res)

    def embed_image(self, image, all_faces: bool = False) -> dict:
        """Embed an image

        :param image: Image
        :type image: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader
        :param all_faces: Detect all faces, defaults to False
        :type all_faces: bool, optional
        :return: Dictionary
        :rtype: dict
        :yield: 10 results
        :rtype: Iterator[dict]
        """
        endpoint = "embed_image"
        image_base64 = self._handle_image(image)
        res = self._post(endpoint, data={"image": image_base64, "all_faces": all_faces})
        yield from self._paginate_results(endpoint, res)

    def get_collection(self, collection_name: str) -> dict:
        """Returns a collection

        :param collection_name: Collection Name
        :type collection_name: str
        :return: Dictionary
        :rtype: dict
        """
        return self._get(f"collections/{collection_name}")

    def get_collections(self):
        """Returns all collections

        :yield: 10 results
        :rtype: Iterator[dict]
        """
        yield from self._paginate_get("collections")

    def search_embedding(self, collection_name: str, face_embeddings: list) -> dict:
        """_summary_

        :param collection_name: Collection Name
        :type collection_name: str
        :param face_embeddings: Face Embeddings
        :type face_embeddings: list
        :return: Dictionary
        :rtype: dict
        :yield: 10 results
        :rtype: Iterator[dict]
        """
        endpoint = f"collections/{collection_name}/search_embedding"
        res = self._post(endpoint, json_data={"face_embeddings": face_embeddings})
        yield from self._paginate_results(endpoint, res)

    def search_image(self, collection_name: str, image, all_faces: bool = False) -> dict:
        """_summary_

        :param collection_name: Collection Name
        :type collection_name: str
        :param image: Image
        :type image: str, bytes, io.BufferedRandom, tempfile._TemporaryFileWrapper, io.BytesIO, io.BufferedReader
        :param all_faces: Search all faces, defaults to False
        :type all_faces: bool, optional
        :return: Dictionary
        :rtype: dict
        :yield: 10 results
        :rtype: Iterator[dict]
        """
        endpoint = f"collections/{collection_name}/search"
        image_base64 = self._handle_image(image)
        res = self._post(endpoint, json_data={"image": image_base64, "all_faces": all_faces})
        yield from self._paginate_results(endpoint, res)

    def update_image(self, collection_name: str, image_id: str, image_metadata: json) -> dict:
        """Update the metadata on an imagine

        :param collection_name: Collection _name
        :type collection_name: str
        :param image_id: Image ID
        :type image_id: str
        :param image_metadata: Image Metadata
        :type image_metadata: json
        :return: Dictionary
        :rtype: dict
        """
        return self._patch(f"collections/{collection_name}/images/{image_id}", data={"image_metadata": image_metadata})
