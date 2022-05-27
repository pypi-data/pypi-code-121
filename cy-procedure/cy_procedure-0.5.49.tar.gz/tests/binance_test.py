from cy_procedure.subject.crawler.config_reader import *
from cy_data_access.connection.connect import *

connect_db_env(db_name=DB_CRAWLER)
print(BinanceFutureCrawlerConfigReader().configs)
print(len(BinanceFutureCrawlerConfigReader().configs))
