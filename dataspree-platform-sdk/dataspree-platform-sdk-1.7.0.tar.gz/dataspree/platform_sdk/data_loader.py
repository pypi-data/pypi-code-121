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

import json
import logging
import os
import numpy as np
from copy import copy, deepcopy
from enum import Enum
from time import sleep
from typing import Optional, Dict, List

from tqdm import tqdm

from dataspree.platform_sdk.client import Client
from dataspree.platform_sdk.decoder.base_decoder import BaseDecoder
from dataspree.platform_sdk.decoder.pcd_decoder import PcdDecoder
from dataspree.platform_sdk.decoder.opencv_decoder import OpencvDecoder

logger = logging.getLogger(__name__)


class LoadMode(Enum):
    PRELOAD = 0
    ADHOC = 1
    ADHOC_CACHED = 2


class DataLoader:
    """Data loader for data from the Data Spree AI Platform"""

    def __init__(self, client: Client, network_model: Dict, dataset_directory: str,
                 mode: LoadMode = LoadMode.ADHOC_CACHED,
                 allowed_status=('annotated', 'reviewed'), decoders: Optional[List[BaseDecoder]] = None,
                 distinct_items_per_category: bool = True):
        self._client = client
        self._network_model = network_model
        self._dataset_directory = dataset_directory
        self._mode = mode
        self._allowed_status = allowed_status
        self._decoders = []
        self._distinct_items_per_category = distinct_items_per_category
        self._max_retries = 10

        if self._dataset_directory == '':
            logger.info('Switching to adhoc mode because no dataset directory is provided.')
            self._mode = LoadMode.ADHOC

        if decoders is None:
            decoders = [PcdDecoder(), OpencvDecoder()]
            # decoders=[PcdDecoder(), OpencvDecoder(), PlyDecoder()] # TODO: Test Me

        for decoder in decoders:
            self.add_decoder(decoder)

        self._items = {}

        # load class label ids and names that are used within this model
        self._class_labels = client.get_model_class_labels(network_model['id'])

        # get all categories and aggregate the respective subset IDs
        self._subsets_ids_by_category = {}
        for entry in network_model['data_subsets']:
            if entry['category'] not in self._subsets_ids_by_category.keys():
                self._subsets_ids_by_category[entry['category']] = []
            if entry['data_subset']['id'] not in self._subsets_ids_by_category[entry['category']]:
                self._subsets_ids_by_category[entry['category']].append(entry['data_subset']['id'])

        # get all subset IDs
        subset_ids = []
        condensed_subset_ids = [self._subsets_ids_by_category[cat] for cat in self._subsets_ids_by_category.keys()]
        for subset_id in [item for sublist in condensed_subset_ids for item in sublist]:
            subset_ids.append(subset_id)

        # get all item IDs
        self._item_ids = set()
        self._item_ids_by_subset = {}
        for subset_id in subset_ids:
            if subset_id not in self._item_ids_by_subset:
                self._item_ids_by_subset[subset_id] = []

            ## FIXME: only get items that have the reqested class IDs.
            # TODO: figure out the most efficient way to get those items.
            # SUGGESTIONS A: client.get_dataset_items with specified class_id for all IDs. Probably slow when a lot of labels are required
            # SUGGESTIONS B: client.get_dataset_items with specified class_id in filter query (?, this is also limited in DLDS isn't it?)
            subset_item_details = self._client.get_data_subset_items(subset_id)
            for item in subset_item_details:
                # del item['name']
                # del item['updated_date']
                if item['status'] in self._allowed_status:
                    item['exists'] = False
                    self._items[item['id']] = item
                    self._item_ids_by_subset[subset_id].append(item['id'])
                    self._item_ids.add(item['id'])

        self._item_ids = list(self._item_ids)

        self._item_ids_by_category = {}
        for category in self._subsets_ids_by_category.keys():
            for subset_id in self._subsets_ids_by_category[category]:
                if category not in self._item_ids_by_category:
                    if distinct_items_per_category:
                        self._item_ids_by_category[category] = set()
                    else:
                        self._item_ids_by_category[category] = list()

                if distinct_items_per_category:
                    self._item_ids_by_category[category].update(self._item_ids_by_subset[subset_id])
                else:
                    self._item_ids_by_category[category].extend(self._item_ids_by_subset[subset_id])

            if distinct_items_per_category:
                self._item_ids_by_category[category] = list(self._item_ids_by_category[category])

        if self._mode == LoadMode.PRELOAD:
            for item_id in tqdm(self._item_ids):
                image_directory = os.path.join(self._dataset_directory, str(self._items[item_id]['dataset']), 'images')
                metainformation_directory = os.path.join(self._dataset_directory, str(self._items[item_id]['dataset']),
                                                         'metainformation')

                item = self._items[item_id]
                dataset_id = item['dataset']
                item_name = item['name'].split('/')[-1]
                image_file_name = f'{dataset_id}_{item_id}_{item_name}'
                metainformation_file_name = image_file_name.split('.')[0] + '.json'
                image_path = os.path.join(image_directory, image_file_name)
                metainformation_path = os.path.join(metainformation_directory, metainformation_file_name)
                if os.path.exists(image_path) and os.path.exists(metainformation_path):
                    item['exists'] = True
                else:
                    self._client.download_dataset_item(item_id, image_dir=image_directory,
                                                            metainformation_directory=metainformation_directory,
                                                            accepted_status=self._allowed_status,
                                                            return_item=False)

    def __reduce__(self):
        return (DataLoader, (self._client,
                             self._network_model,
                             self._dataset_directory,
                             self._mode,
                             self._allowed_status,
                             self._decoders,
                             self._distinct_items_per_category,))

    def add_decoder(self, decoder):
        self._decoders.append(decoder)

    def get_class_labels(self) -> List[Dict]:
        """Get the list of class labels that are selected for the loaded model.

        :return: List containing the class labels with ID and name.
        """
        return copy(self._class_labels)

    def get_categories(self) -> List[str]:
        """List containing the names of all categories.

        :return: List of category names.
        """
        return list(self._item_ids_by_category.keys())

    def get_subset_ids_by_category(self, category) -> List[str]:
        """List containing the ids of all subsets in that categories.

        :return: List of subset ids.
        """
        return self._subsets_ids_by_category.get(category, [])

    def get_subset_ids(self, category=None) -> List[int]:
        """List containing the IDs of the subsets of the specified category or all subsets.

        :param category: Category to filter the subset IDs.
        :return: List of subset IDs.
        """

        if category is None:
            return list(self._item_ids_by_subset.keys())
        else:
            return list(self._subsets_ids_by_category[category])

    def get_item_ids(self) -> List[int]:
        """List containing the IDs of all items.

        This list contains unique item IDs, e.g. an item that belongs to multiple subsets is only listed once.

        :return: List of item IDs.
        """
        return copy(list(set(self._item_ids)))

    def get_item_ids_by_category(self, category) -> List[int]:
        """Get the IDs of all items that belong to the specified category.

        :param category: Category to filter the item IDs.
        :return: List of item IDs.
        """
        return copy(self._item_ids_by_category.get(category, []))

    def get_item_ids_by_subset(self, subset_id):
        """Get the IDs of all items that belong to the specified subset.

        :param subset_id: ID of a subset.
        :return: List of item IDs.
        """
        return copy(self._item_ids_by_subset.get(subset_id, []))

    def get_item(self, item_id, n_retries=0, store_binary: bool = False) -> Optional[Dict]:
        """Get dataset item given its ID.

        :param item_id: ID of the item.
        :param store_binary:
        :return: Dictionary containing the image and meta data or None if the item does not exist.
        >>> {
        >>> 'id': int,
        >>> 'image': [],
        >>> 'annotations': Dict
        >>> }
        """

        logger.debug(f'get item {item_id}')

        loading_error = False

        item_serialized = None
        decoded_image_path = None
        if self._mode == LoadMode.ADHOC:
            item_serialized = self._client.download_dataset_item(item_id, image_dir=None,
                                                                      metainformation_directory=None,
                                                                      accepted_status=self._allowed_status,
                                                                      return_item=True)
        else:
            # get item details (if it exists already)
            item = self._items.get(item_id)
            if item is None:
                item = self._client.get_dataset_item(item_id)
                self._items[item_id] = item

            if item is not None:
                dataset_id = item['dataset']
                image_directory = os.path.join(self._dataset_directory, str(dataset_id), 'images')
                metainformation_directory = os.path.join(self._dataset_directory, str(dataset_id), 'metainformation')

                item_name = item['name'].split('/')[-1]
                image_file_name = f'{dataset_id}_{item_id}_{item_name}'

                metainformation_file_name = os.path.splitext(image_file_name)[0] + '.json'
                image_path = os.path.join(image_directory, image_file_name)
                decoded_image_path = os.path.join(image_directory, f'{image_file_name}.bin') if store_binary else None
                metainformation_path = os.path.join(metainformation_directory, metainformation_file_name)

                item['image_path'] = image_path
                item['decoded_image_path'] = decoded_image_path
                item['metainformation_path'] = metainformation_path
                item_serialized = deepcopy(item)

                if (os.path.exists(image_path)
                    or (decoded_image_path is not None and os.path.exists(decoded_image_path))) \
                        and os.path.exists(metainformation_path):
                    item['exists'] = True

                    if decoded_image_path is not None and os.path.exists(decoded_image_path):
                        try:
                            with open(decoded_image_path, 'rb') as f:
                                item_serialized['decoded_image'] = np.load(f)
                        except Exception:
                            logger.warning(f'could not  decode bianry image file {decoded_image_path}.')

                    if 'decoded_image' not in item_serialized:
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as f:
                                item_serialized['image'] = f.read()
                        else:
                            loading_error = True

                    with open(metainformation_path, 'r') as f:
                        try:
                            loaded = json.load(f)

                            str_changed_date_json = loaded.get('updated_date')
                            str_changed_date_item = item.get('updated_date')

                            if str_changed_date_json is None or str_changed_date_item is None:
                                logger.warning(f'Could not extract modified date from item {item_id}:'
                                               f'"{str_changed_date_json}", "{str_changed_date_item}"')

                            changed_date_json = None
                            changed_date_item = None

                            if str_changed_date_json is not None and str_changed_date_item is not None:
                                changed_date_item = Client.parse_dataset_item_date(str_changed_date_item)
                                changed_date_json = Client.parse_dataset_item_date(str_changed_date_json)

                            if changed_date_json is not None and changed_date_item is not None \
                                    and changed_date_json > changed_date_item:
                                logger.warning('The item\'s cached metainformation are newer than those from the '
                                               'platform. Expecting an error and downloading the current item again. ')

                            item['exists'] = changed_date_item is not None and changed_date_json is not None \
                                             and changed_date_item == changed_date_json

                            if item['exists']:
                                item_serialized['annotations'] = loaded['annotations']

                        except json.JSONDecodeError:
                            logger.warning(f'Could not load metainformation for item {item_id}')
                            loading_error = True

                else:
                    item['exists'] = False

                if not item['exists']:
                    item_serialized: Optional[Dict] = self._client.download_dataset_item(
                        item_id, image_dir=image_directory, metainformation_directory=metainformation_directory,
                        accepted_status=self._allowed_status, return_item=True)
                    if item_serialized is not None:
                        item_serialized['exists'] = True
                        item_serialized['image_path'] = image_path
                        item_serialized['metainformation_path'] = metainformation_directory

        if item_serialized is None:
            loading_error = True
        else:
            # decode

            item_file_extension = os.path.splitext(item_serialized['name'])[1].lower().replace('.', '')
            if item_file_extension == '':
                # assume jpg if no file extension
                item_file_extension = 'jpg'
            if self._decoders:

                if 'decoded_image' in item_serialized:
                    item_serialized['image'] = item_serialized['decoded_image']
                    item_serialized['data_type'] = item_file_extension

                else:
                    loading_error = True
                    for decoder in self._decoders:
                        extensions = decoder.get_file_extensions()
                        if item_file_extension in extensions:
                            try:
                                item_serialized['image'], item_serialized['metadata'] = decoder(
                                    item_serialized['image'])
                                item_serialized['data_type'] = item_file_extension

                                if decoded_image_path is not None:
                                    with open(decoded_image_path, 'wb') as f:
                                        np.save(f, item_serialized['image'])
                                loading_error = False
                            except Exception as e:
                                logger.warning(f'Could not decode image for item {item_id}: {type(e)}: {e}')
                                #loading_error = True
                            break
                    if loading_error: return None

        if loading_error:
            if n_retries < self._max_retries:
                # sleep for 1, 2, 4, 8, ... milliseconds (maximum 2 seconds)
                sleep(min(2.0, 1e-3 * 2 ** n_retries))

                if item_serialized is not None and item_serialized.get('exists', False):
                    if 'image_path' in item_serialized:
                        try:
                            os.remove(item_serialized['image_path'])
                        except Exception as e:
                            logger.error(f'Exception occurred while removing {item_serialized["image_path"]}\n{e}')
                    if 'metainformation_path' in item_serialized:
                        try:
                            os.remove(item_serialized['metainformation_path'])
                        except Exception as e:
                            logger.error(f'Exception occurred while removing '
                                         f'{item_serialized["metainformation_path"]}\n{e}')

                return self.get_item(item_id, n_retries + 1)
            else:
                return None

        image = item_serialized['image']
        data_type = item_serialized['data_type']
        annotations = item_serialized['annotations']

        sample = {
            'id': item_id,
            'image': image,
            'data_type': data_type,
            'annotations': annotations
        }

        return sample
