from pydaisi import Daisi
from pprint import pprint
import time

p = Daisi("gkhi")


res = p.hello()
pprint(res.last_status)
pprint(res.get_status())
pprint(res.fetch_value())
pprint(res.results)
pprint(res.value_fetched)

res2 = p.dispatch("goodbye","you")
pprint(res2.last_status)
while True:
    pprint(res2.get_status())
    time.sleep(1)
    if res2.last_status == "FINISHED":
        break
pprint(res2.value)