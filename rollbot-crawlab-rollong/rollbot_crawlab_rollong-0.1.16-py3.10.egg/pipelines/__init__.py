from rollbot_crawlab.utils import save_item_mongo
from rollbot_crawlab.utils.config import get_task_id
import datetime


class CrawlabMongoPipeline(object):
    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict['task_id'] = get_task_id()
        item_dict['created_at'] = datetime.datetime.now()
        save_item_mongo(item_dict)
        return item
