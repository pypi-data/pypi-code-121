

class Panel:
    """
      A panel object sets up an area on the screen dedicated to
      either a 2D or 3D navigable space, available for the user
      to add content to.

      Args:
          name (str): title for the panel
          width (float): value representing the screen ratio for the panel to occupy
          height (float): value representing the screen ratio for the panel to occupy
          screen_x (float): value between 0.0 and 1.0 for panel location on screen
          screen_y (float): value between 0.0 and 1.0 for panel location on screen
          navigation (str):  navigation mode; either 'static', '2d', or '3d'.
          depth_priority (int): layer number (greater == higher priority)
          is_dynamic (bool): ability to re-size and re-position the panel.
          has_border (bool): add a border to the panel.
          light (float): content brightness.

      Returns:
          Panel: a Panel object
      """
    def __init__(self, nsocket, name, width, height, screen_x, screen_y, navigation, depth_priority, is_dynamic=True, has_border=True, light=1.0):
        pass


    def set_panel_name(self, name):
        """
        Sets the name of the panel form

        Args:
            name (str): name of the panel form.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_width(self, width):
        """
        Sets the width of this panel in Zetane Engine.

        Args:
            width (float): panel width as a fraction of parent panel width.
            At 1.0, this panel will have the same width as its parent panel.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_height(self, height):
        """
        Sets the height of this panel in Zetane Engine.

        Args:
            height (float): panel height as a fraction of parent panel height.
            At 1.0, this panel will have the same height as its parent panel.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_screen_X(self, screen_x=0.0):
        """
        The bottom left corner is the panel's origin point. This function sets the x position of the origin as a fraction of the parent panel's width.

        Args:
            screen_x (float): panel location on screen; as a fraction of parent panel width. Negative values and values greater than 1 are allowed, placing the origin outside the boundaries of the parent panel. Default 0.0.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_screen_Y(self, screen_y=0.0):
        """
        The bottom left corner is the panel's origin point. This function sets the y position of the origin as a fraction of the parent panel's height.

        Args:
            screen_y (float): panel location on screen; as a fraction of parent panel height.Negative values and values greater than 1 are allowed, placing the origin outside the boundaries of the parent panel. Default 0.0.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_navigation_mode(self, mode: str = None):
        """
        Sets the navigation mode of the panel.

        Args:
            mode (str): navigation mode. One of:
             'static': no navigation; useful for HUDs and overlays
             '2d': mouse navigation in XY is enabled
             '3d': mouse navigation in XYZ is enabled

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_depth_order(self, priority: int = 0):
        """
       Sets the depth order of this panel in relation to sibling panels.
       Sibling panels share the same parent panel. The default depth is 0.
       Higher values bring the panel forward. Siblings that share the same
       depth value will be stacked in the same order they were created.

        Args:
            priority(int): layer number (greater == brings panel forward).

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def dynamic(self, is_dynamic=True):
        """
        Decides whether the panel can be dynamically re-sized and re-positioned in
        the zetane engine.

        TODO: this function will be deprecated soon; with its functionality moving to
        set_panel_controls.

        Args:
            is_dynamic (bool): ability to re-size and re-position the panel.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def movable(self, movable: bool = False):
        return self


    def maximizable(self, maximizable: bool = False):
        """
            Enable layout controls to maximize/minimize this panel.

        Args:
            maximizable (bool): determines whether the panel can be maximized

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_background_color(self, rgb: tuple = None):
        """ Sets a background color.

        Args:
            rgb (tuple): RGB color for the panel background.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_background_gradient(self, top_left: tuple = None, top_right: tuple = None, bottom_left: tuple = None, bottom_right: tuple = None):
        """ Sets a 4-corner color gradient for the panel background. Corners with unspecified colors will use a default built-in color dependending on the
          current theme.

            Args:
                top_left (tuple): RGB color for the top left corner.
                top_right (tuple): RGB color for the top right corner.
                bottom_left (tuple): RGB color for the bottom left corner.
                bottom_right (tuple): RGB color for the bottom right corner.

            Returns:
                Panel: Returns this object so calls can be chained.

          """
        return self


    def set_background_image(self, image_path: str = None):
        """ Sets a background image, stretched to fit the panel.

            Args:
                image_path (str): file path to an image (jpg, png, bmp, etc.).

            Returns:
                Panel: Returns this object so calls can be chained.
          """
        return self


    def set_background_alpha(self, alpha: float = 1.0):
        """ Sets the background's opacity.

        Args:
            alpha (float): value in range [0.0, 1.0], where 0.0 is transparent,
            and 1.0 is opaque. Values outside this range will be clamped.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def remove_background(self):
        """ Removes the panel's background. The depth buffer will not be cleared
        and the panel will not contribute any UUID to the screen. Improves performance.
        Useful for null panels used purely for organization as middle nodes for
        layout heirarchy; without interactivity features like camera/navigation.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def border(self, pixels: int = 1.0):
        """
        Adds an inner outline to the panel.

        Args:
            pixels (bool): border thickness, in pixels.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_border_color(self, rgb=None):
        """ Sets a border color.

        Args:
            rgb (tuple): RGB color for the panel border. To enable the border, call 'border(pixels)' with a value > 0.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_border_alpha(self, alpha=1.0):
        """ Sets the border's opacity.

        Args:
            alpha (float): value in range [0.0, 1.0], where 0.0 is transparent,
            and 1.0 is opaque. Values outside this range will be clamped.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def set_camera(self, position: tuple = None, aim: tuple = None):
        """ Sets up the panel's camera.

        Args:
          position (tuple): XYZ position of the camera.
          aim (tuple): XYZ position of the camera aim.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def content_brightness(self, intensity=1.0):
        """
        Change the default brightness of the content in the panel.
        Does not affect the background nor any sibling or child panels.

        Args:
            intensity (float): brightness of panel content. Default is 1.0.

        Returns:
            Panel: Returns this object so calls can be chained.
        """
        return self


    def update(self, debug=False):
        return self
