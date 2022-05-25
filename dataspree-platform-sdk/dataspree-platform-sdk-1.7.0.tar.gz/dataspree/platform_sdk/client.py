#  Copyright 2022 Data Spree GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
import json
import logging
import math
import os
import sys
import threading
import datetime
from typing import Dict, Union, Optional, List, Tuple, Any

import msgpack
import requests as rq
from joblib import Parallel, delayed
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from urllib3 import Retry

from .http_token_authentication import HTTPTokenAuth
from .query import Condition, Conditions, Equal, GreaterThan, LessThan, Or

logger = logging.getLogger(__name__)


class Client:
    """Client for the Data Spree AI Platform.

    The platform client forms the interface to the AI platform and provides a variety of functions. For instance, it is
    possible download a whole dataset given its ID or create a new one and upload the corresponding dataset items.

    :param username: Platform username. Required for authentication.
    :param password: Platform password. Required for authentication.
    :param auth_token: Platform authentication token.
    :param http_retries: Number of HTTP retries before error is thrown.
    :param parallel_requests: Maximum number of parallel HTTP request.
    :param server_url: URL of the AI platform. Modify this parameter in case you use an on-premise installation.

    """

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, auth_token: Optional[str] = None,
                 http_retries: int = 10, parallel_requests: int = 16,
                 server_url: str = 'https://api.vision.data-spree.com/api', verify_ssl: bool = True,
                 verify_s3_ssl: bool = True):

        self.username = username
        self.password = password
        self.auth_token = auth_token

        self.auth = None
        if auth_token:
            self.auth = HTTPTokenAuth(auth_token)
        elif username is not None and password is not None:
            self.auth = HTTPBasicAuth(username, password)

        if self.auth is None:
            raise ValueError('Username and password or authentication token must be provided.')

        self.http_retries = http_retries
        self.server_url = server_url
        self.parallel_requests = parallel_requests
        self.http = rq.Session()
        if not verify_ssl:
            self.http.verify = False
        self.s3_http = rq.Session()
        if not verify_s3_ssl:
            self.s3_http.verify = False
        self.http.auth = self.auth
        retry = Retry(total=http_retries, connect=1, backoff_factor=0.5,
                      status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(pool_maxsize=self.parallel_requests, max_retries=retry)

        self.http.mount('http://', adapter)
        self.http.mount('https://', adapter)

    def __reduce__(self):
        return (Client, (self.username,
                         self.password,
                         self.auth_token,
                         self.http_retries,
                         self.parallel_requests,
                         self.server_url,
                         self.http.verify,
                         self.s3_http.verify,))

    @staticmethod
    def get_dataset_item_date_format_string() -> str:
        return '%Y-%m-%dT%H:%M:%S.%fZ'

    @staticmethod
    def get_dataset_item_date_format_string_short() -> str:
        return '%Y-%m-%dT%H:%M:%SZ'

    @staticmethod
    def parse_dataset_item_date(date_string: Optional[str]) -> Optional[datetime.datetime]:
        if date_string is None:
            return None

        try:
            return datetime.datetime.fromisoformat(date_string)
        except (TypeError, ValueError, AttributeError):
            pass

        try:
            return datetime.datetime.strptime(date_string, Client.get_dataset_item_date_format_string())
        except (TypeError, ValueError, AttributeError):
            pass

        try:
            return datetime.datetime.strptime(date_string, Client.get_dataset_item_date_format_string_short())
        except (TypeError, ValueError, AttributeError):
            pass

        return None

    @staticmethod
    def dataspree_temp_dir(*sub_dirs: str) -> str:
        temp_dir = os.path.join(Client.dataspree_dir(), 'temp', *sub_dirs)
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    @staticmethod
    def dataspree_dir():
        base_dir = os.path.expanduser('~')
        dir = os.path.join(base_dir, '.dataspree')
        if sys.platform in ['win32', 'cygwin'] and os.getlogin() == 'SYSTEM':
            # on windows in case the 'user' is SYSTEM, e.g. when started as a windows service
            dir = os.path.join(os.getenv('ALLUSERSPROFILE'), 'Data Spree', 'AI Platform')
        try:
            os.makedirs(dir)
        except FileExistsError:
            pass
        return dir

    def server_status(self):
        response = self.http.get(f'{self.server_url}/server')
        response.raise_for_status()
        return response.json()

    def create_dataset(self,
                       dataset_name,
                       classification_class_label_ids=None,
                       key_point_ids=None,
                       roi_classification_class_label_ids=None,
                       roi_key_point_ids=None,
                       object_detection_class_label_ids=None,
                       object_detection_key_point_ids=None,
                       object_detection_masks=False,
                       semantic_segmentation_class_label_ids=None):
        """Create a new dataset.

        :param dataset_name: Name of the new dataset.
        :param classification_class_label_ids: IDs of the class labels for the classification of the whole image.
        :param key_point_ids: IDs of the key points that can be annotated for the whole image.
        :param roi_classification_class_label_ids: IDs of the class label for the classification of regions of interest.
        :param roi_key_point_ids: IDs of the key points that can be annotated for each region of interest.
        :param object_detection_class_label_ids: IDs of the class labels for object annotations.
        :param object_detection_key_point_ids: IDs of the key points that can be annotated for individual objects.
        :param object_detection_masks: Set to True if it should be possible to annotate individual objects with segmentation masks.
        :param semantic_segmentation_class_label_ids: IDs of the class labels for annotating each pixel with a class label (semantic segmentation of the image).
        :return: ID of the newly created dataset or -1 if dataset creation fails.
        """

        dataset = {
            'name': dataset_name,
            'classification': classification_class_label_ids is not None,
            'key_points': key_point_ids is not None,
            'roi_classification': roi_classification_class_label_ids is not None,
            'roi_key_points': roi_key_point_ids is not None,
            'object_detection': object_detection_class_label_ids is not None,
            'object_detection_key_points': object_detection_key_point_ids is not None,
            'object_detection_mask': object_detection_masks,
            'semantic_segmentation': semantic_segmentation_class_label_ids is not None,
        }

        if dataset['classification']:
            dataset['classification_class_label_ids'] = classification_class_label_ids

        if dataset['key_points']:
            dataset['key_point_ids'] = key_point_ids

        if dataset['roi_classification']:
            dataset['roi_classification_class_label_ids'] = roi_classification_class_label_ids

        if dataset['roi_key_points']:
            dataset['roi_key_point_ids'] = roi_key_point_ids

        if dataset['object_detection']:
            dataset['object_detection_class_label_ids'] = object_detection_class_label_ids,

        if dataset['object_detection_key_points']:
            dataset['object_detection_key_point_ids'] = object_detection_key_point_ids

        if dataset['semantic_segmentation']:
            dataset['semantic_segmentation_class_label_ids'] = semantic_segmentation_class_label_ids

        try:
            response = self.http.post(self.server_url + '/datasets/', data=dataset)
            response.raise_for_status()
            data = response.json()
            return data['id']
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return -1

    def get_dataset(self, dataset_id: int):
        """Get information about a dataset.

        Example:
            >>> {
            >>>    'id': 46,
            >>>    'total_items': 104,
            >>>    'uploaded_items': 0,
            >>>    'annotated_items': 0,
            >>>    'reviewed_items': 104,
            >>>    'ignored_items': 0,
            >>>    'created_by': {'id': 1, 'username': 'admin'},
            >>>    'name': 'Traffic II',
            >>>    'created_date': '2019-07-29T10:06:22.454871Z',
            >>>    'updated_date': '2019-07-29T10:06:22.454914Z',
            >>>    'classification': False,
            >>>    'key_points': False,
            >>>    'roi_classification': False,
            >>>    'roi_key_points': False,
            >>>    'object_detection': True,
            >>>    'object_detection_key_points': False,
            >>>    'object_detection_mask': False,
            >>>    'semantic_segmentation': False,
            >>>    'classification_class_labels': [],
            >>>    'key_point_names': [],
            >>>    'roi_classification_class_labels': [],
            >>>    'roi_key_points_names': [],
            >>>    'object_detection_class_labels': [{'id': 4, 'name': 'car'},
            >>>     {'id': 6, 'name': 'truck'},
            >>>     {'id': 7, 'name': 'pedestrian'},
            >>>     {'id': 9, 'name': 'cyclist'},
            >>>     {'id': 41, 'name': 'traffic light'},
            >>>     {'id': 119, 'name': 'traffic sign'}],
            >>>    'object_detection_key_point_names': [],
            >>>    'semantic_segmentation_class_labels': []
            >>> }

        :param dataset_id: ID of the dataset to receive information.
        :return: Dictionary containing information of the requested datatset.
        """
        try:
            response = self.http.get(self.server_url + '/datasets/{}/'.format(dataset_id))
            if response.status_code == 200:
                dataset = response.json()
                return dataset
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_dataset_items(self, dataset_id: Optional[int] = None,
                          class_id: Optional[int] = None,
                          subset_id: Optional[Union[str, int]] = None,
                          created_date_since: Optional[Union[str, datetime.datetime]] = None,
                          created_date_until: Optional[Union[str, datetime.datetime]] = None,
                          status: Optional[List[str]] = None,
                          query_expression: Optional[Condition] = None,
                          free_query_str: Optional[str] = None, *, return_query: bool = False,
                          max_items: Optional[int] = None) \
            -> Union[Optional[List[Dict]], Tuple[Optional[List[Dict]], str]]:
        """
        Return all dataset items that match the filter compiled from this functions' parameters.

        :param dataset_id:          Identifier of the dataset whose content be downloaded.
        :param data_subsets_id:     Identifier of the subset whose content be downloaded or None if you don't want
                                    to filter by subset. "null()" if you would like to receive every dataset item
                                    that is not part of any subset.
        :param class_id:            Set this to only download items of the specified class_id
        :param created_date_since:  Set this to filter out dataset items created at created_date_since or earlier.
        :param created_date_until:  Set this to filter out dataset items created at created_date_until or later.
        :param status:              If not set, return the dataset items irrespective of their status.
                                    Otherwise, add an OR filter to the query on the content of the status list.
        :param query_expression:    Set this field to supply a custom query expression to the query.
        :param free_query_str:      Set this field to supply a custom query expression as a string to the query.
        :param return_quer:         Return first query if enabled as second return argument
        :return:                    A list of dataset items or None, if a problem occurred.
        """
        # dataset = self.get_dataset(dataset_id)
        # if dataset is None:
        #     return None

        items_per_request: int = min(5000, max_items) if max_items is not None else 5000

        def format_time(t: Optional[Union[str, datetime.datetime]]) -> Optional[str]:
            return t if t is None or type(t) == str else t.isoformat()

        # Compile conditions
        condition_str: str = Conditions.create(Equal(var='class', val=class_id),
                                               Equal(var='dataset__id', val=dataset_id),
                                               Equal(var='page_size', val=items_per_request),
                                               Equal(var='data_subsets__id', val=subset_id),
                                               GreaterThan(var='created_date', val=format_time(created_date_since)),
                                               LessThan(var='created_date', val=format_time(created_date_until)),
                                               Or(*(Equal(var='status', val=s) for s in status)) if status else None,
                                               query_expression, exclude_empty=True, do_url_escape=True)

        if free_query_str:
            if not free_query_str.startswith('&'):
                free_query_str = f'&{free_query_str}'
            condition_str += free_query_str

        # Compile URL
        url: Optional[str] = f'{self.server_url}/dataset-items/?{condition_str}'
        first_url: str = url

        all_items: List[Dict] = list()
        while url is not None:

            logger.debug(f'Get dataset items from "{url}"')
            try:
                response: rq.models.Response = self.http.get(url)
                response.raise_for_status()
                response_json = response.json()

                items: Optional[List[Dict]] = response_json.get('results')
                url = response_json.get('next')

                if not items:
                    break

                all_items.extend(items)

                if max_items is not None and len(all_items) >= max_items:
                    break

            except rq.exceptions.RequestException as e:
                logger.error(e)

                if return_query:
                    return None, first_url
                return None

        if return_query:
            return all_items, first_url
        return all_items

    def delete_dataset(self, dataset_id):
        """Delete a dataset.

        :param dataset_id: id of the dataset
        :return: 'True' if success else 'False'
        """

        try:
            response = self.http.delete(f'{self.server_url}/datasets/{dataset_id}')
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return False

    def download_dataset(self, directory, dataset_id, n_items=-1, accepted_status=None):
        """Download a dataset from data spree vision platform.

        :param directory:  Directory to download dataset items (images and annotations)
        :param dataset_id: ID of the dataset that should be downloaded.
        :param n_items: Maximum number of items to download. Set to -1 to download all items.
        :param accepted_status: Download only items with the provided status (list of strings). Set to None to accept all status.
        """

        logger.info('Download dataset. Dataset ID: {}'.format(dataset_id))

        # download list of dataset items
        dataset_items = self.get_dataset_items(dataset_id)
        if dataset_items is None:
            logger.error('Could not get list of dataset items for dataset with ID {}'.format(dataset_id))

        # create output directories
        try:
            os.makedirs(directory)
        except FileExistsError:
            pass
        try:
            os.makedirs(os.path.join(directory, 'images'))
        except FileExistsError:
            pass
        image_dir = os.path.join(directory, 'images')
        try:
            os.makedirs(os.path.join(directory, 'annotations'))
        except FileExistsError:
            pass

        annotation_dir = os.path.join(directory, 'annotations')

        if n_items != -1:
            dataset_items = dataset_items[:n_items]

        # use only those dataset items from the list, that are not yet downloaded
        new_dataset_items = []
        for item in dataset_items:
            image_name = item['name'].split('/')[-1]
            image_name = '{}_{}_{}'.format(dataset_id, item['id'], image_name)
            image_file_path = os.path.join(image_dir, image_name)

            annotation_file_name = os.path.splitext(image_name)[0] + '.json'
            annotation_file_path = os.path.join(annotation_dir, annotation_file_name)

            if not os.path.exists(image_file_path) or not os.path.exists(annotation_file_path):
                new_dataset_items.append(item)

        logger.info(
            '{} items available in dataset {}. {} already downloaded'.format(len(dataset_items), dataset_id,
                                                                             len(dataset_items) - len(
                                                                                 new_dataset_items)))

        if len(new_dataset_items) != 0:
            with open(os.path.join(directory, 'items.json'), 'w') as f:
                json.dump(dataset_items, f, indent=2)

            if self.parallel_requests > 1:
                Parallel(n_jobs=self.parallel_requests, prefer='threads')(
                    delayed(self.download_dataset_item)(item['id'], image_dir, annotation_dir, accepted_status)
                    for item in tqdm(new_dataset_items))
            else:
                for item in tqdm(new_dataset_items):
                    self.download_dataset_item(item['id'], image_dir, annotation_dir, accepted_status)

        logger.info('Download completed. (dataset ID: {})'.format(dataset_id))

    def create_data_subset(self, subset_name, dataset_id, description=''):
        """Add a subset to an existing dataset.

        :param subset_name: name of the subset
        :param dataset_id: id of the parent dataset
        :param description: string description
        :return: newly created subset or 'None' if subset creation fails.
        """

        subset_dict = {
            'name': subset_name,
            'description': description,
            'dataset': dataset_id,
        }

        try:
            response = self.http.post(f'{self.server_url}/data-subsets/', data=subset_dict)
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_data_subset(self, subset_id):
        """Get information about a dataset.

        Example:
            >>> {
            >>>    'id': 46,
            >>>    'total_items': 104,
            >>>    'name': 'Traffic II',
            >>>    'description': str,
            >>>    'dataset': 24,
            >>> }

        :param subset_id: ID of the subset to receive information.
        :return: Dictionary containing information of the requested subset.
        """
        try:
            response = self.http.get(self.server_url + '/data-subsets/{}/'.format(subset_id))
            if response.status_code == 200:
                subset = response.json()
                return subset
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_data_subset_items(self, subset_id) -> List[Dict]:
        """
        Get all subset items for the subset given by its ID.
        :see get_dataset_items
        """
        return self.get_dataset_items(subset_id=subset_id)

    def delete_data_subset(self, subset_id):
        """Delete a subset to an existing dataset.

        :param subset_id: id of the subset
        :return: 'True' if success else 'False'
        """

        try:
            response = self.http.delete(f'{self.server_url}/data-subsets/{subset_id}')
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return False

    def create_dataset_item(self,
                            image_file,
                            dataset_id,
                            annotations=None,
                            image_file_name=None,
                            status=None,
                            created_date=None):
        """Create a new dataset item including the image and the associated annotations.

        :param image_file: File path to the image or image bytes to upload that belongs to the new item.
        :param dataset_id: The new item will be created for the provided dataset ID.
        :param annotations: Dictionary of the annotations
        :param image_file_name: Name of the image that should be uploaded. Set to `None` to use the file name derived from `image_file` if provided as a path, otherwise a name is required.
        :param status: Status of the newly created item. Should be one of `['uploaded', 'annotated', 'reviewed', 'ignored']`. Set to `None` to automatically set to `reviewed` or `uploaded` in case the annotations are empty.
        :param created_date: Creation date and time as datetime object or number (seconds, POSIX timestamp) of the dataset item (upload time is used if not provided).
        :return: ID of the newly created item or `-1` in case it could not be created.
        """

        if annotations is None:
            annotations = {}
        if isinstance(image_file, bytes):
            if not isinstance(image_file_name, str):
                raise ValueError('If an image is passed in bytes form, an "image_file_name" (str) has to be provided.')
            files = {
                'data': (image_file_name, image_file)
            }
        else:
            if image_file_name is None:
                image_file_name = os.path.split(image_file)[-1]

            files = {
                'data': (image_file_name, open(image_file, 'rb'))
            }

        if status is None:
            status = 'reviewed' if annotations else 'uploaded'

        dataset_item = {
            'dataset_id': dataset_id,
            'annotations': json.dumps(annotations),
            'status': status
        }

        if created_date is not None:
            if type(created_date) in (int, float):
                created_date_dt = datetime.fromtimestamp(created_date)
            else:
                created_date_dt = created_date

            if type(created_date_dt) != datetime.datetime:
                raise ValueError('"created_date" must be a datetime object or a number')

            created_date_str = created_date_dt.isoformat()
            dataset_item['created_date'] = created_date_str

        try:
            response = self.http.post(self.server_url + '/dataset-items/', data=dataset_item, files=files)
            response.raise_for_status()
            data = response.json()
            return data['id']
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return -1

    def get_dataset_item(self, item_id):
        """Get a dataset item given its ID.
        :param item_id: ID of the item to be retrieved.
        :return: Dictionary containing the item details (e.g., ID, name, status).
        >>> {
        >>>     "id": 137594,
        >>>     "dataset_id": 46,
        >>>     "name": "dataset/46/frame_1563809032073.png",
        >>>     "status": "reviewed",
        >>>     "thumbnail": "https://...",
        >>>     "data": "https://...",
        >>>     "annotations": {
        >>>         "classes": [],
        >>>         "objects": []
        >>>     }
        >>> }

        """
        # load item details
        try:
            response = self.http.get(self.server_url + '/dataset-items/{}'.format(item_id))
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return None

        item_details = json.loads(response.content)

        return item_details

    def delete_dataset_item(self, item_id):
        """Delete a dataset item.

        :param item_id: id of the dataset item
        :return: 'True' if success else 'False'
        """

        try:
            response = self.http.delete(f'{self.server_url}/dataset-items/{item_id}')
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return False

    def download_dataset_item(self, item_id, image_dir: Optional[str] = None,
                              metainformation_directory: Optional[str] = None,
                              accepted_status=None, return_item: bool = False):
        """Download a dataset item into the specified directories (image and metainformation).

        :param item_id: ID of the dataset item to download.
        :param image_dir: Output directory for the image.
        :param metainformation_directory: Output directory for the metainformation.
        :param accepted_status: List of accepted status. If the item status is not in this list, it will not be downloaded.
        :return:
        """
        if image_dir is None and metainformation_directory is None and not return_item:
            raise ValueError('arguments not correct')

        # load item details
        try:
            response = self.http.get(self.server_url + '/dataset-items/{}'.format(item_id))
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return None

        item_details = json.loads(response.content)
        if accepted_status is not None:
            if item_details['status'] not in accepted_status:
                return None
        image_url = item_details['data']

        # download image
        try:
            response = self.s3_http.get(image_url, stream=True)
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)

        item_id = item_details['id']
        dataset_id = item_details['dataset']
        item_name = item_details['name'].split('/')[-1]
        item_name = '{}_{}_{}'.format(dataset_id, item_id, item_name)

        image_bytes: Optional[bytes] = response.content
        if image_bytes is None:
            image_bytes = bytes()
            for chunk in response.iter_content(4096):
                image_bytes += chunk

        if image_dir:
            try:
                os.makedirs(image_dir)
            except FileExistsError:
                pass
            image_file_path = os.path.join(image_dir, item_name)

            with open(image_file_path, 'wb') as f:
                f.write(image_bytes)

        if metainformation_directory:
            os.makedirs(metainformation_directory, exist_ok=True)

            # write annotations to file
            details = dict(item_details)

            # remove unimportant clutter.
            for key in ('data', 'thumbnail'):
                if key in details:
                    del details[key]

            metainformation_file_name = os.path.splitext(item_name)[0] + '.json'
            metainformation_path = os.path.join(metainformation_directory, metainformation_file_name)
            with open(metainformation_path, 'w') as f:
                json.dump(details, f, indent=2)

        if return_item:
            item_details['image'] = image_bytes
            return item_details

        return None

    def add_dataset_items_to_subset(self, item_ids, subset_id):
        """Add an existing dataset item to a subset.

        :param item_ids: List of item IDs or a single item ID to be added
        :param subset_id: ID of target subset
        :return: 'True' if success, else 'False'
        """
        if not isinstance(item_ids, list):
            if isinstance(item_ids, int):
                item_ids = [item_ids]
            else:
                raise ValueError('Item IDs has to be a list of integers or an integer')

        items = {
            'items': item_ids
        }

        try:
            response = self.http.post(f'{self.server_url}/data-subsets/{subset_id}/items/', json=items)
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return False

    def remove_dataset_items_from_subset(self, item_ids, subset_id):
        """Remove a dataset item from a subset.

        :param item_ids: List of item IDs or a single item ID to be removed
        :param subset_id: ID of target subset
        :return: 'True' if success, else 'False'
        """
        if not isinstance(item_ids, list):
            if isinstance(item_ids, int):
                item_ids = [item_ids]
            else:
                raise ValueError('Item IDs has to be a list of integers or an integer')

        items = {
            'items': item_ids
        }

        try:
            response = self.http.post(f'{self.server_url}/data-subsets/{subset_id}/remove_items/', json=items)
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return False

    def get_model(self, model_id):
        """Get information about a model.

        Example:
            >>> {
            >>>     'id': 41,
            >>>     'created_by': {'id': 1, 'username': 'admin'},
            >>>     'worker_id': None,
            >>>     'pretrained_checkpoint_id': None,
            >>>     'name': 'SSD MobileNet V2 & MSF 300x300',
            >>>     'created_date': '2019-07-01T10:02:15.856145Z',
            >>>     'updated_date': '2019-07-29T13:19:32.190259Z',
            >>>     'network_type': 'object_detection',
            >>>     'status': 'open',
            >>>     'progress': 0.0,
            >>>     'model_data': None,
            >>>     'inference_data': None,
            >>>     'network_config_option': 1,
            >>>     'datasets': [7]
            >>> }

        :param model_id: ID of the model to receive information.
        :return: Dictionary containing information of the requested model.
        """

        try:
            response = self.http.get(self.server_url + '/models/{}/'.format(model_id))
            if response.status_code == 200:
                model = response.json()
                return model
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_model_class_labels(self, model_id):
        """Get all class labels for object detection of a model.

        Example:
            >>> [{'id': 4, 'name': 'car'},
            >>>  {'id': 5, 'name': 'van'},
            >>>  {'id': 6, 'name': 'truck'},
            >>>  {'id': 7, 'name': 'pedestrian'},
            >>>  {'id': 8, 'name': 'person_sitting'},
            >>>  {'id': 9, 'name': 'cyclist'},
            >>>  {'id': 10, 'name': 'tram'}]

        :param model_id: ID of the model to receive the class labels.
        :return: List of class labels (ID, name).
        """

        # TODO: Once the API endpoint is re-activated, change back to the old api call

        try:
            # response = self.http.get(self.server_url + '/models/{}/class_labels/'.format(model_id))
            # if response.status_code == 200:
            #     model = response.json()
            #     return model

            response = self.http.get(self.server_url + '/models/{}/'.format(model_id))
            if response.status_code == 200:
                model = response.json()
            else:
                return None

            all_class_labels: List[Dict] = self.get_class_labels()
            filtered_class_labels = [i for i in all_class_labels if i['id'] in model.get('class_labels')]
            return filtered_class_labels
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_model_parameters(self, model_id):
        """Get the parameters of a model.

        Example:
            >>> {
            >>>     'augmentation': {'horizontal_flip': {'probability': 0.5},
            >>>                      'random_scale_crop': {'aspect_ratio_max': 2,
            >>>                                            'aspect_ratio_min': 0.5,
            >>>                                            'probability': 0.8,
            >>>                                            'scaling_factor_max': 1,
            >>>                                            'scaling_factor_min': 0.5}},
            >>>     'dataset': {'input_height': 300, 'input_width': 300, 'training_split': 0.98},
            >>>     'detection': {'anchors': {'parameters': [...], 'position_offset': False},
            >>>                   'matching': {'threshold': 0.5},
            >>>                   'network': 'mobilenet_v2_msf'},
            >>>     'evaluation': {'interval': 500},
            >>>     'learning_rate': {'initial': 0.001, 'selection': 'constant'},
            >>>     'optimizer': {'amsgrad': False,
            >>>                   'beta1': 0.9,
            >>>                   'beta2': 0.999,
            >>>                   'epsilon': 1e-08,
            >>>                   'selection': 'adam',
            >>>                   'weight_decay': 4e-05},
            >>>     'training': {'batch_size': 96, 'checkpoints': {'interval': 100}}
            >>> }

        :param model_id: ID of the model to receive the parameters.
        :return: Dictionary containing all model parameters.
        """

        try:
            response = self.http.get(self.server_url + '/models/{}/parameters/'.format(model_id))
            if response.status_code == 200:
                model = response.json()
                return model
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_model_checkpoints(self, model_id):
        """Get information about all checkpoints of a model.

        Example:
            >>> [{'checkpoint_file': '...',
            >>>  'created_date': '2019-07-22T23:02:19.362520Z',
            >>>  'id': 5,
            >>>  'iteration': 38700,
            >>>  'network_model': 59,
            >>>  'updated_date': '2019-07-27T13:24:42.951453Z'}]

        :param model_id: ID of the model to receive the checkpoints.
        :return: List with checkpoints.
        """
        try:
            response = self.http.get(self.server_url + '/models/{}/checkpoints/'.format(model_id))
            if response.status_code == 200:
                checkpoints = response.json()
                return checkpoints
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return []

    def get_cloud_deployment(self, id):
        """Get information about a cloud deployment.

        Example:
            >>> {
            >>>     'id': 1,
            >>>     'name': 'Deployment Example',
            >>>     'last_online': '2019-12-12T14:00:00Z',
            >>>     'created_date': '2019-12-12T13:30:00.00Z',
            >>>     'updated_date': '2019-12-12T13:30:00.00Z',
            >>>     'parameters': {},
            >>>     'network_model': 123
            >>> }

        :param id: ID of the cloud deployment to receive information.
        :return: Dictionary containing information of the requested cloud deployment.
        """

        try:
            response = self.http.get(self.server_url + '/cloud-deployments/{}/'.format(id))
            if response.status_code == 200:
                return response.json()
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def download_latest_model_checkpoint(self, model_id, output_file_path):
        """Download the latest checkpoint of the given model and write it to the given `output_file_path`.

        :param model_id: ID of the model whose latest checkpoint is download.
        :param output_file_path: Output file path (no directory!).
        :return: Information about the latest checkpoint or `None` if no checkpoint is available or an error occurred.
        """
        checkpoints = self.get_model_checkpoints(model_id)

        if len(checkpoints) == 0:
            return None

        latest_checkpoint = checkpoints[-1]
        if latest_checkpoint['checkpoint_file'] is None:
            return None

        try:
            response = self.s3_http.get(latest_checkpoint['checkpoint_file'], stream=True)
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return None

        with open(output_file_path, 'wb') as f:
            for chunk in response.iter_content(4096):
                f.write(chunk)
        return latest_checkpoint

    def download_model_checkpoint(self, checkpoint_id, output_file_path):
        """Download a model checkpoint given by the checkpoint ID.

        :param checkpoint_id: ID of the checkpoint to download.
        :param output_file_path:  Output file path (no directory!).
        :return: Information about the downloaded checkpoint or `None` if no checkpoint is available or an error occurred.
        """
        logger.info('Download model checkpoint with ID: {}'.format(checkpoint_id))

        try:
            response = self.http.get(self.server_url + '/model-checkpoints/' + str(checkpoint_id))
            response.raise_for_status()
            checkpoint = response.json()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return None

        if checkpoint is None:
            return None

        try:
            response = self.s3_http.get(checkpoint['checkpoint_file'], stream=True)
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return None

        with open(output_file_path, 'wb') as f:
            for chunk in response.iter_content(4096):
                f.write(chunk)

        logger.info('Downloaded model checkpoint with ID: {} to: {}'.format(checkpoint_id, output_file_path))

        return checkpoint

    def create_model_checkpoint(self, model_id, iteration):
        """Create a new checkpoint for a model without uploading the checkpoint file.

        :param model_id: ID of the model for which a checkpoint is created.
        :param iteration: Training iteration of the checkpoint.
        :return: Newly created checkpoint or `None` in case it could not be created.
        """
        model_checkpoint = {
            'network_model': model_id,
            'iteration': iteration
        }

        try:
            response = self.http.post(self.server_url + '/model-checkpoints/', data=model_checkpoint)
            response.raise_for_status()
            return response.json()
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def upload_model_checkpoint(self, checkpoint_id, iteration, file_path):
        """Upload a model checkpoint.

        :param checkpoint_id: ID of the checkpoint to which the files are uploaded.
        :param iteration: Training iteration of the checkpoint.
        :param file_path: File path to the checkpoint file.
        :return: Updated checkpoint information or `None` in case of errors.
        """

        file_name = os.path.split(file_path)[-1]
        files = {
            'checkpoint_file': (file_name, open(file_path, 'rb'))
        }
        model_checkpoint = {
            'iteration': iteration
        }

        try:
            response = self.http.patch(self.server_url + '/model-checkpoints/{}/'.format(checkpoint_id),
                                       data=model_checkpoint, files=files)
            response.raise_for_status()
            logger.info('Model checkpoint uploaded: {}'.format(file_name))
            return response.json()
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def upload_latest_model_checkpoint_async(self, model_id, iteration, file_path):
        """Asynchronous update of the latest model checkpoint (largest iteration) including uploading a new checkpoint file.

        :param model_id: ID of the model for which the latest checkpoint is updated.
        :param iteration: Training iteration of the checkpoint.
        :param file_path: File path to the checkpoint file.
        """
        threading.Thread(target=self.upload_latest_model_checkpoint, args=(model_id, iteration, file_path)).start()

    def upload_latest_model_checkpoint(self, model_id, iteration, file_path):
        """Update of the latest model checkpoint (largest iteration) including uploading a new checkpoint file.

        :param model_id: ID of the model for which the latest checkpoint is updated.
        :param iteration: Training iteration of the checkpoint.
        :param file_path: File path to the checkpoint file.
        :return: Updated checkpoint information or `None` in case of errors.
        """
        checkpoints = self.get_model_checkpoints(model_id)

        if len(checkpoints) == 0:
            checkpoint = self.create_model_checkpoint(model_id, iteration)
        else:
            checkpoint = checkpoints[-1]

        if checkpoint is None:
            return None

        return self.upload_model_checkpoint(checkpoint['id'], iteration, file_path)

    def upload_inference_data_async(self, model_id, file_path):
        """Asynchronous upload of the inference data for the model given by its ID.

        :param model_id: ID of the model for which the latest checkpoint is updated.
        :param file_path: File path to the inference data file.
        """
        threading.Thread(target=self.upload_inference_data, args=(model_id, file_path)).start()

    def upload_inference_data(self, model_id, file_path):
        """Upload the inference data for the model given by its ID.

        :param model_id: ID of the model for which the inference data is updated.
        :param file_path: File path to the inference data file.
        :return: Updated model information or `None` in case of errors.
        """

        file_name = os.path.split(file_path)[-1]
        files = {'inference_data': (file_name, open(file_path, 'rb'))}

        try:
            response = self.http.patch(self.server_url + '/models/{}/'.format(model_id), files=files)
            response.raise_for_status()
            return True
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return False

    def upload_model_statistics_async(self, statistics, timestamp, iteration, model_id):
        """Asynchronous upload of model statistics (e.g., during training and evaluation) for a given model.

        :param statistics: Dictionary of model statistics that must be serializable as JSON.
        :param timestamp: Creation timestamp of the statistics.
        :param iteration: Iteration of the statistics.
        :param model_id: ID of the model the statistics belong to.
        """
        threading.Thread(target=self.upload_model_statistics, args=(statistics, timestamp, iteration, model_id)).start()

    def upload_model_statistics(self, statistics, timestamp, iteration, model_id):
        """Asynchronous upload of model statistics (e.g., during training and evaluation) for a given model.

        :param statistics: Dictionary of model statistics that must be serializable as JSON.
        :param timestamp: Creation timestamp of the statistics.
        :param iteration: Iteration of the statistics.
        :param model_id: ID of the model the statistics belong to.
        """

        logger.info('Upload model statistics')

        statistics_entry = {
            "timestamp": timestamp,
            "iteration": iteration,
            "statistics": json.dumps(statistics),
            "network_model": model_id
        }

        try:
            response = self.http.post(self.server_url + '/model-statistics/', data=statistics_entry)
            response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)
            return

        logger.info('Uploaded model statistics')

    def get_inference_results_by_dataset_item_id(self, dataset_id: Optional[int] = None, iteration: Optional[int] = None,
                                    network_model_id: Optional[int] = None, max_items: Optional[int] = None,
                                    page_size: int = 100, **kwargs: Any) -> Dict[int, Dict[str, Any]]:

        inference_results: List[Dict[str, Any]] = self.get_inference_results(
            dataset_id=dataset_id, iteration=iteration, network_model_id=network_model_id,
            max_items=max_items, page_size=page_size, **kwargs)

        return {ir['dataset_item']['id']: ir for ir in inference_results}

    def get_inference_results(self, dataset_id: Optional[int] = None, iteration: Optional[int] = None,
                              network_model_id: Optional[int] = None, max_items: Optional[int] = None,
                              page_size: int = 100, **kwargs: Any) -> List[Dict[str, Any]]:

        url: str = f'{self.server_url}/inference-results/'
        params: Dict[str, Any] = {'page_size': page_size}

        if dataset_id is not None:
            params['dataset_item__dataset__id'] = dataset_id

        if iteration is not None:
            params['iteration'] = iteration

        if iteration is not None:
            params['network_model_id'] = network_model_id

        params.update(kwargs)

        all_inference_results: List[Dict[str, Any]] = list()
        while url is not None:

            logger.debug(f'Get dataset items from "{url}"')
            response: rq.models.Response = self.http.get(url, params=params)
            response.raise_for_status()
            response_json = response.json()

            inference_results: Optional[List[Dict]] = response_json.get('results')
            url = response_json.get('next')
            params = None

            if not inference_results:
                break

            all_inference_results.extend(inference_results)

            if max_items is not None and len(all_inference_results) >= max_items:
                break

        return all_inference_results

    def upload_inference_results_async(self, results, timestamp, iteration, model_id):
        """Asynchronous upload of inference results (e.g., during evaluation) for a given model.

        :param results: List of results. See :func:`~platform_sdk.Client.upload_inference_results` for details.
        :param timestamp: Creation timestamp of the inference results.
        :param iteration: Iteration of the inference results.
        :param model_id: ID of the model the inference results belong to.
        """
        threading.Thread(target=self.upload_inference_results,
                         args=(results, timestamp, iteration, model_id)).start()

    def upload_inference_results(self, results, timestamp, iteration, model_id, *args):
        """Upload of inference results (e.g., during evaluation) for a given model.

        :param results: List of results.

        Example:
        >>> [
        >>>     {
        >>>         'dataset_item': 42,             # ID of the dataset item the result belongs to
        >>>         'classification': {
        >>>             'classes': [],              # list of platform class IDs (for classification)
        >>>             'class_confidences': [...]  # list containing class confidences (ordered according to 'classes')
        >>>         },
        >>>         'detection': {
        >>>             'boxes': [...]              # list of arrays representing the box coordinates and positions [x, y, width, height, orientation (optional)]
        >>>                                         # x, y, width, and height must be scaled to the interval [0, 1] (the point (1, 1) corresponds to the lower right corner)
        >>>             'classes': [...]            # list of platform class IDs (for detection)
        >>>             'class_confidences': [...]  # 2-dimensional array containing class confidences (ordered according to 'classes') for each box
        >>>         }
        >>>     }
        >>> ]

        :param timestamp: Creation timestamp of the inference results.
        :param iteration: Iteration of the inference results.
        :param model_id: ID of the model the inference results belong to.
        """

        logger.info('Upload inference results')

        msg_bytes = io.BytesIO()

        # add meta data
        msg_bytes.write(msgpack.packb(dict(timestamp=timestamp,
                                           iteration=iteration,
                                           model_id=model_id,
                                           results=len(results))))

        for i, result in enumerate(results):
            msg_bytes.write(msgpack.packb(result))

        response = self.http.post(f'{self.server_url}/bulk-data/',
                                  data=dict(data_type=0),
                                  files=dict(
                                      data=(f'inference-data-{timestamp}-{model_id}.msgpack', msg_bytes.getvalue())))
        response.raise_for_status()

    def get_class_labels(self):
        """Get a list of all available class labels of the platform sorted by name.

        Example:
        >>> [{'id': 37, 'name': 'airplane'},
        >>>  {'id': 78, 'name': 'apple'},
        >>>  {'id': 56, 'name': 'backpack'},
        >>>  {'id': 77, 'name': 'banana'},
        >>>  ...
        >>> ]

        :return: List of class labels or `None` in case of errors.
        """
        try:
            response = self.http.get(self.server_url + '/class-labels/')
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def create_class_label(self, name, public=False):
        """Create a new class label.

        :param name: Name of the new class label.
        :param public: Indicates if the label shall be globally accessible (by all users).
        :return: Newly created class label or `None` in case of errors.
        """

        class_label = {'name': name, 'public': False}

        try:
            response = self.http.post(self.server_url + '/class-labels/', data=class_label)
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_jobs(self, worker_id):
        """Get list of jobs for a particular worker.

        :param worker_id: Jobs of this worker are returned.
        :return: List of jobs or None.
        """

        try:
            response = self.http.get(self.server_url + '/workers/{}/jobs/'.format(worker_id))
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def get_job(self, job_id):
        """Get job details given its ID.

        :param job_id: Job details.
        :return: Job information or None.
        """

        try:
            response = self.http.get(self.server_url + '/jobs/{}/'.format(job_id))
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def update_job(self, job):
        """Update the job.

        :param job: Fields to update. Must include the job ID.
        :return: Job information or None.
        """

        job_id = job.get('id')
        if job_id is None:
            return None

        try:
            response = self.http.patch(self.server_url + '/jobs/{}/'.format(job_id), data=job)
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)

        return None

    def delete_job(self, job_id):
        """Delete a specific job.

        :param job_id: ID of the job that is to be removed.
        """

        try:
            response = self.http.delete(self.server_url + '/jobs/{}/'.format(job_id))
            if response.status_code == 404:
                logger.info('Job could not be deleted because it did not exist.')
            else:
                response.raise_for_status()
        except rq.exceptions.RequestException as e:
            logger.error(e)

    def create_labels_and_dataset(self, dataset_name, classification_class_labels=None,
                                  object_detection_class_labels=None):
        """Create a new dataset with all given class labels as detection class labels.

        A new dataset is created and those class labels that do not exist yet are automatically created as well.

        :param dataset_name: Name of the new dataset.
        :param object_detection_class_labels: List of strings of the object detection class labels for the new dataset.
        :return: ID of the newly created dataset or status code (see :func:`~platform_sdk.Client.create_dataset` for details).
        """

        # load list of all available class labels
        all_class_labels = self.get_class_labels()

        if all_class_labels is None:
            logger.error('Could not retrieve available class labels')
            return -1

        # dictionary containing mapping from class names to class label ids
        class_label_maps = {
            'classification': None,
            'object_detection': None
        }

        task_class_label_map = {}
        if classification_class_labels is not None:
            task_class_label_map['classification'] = classification_class_labels

        if object_detection_class_labels is not None:
            task_class_label_map['object_detection'] = object_detection_class_labels

        for task in task_class_label_map:

            class_label_names = task_class_label_map[task]
            class_label_map = {}

            # contains class names that do not yet exist on the platform
            new_class_labels = []

            # compare class labels of the dataset with existing class labels
            for class_label in class_label_names:
                is_new = True
                for cl in all_class_labels:
                    if class_label == cl['name']:
                        is_new = False
                        class_label_map[class_label] = cl['id']
                        break

                if is_new:
                    new_class_labels.append(class_label)

            # create new class labels
            for new_class_label in new_class_labels:
                id = self.create_class_label(new_class_label)
                if id is None:
                    logger.error('Could not create new class label ({}).'.format(new_class_label))
                    return -1
                class_label_map[new_class_label] = id

            class_label_maps[task] = class_label_map.values()

        logger.debug('Create new dataset')
        return self.create_dataset(dataset_name,
                                   classification_class_label_ids=class_label_maps['classification'],
                                   object_detection_class_label_ids=class_label_maps['object_detection'])

    def get_detection_class_label_map(self, dataset_id):
        """Retrieve a dictionary that maps class label names to their IDs.

        Example:
        >>> {'car': 4,
        >>>     'cyclist': 9,
        >>>     'motorcycle': 36,
        >>>     'pedestrian': 7,
        >>>     'traffic light': 41,
        >>>     'traffic sign': 119,
        >>>     'truck': 6
        >>> }

        :param dataset_id: The mapping is loaded for class labels of this dataset.
        :return: Class label map or `None` in case of errors.
        """

        dataset = self.get_dataset(dataset_id)

        if dataset is None:
            logger.error('Could not get dataset with ID {} for retrieving class labels'.format(dataset_id))
            return None

        class_labels = dataset['object_detection_class_labels']
        class_label_map = {}
        for class_label in class_labels:
            class_label_map[class_label['name']] = class_label['id']
        return class_label_map

    def get_classification_class_label_map(self, dataset_id):
        """Retrieve a dictionary that maps class label names to their IDs.

        Example:
        >>> {'car': 4,
        >>>     'cyclist': 9,
        >>>     'motorcycle': 36,
        >>>     'pedestrian': 7,
        >>>     'traffic light': 41,
        >>>     'traffic sign': 119,
        >>>     'truck': 6
        >>> }

        :param dataset_id: The mapping is loaded for class labels of this dataset.
        :return: Class label map or `None` in case of errors.
        """

        dataset = self.get_dataset(dataset_id)

        if dataset is None:
            logger.error('Could not get dataset with ID {} for retrieving class labels'.format(dataset_id))
            return None

        class_labels = dataset['classification_class_labels']
        class_label_map = {}
        for class_label in class_labels:
            class_label_map[class_label['name']] = class_label['id']
        return class_label_map

    def create_worker(self, name):
        """Create a new training worker.

        :return: ID of the newly created worker or `None`.
        """

        try:
            worker = {
                'name': name,
                'status': '',
                'details': {}
            }
            response = self.http.post(self.server_url + '/workers/', data=worker)
            response.raise_for_status()
            data = response.json()
            return data
        except rq.exceptions.RequestException as e:
            logger.error(e)
            raise e

    def import_dataspree(self, dataset_name, dataset_id, images, annotations):
        """Import a dataset that is available in the dataspree format.

        :param dataset_name: Name of the dataset that should be created. Set `None` if no new dataset should be created.
        :param dataset_id: ID of an existing dataset to which items should be imported. Set `-1` if a new dataset should be created.
        :param images: Directory containing all images.
        :param annotations: Directory containing the annotations.
        :return: Status code. 0: import completed, -1: error
        """
        logger.info('Import dataspree data')

        # create new dataset if no id is given
        if dataset_id == -1:
            # iterate over all items and determine used class labels (only for object detection for now)
            logger.debug('Retrieve used class labels')
            class_label_ids = set()
            annotation_files = os.listdir(annotations)
            for annotation_file in annotation_files:
                with open(os.path.join(annotations, annotation_file), 'r') as f:
                    annotation = json.load(f)
                    for o in annotation['objects']:
                        class_label_ids.add(o['label'])

            logger.debug('Create new dataset')
            dataset_id = self.create_dataset(dataset_name, object_detection_class_label_ids=class_label_ids)
        else:
            dataset = self.get_dataset(dataset_id)
            if dataset is None:
                logger.error('Dataset with ID {} does not exist.'.format(dataset_id))
                return -1

        if dataset_id == -1:
            logger.error('Dataset ID not provided and could not create new dataset.')
            return -1

        dataset_items = self.get_dataset_items(dataset_id)
        dataset_item_names = []

        for item in dataset_items:
            dataset_item_name = item['name'].split('/')[-1]
            dataset_item_names.append(dataset_item_name)

        # upload dataset items
        annotation_files = os.listdir(annotations)
        annotation_files.sort()

        image_files = os.listdir(images)
        image_files.sort()

        logger.info('Upload dataset items')
        for image_file in tqdm(image_files):

            # do not upload in case the dataset item exits already
            if image_file in dataset_item_names:
                continue

            base_name, image_extension = os.path.splitext(image_file)
            annotation_file = '{}.{}'.format(base_name, 'json')

            image_file_path = os.path.join(images, image_file)
            base_name_split = base_name.split('_')

            # first two elements of base_name_split contain dataset_id and item_id
            image_file_name = '{}{}'.format('_'.join(base_name_split[2:]), image_extension)

            annotation = {}
            # load annotations if they exist
            if annotation_file in annotation_files:
                annotation_files.remove(annotation_file)

                with open(os.path.join(annotations, annotation_file), 'r') as f:
                    annotation = json.load(f)

            if self.create_dataset_item(image_file_path, dataset_id, annotation, image_file_name) == -1:
                logger.error('Error during creation of dataset item.')
                return -1

        return 0

    def import_classification_directories(self, dataset_name, dataset_id, directory):
        """Import a dataset for classification where each subfolder represents a class. The folder names need to match the class names that are available in the DLSD platform.

                :param dataset_name: Name of the dataset that should be created. Set `None` if no new dataset should be created.
                :param dataset_id: ID of an existing dataset to which items should be imported. Set `-1` if a new dataset should be created.
                :param directory: Directory containing image subfolders.
                :return: Status code. 0: import completed, -1: error
                """
        logger.info('Import classification directories')

        subfolders = os.listdir(directory)

        # create new dataset if no id is given
        if dataset_id == -1:
            # iterate over all items and determine used class labels
            logger.debug('Retrieve used class labels')
            class_labels = set()
            for subfolder in subfolders:
                class_labels.add(subfolder.lower())

            dataset_id = self.create_labels_and_dataset(dataset_name, classification_class_labels=class_labels)
        else:
            dataset = self.get_dataset(dataset_id)
            if dataset is None:
                logger.error('Dataset with ID {} does not exist.'.format(dataset_id))
                return -1

        if dataset_id == -1:
            logger.error('Dataset ID not provided and could not create new dataset.')
            return -1

        class_label_map = self.get_classification_class_label_map(dataset_id)

        dataset_items = self.get_dataset_items(dataset_id)
        dataset_item_names = []

        for item in dataset_items:
            dataset_item_name = item['name'].split('/')[-1]
            dataset_item_names.append(dataset_item_name)

        logger.info('Upload dataset items')
        # upload dataset items
        for subfolder in subfolders:
            class_label_name = subfolder.lower()
            logger.info('Import {}'.format(class_label_name))

            image_files = os.listdir(os.path.join(directory, subfolder))

            class_annotation = {
                'classes': [class_label_map[class_label_name]]
            }

            for image_file in tqdm(image_files):

                # do not upload in case the dataset item exits already
                if image_file in dataset_item_names:
                    continue

                image_file_path = os.path.join(directory, subfolder, image_file)

                if self.create_dataset_item(image_file_path, dataset_id, class_annotation) == -1:
                    logger.error('Error during creation of dataset item.')
                    return -1

        return 0

    def import_kitti(self, dataset_name, dataset_id, images, annotations):
        """Import a dataset that is available in the KITTI format [1].

        :param dataset_name: Name of the dataset that should be created. Set `None` if no new dataset should be created.
        :param dataset_id: ID of an existing dataset to which items should be imported. Set `-1` if a new dataset should be created.
        :param images: Directory containing all images.
        :param annotations: Directory containing the annotations.
        :return: Status code. 0: import completed, -1: error

        [1] Geiger et al., "Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite", 2012.
            http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=2d
        """
        logger.info('Import KITTI data')

        # we import Pillow here as it is not required for other endpoints
        from PIL import Image

        # create new dataset if no id is given
        if dataset_id == -1:
            # iterate over all items and determine used class labels
            logger.debug('Retrieve used class labels')
            class_labels = set()
            annotation_files = os.listdir(annotations)
            for annotation_file in annotation_files:
                with open(os.path.join(annotations, annotation_file), 'r') as f:
                    file_content = f.readlines()
                    for line in file_content:
                        class_label = line.split(' ')[0].lower()
                        # skip all objects with label 'dontcare'
                        if class_label == 'dontcare' or class_label == 'misc':
                            continue
                        class_labels.add(class_label.lower())

            dataset_id = self.create_labels_and_dataset(dataset_name, object_detection_class_labels=class_labels)
        else:
            dataset = self.get_dataset(dataset_id)
            if dataset is None:
                logger.error('Dataset with ID {} does not exist.'.format(dataset_id))
                return -1

        if dataset_id == -1:
            logger.error('Dataset ID not provided and could not create new dataset.')
            return -1

        class_label_map = self.get_detection_class_label_map(dataset_id)

        dataset_items = self.get_dataset_items(dataset_id)
        dataset_item_names = []

        for item in dataset_items:
            dataset_item_name = item['name'].split('/')[-1]
            dataset_item_names.append(dataset_item_name)

        def convert_kitti_annotation(image_width, image_height, file_content):
            normalizer = max(image_width, image_height)
            objects = []

            for i, line in enumerate(file_content):
                attributes = line.split(' ')

                class_label = attributes[0].lower()
                # skip all objects with label 'dontcare'
                if class_label == 'dontcare' or class_label == 'misc':
                    continue

                class_label_id = class_label_map[class_label]

                left_x = float(attributes[4])
                top_y = float(attributes[5])
                right_x = float(attributes[6])
                bottom_y = float(attributes[7])

                x = ((left_x + right_x) / 2.0) / normalizer
                y = ((top_y + bottom_y) / 2.0) / normalizer
                w = (right_x - left_x) / normalizer
                h = (bottom_y - top_y) / normalizer

                o = {
                    'id': i,
                    'label': class_label_id,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'orientation': 0
                }

                objects.append(o)

            return objects

        # upload dataset items
        annotation_files = os.listdir(annotations)
        image_files = os.listdir(images)

        logger.info('Upload dataset items')
        for image_file in tqdm(image_files):

            # do not upload in case the dataset item exits already
            if image_file in dataset_item_names:
                continue

            base_name = os.path.splitext(image_file)[0]
            annotation_file = '{}.{}'.format(base_name, 'txt')

            # only upload if image and annotation exists
            if annotation_file in annotation_files:
                annotation_files.remove(annotation_file)
                image_file_path = os.path.join(images, image_file)

                # We need to open the image to retrieve its width and height
                # Image.open is a lazy operation - hence, the complete image
                # data is not read immediately.
                image = Image.open(image_file_path)
                image_width, image_height = image.size

                with open(os.path.join(annotations, annotation_file), 'r') as f:
                    objects = convert_kitti_annotation(image_width, image_height, f.readlines())
                    annotation = {
                        'objects': objects
                    }

                if self.create_dataset_item(image_file_path, dataset_id, annotation) == -1:
                    logger.error('Error during creation of dataset item.')
                    return -1

        return 0

    def import_coco(self, dataset_name, dataset_id, images, annotations):
        """Import a dataset that is available in the COCO format [1].

        :param dataset_name: Name of the dataset that should be created. Set `None` if no new dataset should be created.
        :param dataset_id: ID of an existing dataset to which items should be imported. Set `-1` if a new dataset should be created.
        :param images: Directory containing all images.
        :param annotations: Directory containing the annotations.
        :return: Status code. 0: import completed, -1: error

        [1] Lin et al., "Microsoft COCO: Common Objects in Context", 2014.
            https://cocodataset.org/
        """

        logger.info('Import COCO data')

        with open(annotations, 'r') as f:
            coco = json.load(f)

        coco_class_id_map = {}
        for c in coco['categories']:
            coco_class_id_map[c['id']] = c['name']

        # create new dataset if no id is given
        if dataset_id == -1:
            # iterate over all items and determine used class labels
            logger.debug('Retrieve used class labels')
            dataset_id = self.create_labels_and_dataset(dataset_name,
                                                        object_detection_class_labels=coco_class_id_map.values())
            logger.info('Created dataset with ID {}.'.format(dataset_id))
        else:
            dataset = self.get_dataset(dataset_id)
            if dataset is None:
                logger.error('Dataset with ID {} does not exist.'.format(dataset_id))
                return -1

        if dataset_id == -1:
            logger.error('Dataset ID not provided and could not create new dataset.')
            return -1

        class_label_map = self.get_detection_class_label_map(dataset_id)
        dataset_items = self.get_dataset_items(dataset_id)
        dataset_item_names = []

        for item in dataset_items:
            dataset_item_name = item['name'].split('/')[-1]
            dataset_item_names.append(dataset_item_name)

        # upload dataset items
        logger.info('Upload dataset items')

        coco_annotations = {}
        coco_annotation_ids = {}
        for a in coco['annotations']:
            coco_annotations[a['id']] = a
            image_id = a['image_id']
            if image_id not in coco_annotation_ids:
                coco_annotation_ids[image_id] = []
            coco_annotation_ids[image_id].append(a['id'])

        if self.parallel_requests > 1:
            Parallel(n_jobs=self.parallel_requests, prefer='threads')(
                delayed(self.upload_item_coco)(coco_image, images, coco_annotation_ids, coco_annotations,
                                               coco_class_id_map,
                                               class_label_map, dataset_id, dataset_item_names) for coco_image in
                tqdm(coco['images']))
        else:
            for coco_image in tqdm(coco['images']):
                self.upload_item_coco(coco_image, images, coco_annotation_ids, coco_annotations, coco_class_id_map,
                                      class_label_map, dataset_id, dataset_item_names)

        return 0

    def upload_item_coco(self, coco_image, images, coco_annotation_ids, coco_annotations, coco_class_id_map,
                         class_label_map, dataset_id, dataset_item_names):
        image_id = coco_image['id']
        image_file_name = coco_image['file_name']

        # do not upload in case the dataset item exits already
        if image_file_name in dataset_item_names:
            return

        image_file_path = os.path.join(images, image_file_name)
        image_width = coco_image['width']
        image_height = coco_image['height']
        normalizer = max(image_width, image_height)

        # get corresponding annotations
        objects = []
        if image_id not in coco_annotation_ids:
            return
        for i, cid in enumerate(coco_annotation_ids[image_id]):
            a = coco_annotations[cid]

            coco_class_id = a['category_id']
            class_label_name = coco_class_id_map[coco_class_id]
            class_label_id = class_label_map[class_label_name]
            x = (a['bbox'][0] + 0.5 * a['bbox'][2]) / normalizer
            y = (a['bbox'][1] + 0.5 * a['bbox'][3]) / normalizer
            w = a['bbox'][2] / normalizer
            h = a['bbox'][3] / normalizer
            o = {
                'id': i,
                'label': class_label_id,
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'orientation': 0
            }
            objects.append(o)

        annotation = {
            'objects': objects
        }

        if self.create_dataset_item(image_file_path, dataset_id, annotation) == -1:
            logger.error('Error during creation of dataset item.')
            return -1
