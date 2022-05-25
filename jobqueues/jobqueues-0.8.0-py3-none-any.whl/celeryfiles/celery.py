from __future__ import absolute_import, unicode_literals
from jobqueues.celeryqueue import CeleryQueue


q = CeleryQueue(_checkWorkers=False)
app = q._app

if __name__ == "__main__":
    app.start()
