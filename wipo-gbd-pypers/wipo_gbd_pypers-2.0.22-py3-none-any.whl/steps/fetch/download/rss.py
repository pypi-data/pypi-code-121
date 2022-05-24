import os
from xml.etree import ElementTree as etree
from pypers.steps.base.fetch_step import FetchStep
from pypers.utils import download


class RSS(FetchStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch an RSS feed"
        ]
    }
    from_type = 'from_url'

    def specific_process(self):
        # getting files from rss
        rss_url = self.fetch_from['from_url']
        r = download.download(rss_url,
                              http_proxy=self.meta['pipeline'][
                                  'input'].get('http_proxy'),
                              https_proxy=self.meta['pipeline'][
                                  'input'].get('https_proxy'))

        feed_data = etree.fromstring(r.read())
        r.close()
        items = feed_data.findall('channel/item')
        links = [item.findtext('link') for item in items]
        count = 0
        for archive_url in sorted(links):
            if self.limit and count == self.limit:
                break
            if os.path.basename(archive_url) in self.done_archives:
                continue
            if not self.rgx.match(archive_url):
                continue
            count += 1
            self.logger.info('[rss] %s: %s' % (count, archive_url))

            rh = download.download(
                archive_url,
                http_proxy=self.meta['pipeline']['input'].get('http_proxy'),
                https_proxy=self.meta['pipeline']['input'].get('https_proxy'))

            output_file = os.path.join(self.output_dir,
                                       os.path.basename(archive_url))
            # Open our local file for writing
            with open(output_file, 'wb') as local_file:
                local_file.write(rh.read())
            rh.close()
            self.output_files.append(output_file)
        r.close()
