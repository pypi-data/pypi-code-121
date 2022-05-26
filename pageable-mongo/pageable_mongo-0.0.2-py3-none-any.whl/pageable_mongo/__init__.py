__version__ = "0.0.2"

import math

class Pageable():

  def __init__(self, mongo):
    self.mongo      = mongo
    self.collection = None
    self.match      = None
    self.projection = None
    self.sort_on    = None
    self.order      = 1
    self.skip_to    = 0
    self.limit_to   = 0

  def __getitem__(self, collection):
    self.collection = self.mongo[collection]
    return self

  def __getattr__(self, attr):
    if attr in self.mongo.list_collection_names():
      return self[attr]
    if self.collection is None:
      return getattr(self.mongo, attr)
    else:
      return getattr(self.collection, attr)

  def find(self, match, projection=None):
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

  @property
  def result(self):
    return self._pageable(list(self.collection.aggregate(self.query))[0])

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

  def _pageable(self, result):
    try:
      total = result["totalElements"]
    except KeyError:
      total = 0
    sorting        = bool(self.sort_on)
    paged          = bool(self.skip_to) or bool(self.limit_to)
    resultset_size = len(result["content"])

    result["pageable"] = {
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

    result["first"]            = self.skip_to < self.limit_to
    result["last"]             = ( total - self.skip_to ) < self.limit_to
    result["totalPages"]       = math.ceil(total / self.limit_to) if self.limit_to else 0
    result["numberOfElements"] = resultset_size
    result["number"]           = self.skip_to
    result["size"]             = self.limit_to
    result["empty"]            = resultset_size == 0
    result["sort"]             = {
      "sorted"   : sorting,
      "unsorted" : not sorting,
      "empty"    : resultset_size == 0
    }
    return result
