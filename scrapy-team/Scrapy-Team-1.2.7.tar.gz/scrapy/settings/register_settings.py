# 爬虫中间件 ItemHeadersMiddleware 结合 oss下载中间键使用 添加请求头参数
SPIDER_MIDDLEWARES = {
    "Scrapy_Prj.middlewares.spidermiddlewares.itemheaders.ItemHeadersMiddleware":300
}

# 下载中间件配置参数
DOWNLOADER_MIDDLEWARES = {
    "gerapy_pyppeteer.downloadermiddlewares.PyppeteerMiddleware":540,
    'Scrapy_Prj.middlewares.downloadermiddlewares.randuamiddleware.RandomUserAgent': 543,
    'Scrapy_Prj.middlewares.downloadermiddlewares.proxymiddleware.ProxyMiddleware': 888,
}

# 阿里云文件管道以及存储管道设置参数
ITEM_PIPELINES = {
    'Scrapy_Prj.pipelines.ossimgpipelines.OssImagesPipeline': 200,
    'Scrapy_Prj.pipelines.ossimgpipelines.OssImagesPipelineBak': 201,
    'Scrapy_Prj.pipelines.ossfilepipelines.OssFilesPipeline': 300,
    'Scrapy_Prj.pipelines.ossfilepipelines.OssFilesPipelineBak': 301,
    'Scrapy_Prj.pipelines.bloomerfiler.BloomFilterPipeline': 399,
    'Scrapy_Prj.pipelines.mysqlpipelines.MySQLPipeline': 400,
    'Scrapy_Prj.pipelines.mongodbPipelines.MongodbPipeline': 450,
    'Scrapy_Prj.pipelines.rabbitmqpipelines.RabbitMQPipeline': 500,
    'Scrapy_Prj.pipelines.excelpipelines.ExcelFactoryPipeline': 550,
    'Scrapy_Prj.pipelines.excelpipelines.ExcelDataplatformPipeline': 550,
    # 'Scrapy_Prj.pipelines.influxdbpipelines.SpiderStatLogging': 600,
}

# 拓展中间件
EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider': 500, # CLOSESPIDER_TIMEOUT/CLOSESPIDER_ERRORCOUNT/CLOSESPIDER_ITEMCOUNT设置运行时间停止、错误个数停止或者item数量停止等
}