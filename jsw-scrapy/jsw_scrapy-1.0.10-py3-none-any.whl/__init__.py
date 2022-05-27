import pkg_resources

version = pkg_resources.get_distribution('jsw-scrapy').version
__version__ = version

# next models/pipelines/spiders
from jsw_scrapy.models import BaseModel
from jsw_scrapy.pipelines.base_pipeline import BasePipeline
from jsw_scrapy.spiders.base_spider import BaseSpider

