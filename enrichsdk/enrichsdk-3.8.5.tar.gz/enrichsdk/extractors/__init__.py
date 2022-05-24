"""
Extractors
^^^^^^^^^^

Classes to support querying of datasets from database.

Implementation of this class for SQLite is in enrich-scribble assets.

"""


class ExtractorBase(object):
    """
    Baseclass for an engine to query datasets

    """

    def __init__(self, conf, *args, **kwargs):
        self.conf = conf

    def get_metadata(self):
        """
        Get metdata for the dataset specified
        """
        raise Exception("Implement in subclass")

    def get_collections_metadata(self, table):
        """
        Get metdata for a given table

        Args:
          table (str): Collection whose metadata is required
        """
        raise Exception("Implement in subclass")

    def get_attributes_metadata(self, filterargs):

        """
        Get attribute information for a given dataset

        Args:
          filterargs (dict): Collection and other information
             {
               'table': 'XYA'
             }

        """
        raise Exception("Implement in subclass")

    def query_by_spec(self, spec, filterargs):
        """
        Specify an abstract query in spec and scope
        in the filter args (table, output columns)

        Args:
          spec (dict): Specification of the query
          filterargs (dict): Has table and output columns
        """
        raise Exception("Implement in subclass")

    def query_raw(self, query):
        """
        Specify a raw to be executed. This reqires that
        the caller has an idea of what the dataset looks
        like and how to compute

        Args:
          query (object): Any object that the engine can accept
        """
        raise Exception("Implement in subclass")
