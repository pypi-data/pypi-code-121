

class Context:
    """The context object is responsible for managing the connection with the Zetane engine and holding information about the content of the engine. Because of that, objects are constructed via the context object which ensures they will have the correct socket connection.

    New in v1.7.2: The context can be used as a python context manager, which is the recommended approach when possible.

    Returns:
        Context: An object wrapping the Zetane Engine.
    """
    def __init__(self, host="127.0.0.1", port=4004, socket="", remote=False, append=False, update_on_exit=True):
        pass


    def update(self):
        """ Update all context objects """
        return self


    def plain_launch(self):
        """Launches the Zetane window"""
        return self


    def launch(self):
        """Launches the Zetane window and connects to the socket"""
        return self


    def running(self):
        """Returns whether or not the Zetane window is running.

        Returns:
            Bool: Whether the Zetane process is running or not
        """
        return self


    def address(self):
        """ returns address:port. """
        return self


    def connect(self, refresh=False, retry_connection=True, retries=10):
        """ Attempts connection with the socket. """
        return self


    def disconnect(self):
        """ Disconnect from the socket. """
        return self


    def close(self):
        """ Close the Zetane window and disconnect from the socket. """
        return self


    def debug(self):
        """ Puts the engine into debug mode, stopping at the point this method is called. """
        return self


    def image(self, data=None, filepath=None):
        """The image object holds a reference to an image in the Zetane universe, which is either a 2D representation of numpy data in the format Height x Width x Depth or a string to a filepath.

        Args:
            data (numpy, optional): A numpy array of the format Height x Width x Depth that will be interpreted as a 2D image. Also takes an array of numpy arrays for multiple images.
            filepath (str, optional): A string to an image filepath, or an array of strings for multiple images.

        Returns:
            Image: An object wrapping an image in the Zetane engine.
        """
        return self


    def numpy(self, data=None, filepath=None):
        """The numpy object holds a reference to a tensor object in the zetane engine, which can be visualized in a variety of ways or used to power other graphics principles.

        Args:
            data (numpy, optional): A numpy array of any N dimensions.

        Returns:
            Numpy: A zetane object for a numpy array.
        """
        return self


    def mesh(self, filepath=None):
        """The mesh object holds a reference to a mesh in the Zetane universe.

        Args:
            filepath (str, optional): A string to a mesh filepath.

        Returns:
            Mesh: A zetane object for a mesh.
        """
        return self


    def pointcloud(self, filepath=None):
        """The pointcloud object holds a reference to a pointcloud in the Zetane universe. Supports file formats las, laz, xml, obj, gltf, glb, and ply.

        Args:
            filepath (str): Set the filepath of the pointcloud object.

        Returns:
            PointCloud: Returns a zetane PointCloud object.
        """
        return self


    def vector(self, data=None):
        """ Create a new Zetane Vector object

        .. seealso:: Module :mod: `vector`

            :param data: numpy data or file path to a numpy file (.npy, .npz).
            :type data: str, numpy array.
            :return: Zetane Vector object.
        """
        return self


    def model(self):
        """The model class creates a reference to a machine learning model in the Zetane engine and renders the model architecture. Additionally, the model has data about the model internals and inputs. There are UI elements that allow the model intermediate information to be expanded and explored in order to examine weight and convolutional feature maps.

        Returns:
            Model: A zetane model object
        """
        return self


    def text(self, text=""):
        """The text object holds a reference to renderable text in the Zetane universe. Text has a number of methods that adjust how the text is rendered.

        Args:
            text (str): the text to be displayed in the engine

        Returns:
            Text: A zetane text object
        """
        return self


    def table(self, filepath=None):
        """The table object holds a reference to a table in the Zetane universe. It represents a dataframe in a visual, inspectable way.

        Args:
            filepath (str): Path to a tabular data file (.csv)

        Returns:
            Table: Returns a zetane Table object.
        """
        return self


    def form(self, type="", get_child_data=False):
        """ Create a new form object in Zetane.

        .. seealso:: Module :mod: `form`

            :param type: Form type to search for in Universe
            :param get_child_data: If true, will retrieve all the data in the child forms as well
            :return: Zetane Form object.
        """
        return self


    def chart(self, title='Chart', domain=[0.0, 1.0], range=[0.0, 1.0], visual_type='Line', metrics=[]):
        """Create a new Chart object in Zetane that holds metrics. Charts can be one of a variety of different types.

        Args:
            title (str): the title for the Chart.
            domain (float list): pair of floats containing domain info.
            range (float list): pair of floats containing range info.
            visual_type (str): The method of representation.
            metrics (list of Metrics): metrics contained by the Chart object.

        Returns:
            Chart: a Chart object.
        """
        return self


    def clear_universe(self):
        """ Clear the Zetane universe.

        :return: None
        """
        return self


    def clear(self):
        """ Clear the Zetane universe and invalidate all context objects """
        return self


    def panel(self, name, width=0.10, height=0.10, screen_x=0.0, screen_y=0.0, navigation='3d', depth_priority=1, is_dynamic=True, has_border=True, light=1.0):
        """
        Create a new panel object in Zetane

        Args:
          name (str): title for the panel
          width (float): value representing the screen ratio for the panel to occupy
          height (float): value representing the screen ratio for the panel to occupy
          screen_x (float): value between 0.0 and 1.0 for panel location on screen
          screen_y (float): value between 0.0 and 1.0 for panel location on screen
          navigation (str):  navigation mode; either 'static', '2d', or '3d'.
          depth_priority (int): depth relative to silbing panels (higher values bring the panel forwards)

        Returns:
          Panel: a Panel object
        """
        return self


    def snapshot(self, filename=""):
        return self


    def render(self):
        """Render all objects created in this Zetane context.
        """
        return self


    def save(self, filename):
        """ Save the current context as a .ztn file

        :param filename: path of the .ztn file to be saved
        :return: Save object.
        """
        return self


    def load(self, filename, receiving_panel=None, verbose=True, parse_xml_intelligently=False, parse_api_tags=True, resolve_absolute_path=True):
        """ Load the current context as a .ztn file.

        Retrieved Load object will have handles to every object that was present in the loaded Zetane universe.
        Handles can be accessed trough the .objects() method which returns a dictionary keyed to the unique object names
        Alternatively, users can call .get_objects_sorted_by_name() to get all objects in a list sorted by unique names
        example: `zimg, zmodel, zmodel = zcontext.load(filename).get_objects_sorted_by_name()`
        example: `zimg = zcontext.load(filename).objects()['unique_img_name']`

        .. note::

            * Due to the new loading/saving functionalities it is expected that default-constructed Zobj derived objects have no active logic
            * Ie: their __init__ methods should not actually trigger an update that sends data to Zetane, otherwise we will not be able to retrieve values without side-effects

        :param filename: path of the .ztn file to be loaded
        :param verbose: if True, will print out message when loaded object's name is already taken
        :param parse_xml_intelligently: if True, will parse the .ztn file as an XML. Else simple regex used to parse.
        :param receiving_panel: panel object to contain the loaded .ztn contents
        :param parse_api_tags: if False, will skip parsing object handles.
        :param resolve_abs_path: when True, will resolve the filename's absolute path before sending it to the engine.
        :return: Load object.
        """
        return self


    def is_name_taken(self, name):
        """ returns True if an object in the context has the name."""
        return self
