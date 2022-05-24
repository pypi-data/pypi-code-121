from .mc_fetcher import mc_fetch
from .et_fetcher import et_fetch
from .bs_fetcher import bs_fetch
import ray

class Fetcher:
    def __init__(self):
        self.data = self.fetch()

    def fetch(self):
        data = []

        mc = mc_fetch.remote()
        et = et_fetch.remote()
        bs = bs_fetch.remote()
        mc_data, et_data, bs_data = ray.get([mc, et, bs])
        for i in mc_data:
            data.append(i)
        for i in et_data:
            data.append(i)
        for i in bs_data:
            data.append(i)
        
        return data