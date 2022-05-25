# -*- coding: utf-8 -*-
"""
更新日期:2022/4/28
作者: D.Z.zhong
用途: 图片管道文件实现异步下载上传至阿里云oss
运行环境：win10 64/linux + python3.9 + scrapy2.4.1 + oss2 + magic(pip install python-magic-bin)
选择目录位置:{python}/Lib/site-packages/scrapy/xcc_pipelines
"""

import logging
from io import BytesIO
from urllib.parse import urlparse

from .ossfilepipelines import OssFilesPipeline
from scrapy.utils.request import referer_str
from scrapy.pipelines.files import FileException

from scrapy.utils.misc import arg_to_iter
from twisted.internet.defer import DeferredList

# logging.basicConfig(level=logging.INFO)
logging.getLogger('pdfplumber').setLevel(logging.WARNING)
logging.getLogger('PyPDF2').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('oss2').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)




class OssImagesPipeline(OssFilesPipeline): #图片类
    DEFAULT_FILES_OSS_URLS_FIELD = 'raw_img_url'
    DEFAULT_FILES_OSS_RESULT_FIELD = 'img_url'
    MIN_WIDTH = 50
    MIN_HEIGHT = 50
    def process_item(self, item, spider):
        info = self.spiderinfo
        requests = arg_to_iter(self.get_media_requests(item, info))
        dlist = [self._process_request(r, info, item) for r in requests]
        dfd = DeferredList(dlist, consumeErrors=1)
        return dfd.addCallback(self.item_completed, item, info)

    def media_downloaded(self, response, request, info, *, item=None):
        '''多处理了一步图片大小判断'''
        from PIL import Image
        orig_image = Image.open(BytesIO(response.body))

        width, height = orig_image.size
        if width < self.MIN_WIDTH or height < self.MIN_HEIGHT:
            raise ImageException("Image too small "
                                 f"({width}x{height} < "
                                 f"{self.MIN_WIDTH}x{self.MIN_HEIGHT})")

        referer = referer_str(request)
        if response.status != 200:
            logger.warning(
                'File (code: %(status)s): Error downloading file from '
                '%(request)s referred in <%(referer)s>',
                {'status': response.status,
                 'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('download-error')

        if not response.body:
            logger.warning(
                'File (empty-content): Empty file from %(request)s referred '
                'in <%(referer)s>: no-content',
                {'request': request, 'referer': referer},
                extra={'spider': info.spider}
            )
            raise FileException('empty-content')

        status = 'cached' if 'cached' in response.flags else 'downloaded'
        logger.debug(
            'File (%(status)s): Downloaded file from %(request)s referred in '
            '<%(referer)s>',
            {'status': status, 'request': request, 'referer': referer},
            extra={'spider': info.spider}
        )
        self.inc_stats(info.spider, status)

        try:
            path = self.file_path(request, response=response, info=info, item=item)
            checksum = self.file_downloaded(response, request, info, item=path)
        except FileException as exc:
            logger.warning(
                'File (error): Error processing file from %(request)s '
                'referred in <%(referer)s>: %(errormsg)s',
                {'request': request, 'referer': referer, 'errormsg': str(exc)},
                extra={'spider': info.spider}, exc_info=True
            )
            raise
        except Exception as exc:
            logger.error(
                'File (unknown-error): Error processing file from %(request)s '
                'referred in <%(referer)s>',
                {'request': request, 'referer': referer},
                exc_info=True, extra={'spider': info.spider}
            )
            raise FileException(str(exc))

        return {'url': request.url, 'path': path, 'checksum': checksum, 'status': status}
        # return super().media_downloaded(response, request, info, item=item)

class OssImagesPipelineBak(OssImagesPipeline): #图片类备用 如电路图
    pass


class ImageException(FileException):
    """General image error exception"""