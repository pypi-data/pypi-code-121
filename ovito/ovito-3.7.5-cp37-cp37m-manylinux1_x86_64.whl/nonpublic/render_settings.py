from . import RenderSettings

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_custom_range(self):
    """
    Specifies the range of animation frames to render if :py:attr:`range` is set to ``CustomInterval``.

    :Default: ``(0,100)``
    """
    return (self.custom_range_start, self.custom_range_end)
def _set_RenderSettings_custom_range(self, range):
    if len(range) != 2: raise TypeError("Tuple or list of length two expected.")
    self.custom_range_start = range[0]
    self.custom_range_end = range[1]
RenderSettings.custom_range = property(_get_RenderSettings_custom_range, _set_RenderSettings_custom_range)

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_size(self):
    """
    The size of the image or movie to be generated in pixels.

    :Default: ``(640,480)``
    """
    return (self.output_image_width, self.output_image_height)
def _set_RenderSettings_size(self, size):
    if len(size) != 2: raise TypeError("Tuple or list of length two expected.")
    self.output_image_width = size[0]
    self.output_image_height = size[1]
RenderSettings.size = property(_get_RenderSettings_size, _set_RenderSettings_size)

# Here only for backward compatibility with OVITO 2.9.0:
def _get_RenderSettings_filename(self):
    """
    A string specifying the file path under which the rendered image or movie should be saved.

    :Default: ``None``
    """
    if self.save_to_file and self.output_filename: return self.output_filename
    else: return None
def _set_RenderSettings_filename(self, filename):
    if filename:
        self.output_filename = filename
        self.save_to_file = True
    else:
        self.save_to_file = False
RenderSettings.filename = property(_get_RenderSettings_filename, _set_RenderSettings_filename)
