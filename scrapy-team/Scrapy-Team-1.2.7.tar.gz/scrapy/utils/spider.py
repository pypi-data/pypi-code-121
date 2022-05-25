import inspect
import logging

from scrapy.spiders import Spider
from scrapy.utils.defer import deferred_from_coro
from scrapy.utils.misc import arg_to_iter
from scrapy.settings import register_settings
try:
    from scrapy.utils.py36 import collect_asyncgen
except SyntaxError:
    collect_asyncgen = None


logger = logging.getLogger(__name__)


def iterate_spider_output(result):
    if collect_asyncgen and hasattr(inspect, 'isasyncgen') and inspect.isasyncgen(result):
        d = deferred_from_coro(collect_asyncgen(result))
        d.addCallback(iterate_spider_output)
        return d
    elif inspect.iscoroutine(result):
        d = deferred_from_coro(result)
        d.addCallback(iterate_spider_output)
        return d
    return arg_to_iter(result)


def iter_spider_classes(module):
    """
    by zhizhong
    Return an iterator over all spider classes defined in the given module
    that can be instantiated (i.e. which have name)
    """
    # this needs to be imported here until get rid of the spider manager
    # singleton in scrapy.spider.spiders
    from scrapy.spiders import Spider
    try:
        import spider_register
    except:
        logging.warning("注意检查!! 项目中是否存在 spider_register 注册文件")
    for obj in vars(module).values():
        if inspect.isclass(obj) and len(obj.__module__.split("."))==5:
            project_dir, spider_path, user_name, register_key = obj.__module__.split(".",3)
            if (
                issubclass(obj, Spider)
                and obj.__module__ == module.__name__
                ):
                try:
                    if getattr(obj, 'name') is None or isinstance(obj.name,list):
                        obj.name = eval(f"spider_register.{user_name}.get('{register_key}')[0]") # to_fixed
                        obj = filter_settings_by_register(obj,eval(f"spider_register.{user_name}.get('{register_key}')"))
                except Exception as e: 
                    print(f"经过检查,{user_name}同学的爬虫模块{register_key}名为{obj.name}的配置存在匹配异常：{e}")
                yield obj

def filter_settings_by_register(obj,param):
    """
    by zhizhong
    根据spider_register 文件中管道中间件配置情况过滤爬虫设置
    """
    relate_dic = {
        "stickyitem":"Scrapy_Prj.middlewares.spidermiddlewares.itemheaders.ItemHeadersMiddleware",
        "ua":"Scrapy_Prj.middlewares.downloadermiddlewares.randuamiddleware.RandomUserAgent",
        "proxy":"Scrapy_Prj.middlewares.downloadermiddlewares.proxymiddleware.ProxyMiddleware",
        "file":"Scrapy_Prj.pipelines.ossfilepipelines.OssFilesPipeline",
        "file_bak":"Scrapy_Prj.pipelines.ossfilepipelines.OssFilesPipelineBak",
        "img":"Scrapy_Prj.pipelines.ossimgpipelines.OssImagesPipeline",
        "img_bak":"Scrapy_Prj.pipelines.ossimgpipelines.OssImagesPipelineBak",
        "pyppeteer":"gerapy_pyppeteer.downloadermiddlewares.PyppeteerMiddleware",
        "bloom":"Scrapy_Prj.pipelines.bloomerfiler.BloomFilterPipeline",
        "mysql":"Scrapy_Prj.pipelines.mysqlpipelines.MySQLPipeline",
        "mongo":"Scrapy_Prj.pipelines.mongodbPipelines.MongodbPipeline",
        "rabbit":"Scrapy_Prj.pipelines.rabbitmqpipelines.RabbitMQPipeline",
        "kafka":"Scrapy_Prj.pipelines.kafkaPipelines.KafkaPipeline",
        "closespider":"scrapy.extensions.closespider.CloseSpider",
        "fctexcel":"Scrapy_Prj.pipelines.excelpipelines.ExcelFactoryPipeline",
        "dpfexcel":"Scrapy_Prj.pipelines.excelpipelines.ExcelDataplatformPipeline",
        "mailer":"scrapy.extensions.extensions.statsmailer.StatsMailer",
    }
    obj.custom_settings =obj.custom_settings if obj.custom_settings else {}
    # 为防止重复引用,对custom_settings引用源码中scrapy.xcc_管道或中间件置空
    if set(i for i in obj.custom_settings.get("SPIDER_MIDDLEWARES",{}).keys()if i.startswith("scrapy.xcc_")):
        obj.custom_settings["SPIDER_MIDDLEWARES"] = {}
    if set(i for i in obj.custom_settings.get("DOWNLOADER_MIDDLEWARES",{}).keys()if i.startswith("scrapy.xcc_")):
        obj.custom_settings["DOWNLOADER_MIDDLEWARES"] = {}
    if set(i for i in obj.custom_settings.get("ITEM_PIPELINES",{}).keys()if i.startswith("scrapy.xcc_")):
        obj.custom_settings["ITEM_PIPELINES"] = {}
    if set(i for i in obj.custom_settings.get("EXTENSIONS",{}).keys()if i.startswith("scrapy.xcc_")):
        obj.custom_settings["EXTENSIONS"] = {}
    # 取spider_register中开启管道
    obj.custom_settings = dict() if obj.custom_settings is None else obj.custom_settings
    settings_temp = register_settings
    spider_middlewares = {relate_dic[i]  for i in param[1] if isinstance(param[1],tuple)} or {relate_dic[param[1]] for i in param[1] if param[1]} 
    downloader_middlewares = {relate_dic[i]  for i in param[2] if isinstance(param[2],tuple)} or {relate_dic[param[2]] for i in param[2] if param[2]} 
    pipelines = {relate_dic[i]  for i in param[3] if isinstance(param[3],tuple)} or {relate_dic[param[3]] for i in param[3] if param[3]} 
    extensions ={relate_dic[i]  for i in param[4] if isinstance(param[4],tuple)} or {relate_dic[param[4]] for i in param[4] if param[4]} 

    temp_dict = dict()
    temp_dict["SPIDER_MIDDLEWARES"] = obj.custom_settings.get("SPIDER_MIDDLEWARES",{})
    temp_dict["SPIDER_MIDDLEWARES"].update({k:v for k,v in settings_temp.SPIDER_MIDDLEWARES.items() if k in spider_middlewares})
    temp_dict["DOWNLOADER_MIDDLEWARES"] = obj.custom_settings.get("DOWNLOADER_MIDDLEWARES",{})
    temp_dict["DOWNLOADER_MIDDLEWARES"].update({k:v for k,v in settings_temp.DOWNLOADER_MIDDLEWARES.items() if k in downloader_middlewares})
    temp_dict["ITEM_PIPELINES"] = obj.custom_settings.get("ITEM_PIPELINES",{})
    temp_dict["ITEM_PIPELINES"].update({k:v for k,v in settings_temp.ITEM_PIPELINES.items() if k in pipelines})
    temp_dict["EXTENSIONS"] = obj.custom_settings.get("EXTENSIONS",{})
    temp_dict["EXTENSIONS"].update({k:v for k,v in settings_temp.EXTENSIONS.items() if k in extensions})
    obj.custom_settings.update(temp_dict)
    return obj


def spidercls_for_request(spider_loader, request, default_spidercls=None,
                          log_none=False, log_multiple=False):
    """Return a spider class that handles the given Request.

    This will look for the spiders that can handle the given request (using
    the spider loader) and return a Spider class if (and only if) there is
    only one Spider able to handle the Request.

    If multiple spiders (or no spider) are found, it will return the
    default_spidercls passed. It can optionally log if multiple or no spiders
    are found.
    """
    snames = spider_loader.find_by_request(request)
    if len(snames) == 1:
        return spider_loader.load(snames[0])

    if len(snames) > 1 and log_multiple:
        logger.error('More than one spider can handle: %(request)s - %(snames)s',
                     {'request': request, 'snames': ', '.join(snames)})

    if len(snames) == 0 and log_none:
        logger.error('Unable to find spider that handles: %(request)s',
                     {'request': request})

    return default_spidercls


class DefaultSpider(Spider):
    name = 'default'
