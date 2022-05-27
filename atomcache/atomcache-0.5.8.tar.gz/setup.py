# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['atomcache']

package_data = \
{'': ['*']}

install_requires = \
['aioredis>=2.0.0,<3.0.0', 'fastapi>=0.61.2,<0.62.0']

setup_kwargs = {
    'name': 'atomcache',
    'version': '0.5.8',
    'description': 'Asynchronous cache manager designed for horizontally scaled web applications.',
    'long_description': '## Introduction\nAsynchronous cache manager designed for horizontally scaled web applications.\n**NOTE:** _Currently has implementation only for FastAPI using Redis._\n\n## Requirements\n\nPython 3.7+\n\n* <a href="https://aioredis.readthedocs.io" class="external-link" target="_blank">aioredis</a> for cache implementation.\n* <a href="https://fastapi.tiangolo.com" class="external-link" target="_blank">FastAPI</a> for the web parts.\n  \n## Installation\n\n<div class="termy">\n\n```console\n$ pip install atomcache\n\n---> 100%\n```\n\n## Explanation schema\n\n![Class Diagram](http://www.plantuml.com/plantuml/proxy?src=https://raw.githubusercontent.com/pysergio/atomcache/master/README.md)\n\n<details markdown="1">\n<summary>As UML</summary>\n\n```plantuml\n@startuml\n    !theme materia\n    participant Redis\n    participant Instance_A as A\n    participant Instance_B as B\n    participant Instance_N as C\n\n\n    B <-> Redis: GET: Cache=null & GET: Lock=null\n\n    B <-> Redis: SET: Lock = true\n\n    activate B #Red\n    A <--> Redis: GET: Cache=null & GET: Lock=true\n    activate A #Transparent\n    C <--> Redis: GET: Cache=null & GET: Lock=true\n    activate C #Transparent\n    B <--> B: Do the computation\n    B -> Redis: SET: Cache={...}\n    deactivate B\n\n    group Notify Cache SET\n        Redis -> C\n        Redis -> A\n    end\n    group GET Cache\n        Redis <-> C\n    deactivate C\n        Redis <-> A\n    deactivate A\n    end\n@enduml\n```\n</details>\n\n## Examples:\n\n### Usage as FastAPI Dependency\n\n* Create a file `events.py` with:\n\n```Python\nfrom typing import Optional, Callable\n\nimport aioredis\nfrom fastapi import FastAPI, Depends\nfrom atomcache import Cache\n\n\ndef create_start_app_handler(app: FastAPI) -> Callable:\n    async def start_app() -> None:\n        redis: aioredis.Redis = await aioredis.from_url(url="redis://localhost", encoding="utf-8")\n        await Cache.init(app, redis)\n\n    return start_app\n\n\ndef create_stop_app_handler(app: FastAPI) -> Callable:\n    async def stop_app() -> None:\n        await Cache.backend.close()\n\n    return stop_app\n```\n\n* Create a file `main.py` with:\n\n```Python\nfrom typing import Optional\n\nfrom fastapi import FastAPI, Depends\nfrom atomcache import Cache\n\nfrom .events import create_start_app_handler, create_stop_app_handler\n\napp = FastAPI()\n\napp.add_event_handler("startup", create_start_app_handler(app))\napp.add_event_handler("shutdown", create_stop_app_handler(app))\n\n\n@router.get("/resources", response_model=List[TheResponseModel], name="main:test-example")\nasync def resources(offset: int = 0, items: int = 10, cache: Cache = Depends(Cache(exp=600)):\n    cache_id = f"{offset}-{items}"  # Build cache identifier\n    await cache.raise_try(cache_id)  # Try to respond from cache\n    response = await db.find(TheResponseModel, skip=offset, limit=items)\n    await asyncio.sleep(10)  # Do some heavy work for 10 sec, see `lock_timeout`\n    return cache.set(response, cache_id=cache_id)\n```\n\n### Direct cache usage for avoiding repetitive calling on external resources:\n\n```Python\nfrom aiohttp import ClientSession\nfrom atomcache import Cache\n\ncache = Cache(exp=1200, namespace="my-namespace:")\n\n\nasync def requesting_helper(ref: str) -> List[dict]:\n    cached_value = await cache.get(cache_id=ref)\n    if cached_value is not None:\n        return cached_value\n\n    async with ClientSession() as session:\n        async with session.get(f"https://external-api.io/{ref}") as response:\n            if response.ok:\n                cached_value = response.json()\n                return cache.set(cached_value, cache_id=ref)\n    return []\n```\n',
    'author': 'Serghei Ungurean',
    'author_email': 'srg.ungurean@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pysergio/atomcache',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
