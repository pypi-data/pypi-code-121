import json
import math
import requests
from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract AUTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    # we get the data_files from archive extract
    # need to collect img urls for download
    def process(self):
        # divide appnums into chunks of 100
        appnum_list = list(self.manifest['data_files'].keys())
        chunk_size = 100
        chunk_nb = int(math.ceil(float(len(appnum_list))/chunk_size))

        appnum_chunk_list = [
            appnum_list[i*chunk_size:i*chunk_size+chunk_size]
            for i in range(chunk_nb)]

        media_url = 'https://search.ipaustralia.gov.au/trademarks/external/' \
                    'api-v2/media?markId=%s'
        proxy_params, auth = self.get_connection_params('from_web')
        for appnum_chunk in appnum_chunk_list:
            with requests.session() as session:
                response = session.get(media_url % ','.join(appnum_chunk),
                                       proxies=proxy_params, auth=auth)
                medias = json.loads(response.content)

                for media in medias:
                    appnum = media['markId']
                    for idx, img in enumerate(media.get('images', [])):
                        self.add_img_url(appnum, img['location'])
