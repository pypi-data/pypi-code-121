# -*- coding:utf-8 -*-
import logging

import os

from .faiss_utils import FaissManager


class ImageIndexUtils(object):
    key_extend_list = "extend_list"

    def __init__(self, index_dir: str, dimension: int):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)
        self.db_index_dir = index_dir
        self.manager = FaissManager(
            index_path=os.path.join(index_dir, "faiss.index"),
            dimension=dimension
        )
        self.dimension = dimension
        self._key_distance = "distance"
        self._key_top_k = "top"

    def image_search(self, feature_list: list, top_k: int = 3, extend: bool = False) -> list:
        """
            for each feature, return list like: [(1, [100], 0.10), (3,[], 0.30), ...]
        """
        return [
            result for result in self.image_search_iterator(feature_list=feature_list, top_k=top_k, extend=extend)
        ]

    def get_image_info(self, image_index: int) -> dict:
        return self.manager.index_info_list[image_index]

    def image_search_iterator(self, feature_list: list, top_k: int = 3, extend: bool = False):
        """
            for each feature, return list like: [(1, [100], 0.10), (3,[], 0.30), ...]
        """
        distance_list, indices = self.manager.search(feature_list, top_k=top_k)

        for index in range(distance_list.shape[0]):
            image_result_list = []

            for i in range(top_k):
                image_index = indices[index][i]
                if image_index == self.manager.not_found_id:
                    break

                if extend:
                    image_result_list.append(
                        (image_index,
                         self.manager.index_info_list[image_index].get(self.manager.key_extend_list, []),
                         distance_list[index][i])
                    )
                else:
                    image_result_list.append((image_index, [], distance_list[index][i]))

            yield image_result_list

    def add_images(self, image_feature_list: list, image_info_list: list):
        assert len(image_feature_list) == len(image_info_list)
        self.manager.train(image_feature_list, info_list=image_info_list)


__all__ = ("ImageIndexUtils",)
