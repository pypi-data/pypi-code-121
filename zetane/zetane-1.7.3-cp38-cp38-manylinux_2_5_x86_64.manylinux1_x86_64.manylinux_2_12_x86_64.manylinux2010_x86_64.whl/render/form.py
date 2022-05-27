

class Form:
    """ The Form objects allows us to retrieve dynamically from the Zetane 'universe'. The Zetane universe is composed of a scene tree that is queryable in several different ways.

    Args:
        nsocket (Socket): Socket to communicate with the Zetane Engine
        type (string): The type of the object we will search for in the Zetane Engine. See the above example for how this works with the Zetane universe.
        get_child_data (bool): Sets a property whether to query objects owned by the searched for object in the scene tree.

    Example:
        If our tree is composed like the following:

        >>>
        <universe>
          <vertex />
        </universe>

        We can query for the vertex object using `Form(type='vertex')`
    """
    def __init__(self, nsocket, type="", get_child_data=False):
        pass


    def update(self):
        return self


    def has_received(self):
        return self


    def get_received_data(self):
        """
        Gets the zobject returned by the query
        """
        return self


    def get_values(self, timeout=10):
        """
            Gets values associated with the queried object. Blocks the thread
            until the values are retreived or the query times out.
            The query is guaranteed to happen at least once, regardless of
            timeout value.

        Args:
            timeout (float): period in seconds to wait for the retreival to be complete.

        Returns:
            queried object values; or None on timeout.
        """
        return self


    def get_words(self, timeout=10):
        """
        Gets 'words', which are strings associated with the queried object
        """
        return self


    def get_subforms(self):
        """
        Gets any objects that are owned by the queried objects. These are child nodes of the current object.
        """
        return self


    def get_parent(self):
        """
        Gets the parent of the queried node in the scene tree.
        """
        return self
