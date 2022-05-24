import logging
from contextlib import suppress

import scrapy
from itemadapter import ItemAdapter
from rollbot_crawlab.utils.oss_file_upload import OssFileUpload
from scrapy.exceptions import NotConfigured
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.log import failure_to_exc_info
from twisted.internet import threads, defer

logger = logging.getLogger(__name__)

class AliOssStore(object):
    file_upload = None

    def __init__(self, ali_oss_config):
        OSS_ACCESS_KEY_ID = ali_oss_config.get("OSS_ACCESS_KEY_ID")
        OSS_SECRET_ACCESS_KEY = ali_oss_config.get("OSS_SECRET_ACCESS_KEY")
        OSS_ENDPOINT_URL = ali_oss_config.get("OSS_ENDPOINT_URL")
        OSS_BUCKET_NAME = ali_oss_config.get("OSS_BUCKET_NAME")
        self.file_upload = OssFileUpload(OSS_ACCESS_KEY_ID, OSS_SECRET_ACCESS_KEY, OSS_ENDPOINT_URL, OSS_BUCKET_NAME)

    def stat_file(self, path, info):
        def _onsuccess(obj):
            return obj
        return threads.deferToThread(self.file_upload.exist, path).addCallback(_onsuccess)

    def persist_file(self, path, buf, info, meta=None, headers=None):
        return threads.deferToThread(self._upload_file, path, buf)

    def _upload_file(self, path, buf):
        self.file_upload.upload_object(path, buf)


class OssFilePipeline(FilesPipeline):
    DEFAULT_FILES_URLS_FIELD = "movies"
    DEFAULT_FILES_RESULT_FIELD = "oss_movies"

    def __init__(self, store_uri, ali_oss_config, settings=None):
        self.ali_oss_config = ali_oss_config
        if store_uri[len(store_uri) - 1] != '/':
            store_uri += "/"
        self.store_uri = store_uri
        super(OssFilePipeline, self).__init__(store_uri=self.store_uri, settings=settings)

    def _get_store(self, uri):
        return AliOssStore(
            self.ali_oss_config
        )

    def get_media_requests(self, item, info):

        upload_oss = item.get('upload_oss', False)
        if upload_oss:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
            }
            if item.get("block_id") == "post.instagram":
                headers["origin"] = "https://www.instagram.com/"
                headers["referer"] = "https://www.instagram.com/"
            return [scrapy.Request(x, headers=headers, meta={'has_base': True}) for x in item.get(self.files_urls_field, [])]
        else:
            item["download_image"] = False
            item["download_video"] = False
            return []

    @classmethod
    def from_settings(cls, settings):
        ali_oss_config = {
            "OSS_ACCESS_KEY_ID": settings['OSS_ACCESS_KEY_ID'],
            "OSS_SECRET_ACCESS_KEY": settings['OSS_SECRET_ACCESS_KEY'],
            "OSS_ENDPOINT_URL": settings['OSS_ENDPOINT_URL'],
            "OSS_BUCKET_NAME": settings['OSS_BUCKET_NAME']
        }
        store_uri = settings['OSS_BUCKET_URL']
        if not ali_oss_config:
            raise NotConfigured('You should config the ali_oss_config to enable this pipeline')
        return cls(store_uri=store_uri, ali_oss_config=ali_oss_config, settings=settings)

    def media_to_download(self, request, info, *, item=None):
        def _onsuccess(result):
            if not result:
                return  # returning None force download
            return {'url': request.url, 'path': path}

        path = self.file_path(request, info=info, item=item)
        dfd = defer.maybeDeferred(self.store.stat_file, path, info)
        dfd.addCallbacks(_onsuccess, lambda _: None)
        dfd.addErrback(
            lambda f:
            logger.error(self.__class__.__name__ + '.store.stat_file',
                         exc_info=failure_to_exc_info(f),
                         extra={'spider': info.spider})
        )
        return dfd

    def map_item_for_oss_url(self, item):
        item["oss_url"] = self.store_uri + item.get("path")
        return item


class ImageFilesPipeline(OssFilePipeline):
    DEFAULT_FILES_URLS_FIELD = "images"
    DEFAULT_FILES_RESULT_FIELD = "oss_images"

    def item_completed(self, results, item, info):
        with suppress(KeyError):
            if results and len(results) > 0:
                res_list = [x for ok, x in results if ok]
                if len(res_list) > 0:
                    res_list = list(map(self.map_item_for_oss_url, res_list))
                    article_html = ItemAdapter(item).get("article_html")
                    if article_html and '' != article_html:
                        for res_item in res_list:
                            request_url = res_item.get('url')
                            oss_url = res_item.get('oss_url')
                            article_html = article_html.replace(request_url, oss_url)
                        ItemAdapter(item)["article_html"] = article_html
                    ItemAdapter(item)[self.files_result_field] = res_list
                    ItemAdapter(item)["download_image"] = True
                else:
                    ItemAdapter(item)["download_image"] = False
        return item

    def file_path(self, request, response=None, info=None, item=None):
        return self.store.file_upload.get_file_path(
            url=request.url, item=item, default_ext=".jpg", folder="image"
        )


class VideoFilesPipeline(OssFilePipeline):
    DEFAULT_FILES_URLS_FIELD = "movies"
    DEFAULT_FILES_RESULT_FIELD = "oss_movies"

    def item_completed(self, results, item, info):
        with suppress(KeyError):
            if results and len(results) > 0:
                res_list = [x for ok, x in results if ok]
                if len(res_list) > 0:
                    res_list = list(map(self.map_item_for_oss_url, res_list))
                    article_html = ItemAdapter(item).get("article_html")
                    if article_html and '' != article_html:
                        for res_item in res_list:
                            request_url = res_item.get('url')
                            oss_url = res_item.get('oss_url')
                            article_html = article_html.replace(request_url, oss_url)
                        ItemAdapter(item)["article_html"] = article_html
                    ItemAdapter(item)[self.files_result_field] = res_list
                    ItemAdapter(item)["download_video"] = True
                else:
                    ItemAdapter(item)["download_video"] = False
        return item

    def file_path(self, request, response=None, info=None, item=None):
        return self.store.file_upload.get_file_path(
            url=request.url, item=item, default_ext=".mp4", folder="video"
        )


class AuthorAvatarFilesPipeline(OssFilePipeline):
    def get_media_requests(self, item, info):
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        upload_oss = item.get('upload_oss', False)
        request_list = []
        if upload_oss:
            author_avatar = ItemAdapter(item).get('author', {}).get("avatar")
            if author_avatar:
                request_list.append(
                    scrapy.Request(author_avatar, headers=headers, meta={'has_base': True})
                )
        else:
            item["download_image"] = False
            item["download_video"] = False
        return request_list

    def item_completed(self, results, item, info):
        with suppress(KeyError):
            if 'author' in item:
                res_list = [x for ok, x in results if ok]
                if len(res_list) > 0:
                    res_list = list(map(self.map_item_for_oss_url, res_list))
                    article_html = ItemAdapter(item).get("article_html")
                    if article_html and '' != article_html:
                        for res_item in res_list:
                            request_url = res_item.get('url')
                            oss_url = res_item.get('oss_url')
                            article_html = article_html.replace(request_url, oss_url)
                        ItemAdapter(item)["article_html"] = article_html
                    if res_list and len(res_list) > 0:
                        ItemAdapter(item)['author']['avatar'] = res_list[0].get("oss_url")
        return item

    def file_path(self, request, response=None, info=None, item=None):
        return self.store.file_upload.get_file_path(
            url=request.url, item=item, default_ext=".jpg", folder="avatar"
        )
