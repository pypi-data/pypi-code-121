__version__ = "0.1.0"

import math

class Pageable():

  def __init__(self, mongo):
    self.mongo       = mongo
    self.collections = {}

  def __getitem__(self, collection):
    try:
      return self.collections[collection]
    except KeyError:
      self.collections[collection] = PageableCollection(self.mongo[collection])
    return self.collections[collection]

  def __getattr__(self, attr):
    return self[attr]

class PageableCollection():

  def __init__(self, collection):
    self.collection = collection
    self.match      = None
    self.projection = None
    self.sort_on    = None
    self.order      = 1
    self.skip_to    = 0
    self.limit_to   = 0
    self.result     = {}

  def _reset(self):
    self.match      = None
    self.projection = None
    self.sort_on    = None
    self.order      = 1
    self.skip_to    = 0
    self.limit_to   = 0
    self.result     = {}

  def __getattr__(self, attr):
    return getattr(self.collection, attr)

  def find(self, match, projection=None):
    self._reset()
    self.match     = match
    self.projection = projection
    return self

  def sort(self, sort_on, order=1):
    self.sort_on = sort_on
    self.order   = order
    return self

  def skip(self, skip_to):
    self.skip_to = skip_to
    return self

  def limit(self, limit_to):
    self.limit_to = limit_to
    return self

  @property
  def query(self):
    return [
      { "$match": self.match },
      { "$facet": {
        "resultset": self._paginate(),
        "total": [
          { "$count": "count" }
        ]
      }},
      { "$project" : {
        "resultset" : "$resultset",
        "total"     : { "$arrayElemAt": [ "$total", 0] }
      }},
      { "$project" : {
        "content"       : "$resultset",
        "totalElements" : "$total.count"
      }}
    ]

  def __iter__(self):
    # execute, cache
    self.result = list(self.collection.aggregate(self.query))[0]
    # return iter to results
    return iter(self.result["content"])

  def _paginate(self):
    query = []
    if self.projection:
      query.append({ "$project" : self.projection })
    if self.sort_on:
      query.append({ "$sort"  : { self.sort_on : self.order }})
    if self.skip_to:
      query.append({ "$skip"  : self.skip_to })
    if self.limit_to:
      query.append({ "$limit" : self.limit_to })
    return query

  def __len__(self):
    try:
      return self.result["totalElements"]
    except KeyError:
      pass
    return 0

  @property
  def pageable(self):
    total          = len(self)
    sorting        = bool(self.sort_on)
    paged          = bool(self.skip_to) or bool(self.limit_to)
    resultset_size = len(self.result["content"])

    stats = {
      "sort": {
        "sorted"   : sorting,
        "unsorted" : not sorting,
        "empty"    : resultset_size == 0
      },
      "offset"     : self.skip_to,
      "pageNumber" : int(self.skip_to / self.limit_to) if self.limit_to else 0,
      "pageSize"   : self.limit_to,
      "paged"      : paged,
      "unpaged"    : not paged
    }

    stats["first"]            = self.skip_to < self.limit_to
    stats["last"]             = ( total - self.skip_to ) < self.limit_to
    stats["totalPages"]       = math.ceil(total / self.limit_to) if self.limit_to else 0
    stats["numberOfElements"] = resultset_size
    stats["number"]           = self.skip_to
    stats["size"]             = self.limit_to
    stats["empty"]            = resultset_size == 0
    stats["sort"]             = {
      "sorted"   : sorting,
      "unsorted" : not sorting,
      "empty"    : resultset_size == 0
    }
    return stats
