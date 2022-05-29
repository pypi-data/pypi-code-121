from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class ModelImages(Function):
    """Export images of an HBJSON file."""

    hbjson_file = Inputs.file(
        description='HBJSON file.',
        path='input.hbjson'
    )

    image_type = Inputs.str(
        description='Choose the type of image file.'
        'Choose from: png, jpg, ps, tiff, bmp, pnm.',
        default='png',
        spec={'type': 'string',
              'enum': ['png', 'jpg', 'ps', 'tiff', 'bmp', 'pnm']}
    )

    image_width = Inputs.int(
        description='Width of images in pixels. If set to 0, x dimension of a radiance'
        ' view will be used.',
        default=0
    )

    image_height = Inputs.int(
        description='Height of images in pixels.If set to 0, y dimension of a radiance'
        ' view will be used.',
        default=0
    )

    background_color = Inputs.str(
        description='Background color for the images as a string of rgb values.',
        default='255 255 255'
    )

    model_display_mode = Inputs.str(
        description='Set display mode for the model.'
        'Choose from: shaded, surface, surfacewithedges, wireframe, points.',
        default='shaded',
        spec={'type': 'string',
              'enum': ['shaded', 'surface', 'surfacewithedges', 'wireframe', 'points']}
    )

    grid_options = Inputs.str(
        description='Export sensor grids as either points or meshes.'
        ' Choose from: ignore, points, meshes. Choosing ignore will not load grids.',
        default='ignore',
        spec={'type': 'string',
              'enum': ['ignore', 'points', 'meshes']}
    )

    grid_display_mode = Inputs.str(
        description='Set display mode for the Sensorgrids.'
        'Choose from: shaded, surface, surfacewithedges, wireframe, points',
        default='shaded',
        spec={'type': 'string',
              'enum': ['shaded', 'surface', 'surfacewithedges', 'wireframe', 'points']}
    )

    triangle_angle = Inputs.int(
        description='Set the internal angle of the triangles in case'
        ' radial-grid is selected from grid options.', default=45
    )

    triangle_radius = Inputs.float(
        description='Set the radial height of the triangles in meters in case'
        ' radial-grid is selected from grid options.', default=1.0
    )

    config_path = Inputs.path(
        description='File path to the config json file to load additional simulation data.',
        path='config.json',
        optional=True
    )

    @command
    def model_images(self):
        return 'honeybee-vtk export model-images input.hbjson --folder target_folder'\
            ' --config config.json --image-type {{self.image_type}}'\
            '--image-width {{self.image_width}}'\
            ' --image-height {{self.image_height}}'\
            ' --background-color {{self.background_color}}'\
            ' --model-display-mode {{self.model_display_mode}} --grid-options'\
            ' {{self.grid_options}} --grid-display-mode {{self.grid_display_mode}}'\
            '--triangle-angle {{self.triangle_angle}}' \
            ' --triangle-radius {{self.triangle_radius}}'\

    images = Outputs.folder(
        description='Folder location where the images are exported.',
        path='target_folder'
    )


@dataclass
class GridImages(Function):
    """Export images of the grids in an HBJSON file."""

    hbjson_file = Inputs.file(
        description='HBJSON file.',
        path='input.hbjson'
    )

    image_type = Inputs.str(
        description='Choose the type of image file.'
        'Choose from: png, jpg, ps, tiff, bmp, pnm.',
        default='png',
        spec={'type': 'string',
              'enum': ['png', 'jpg', 'ps', 'tiff', 'bmp', 'pnm']}
    )

    image_width = Inputs.int(
        description='Width of images in pixels. If not set, x dimension of a radiance'
        ' view will be used.',
        default=0
    )

    image_height = Inputs.int(
        description='Height of images in pixels.If not set, y dimension of a radiance'
        ' view will be used.',
        default=0
    )

    background_color = Inputs.str(
        description='Background color for the images as a string of rgb values.',
        default='255 255 255'
    )

    grid_options = Inputs.str(
        description='Export sensor grids as either points, meshes, or radial-grids.'
        ' Choose from: ignore, points, meshes. Choosing ignore will not load grids.',
        default='ignore',
        spec={'type': 'string',
              'enum': ['ignore', 'points', 'meshes', 'radial-grid']}
    )

    grid_display_mode = Inputs.str(
        description='Set display mode for the Sensorgrids.'
        'Choose from: shaded, surface, surfacewithedges, wireframe, points',
        default='shaded',
        spec={'type': 'string',
              'enum': ['shaded', 'surface', 'surfacewithedges', 'wireframe', 'points']}
    )

    config_path = Inputs.path(
        description='File path to the config json file which can be used to mount'
        'simulation data on HBJSON.',
        path='config.json',
        optional=True
    )

    grid_filter = Inputs.str(
        description='Filter for the grids to be exported using a regex pattern.'
        'If not set, all grids will be exported.',
        default='*',
    )

    full_match = Inputs.str(
        description='A flag to indicate if the grids should be filtered by their'
        ' identifiers as full matches.',
        default='no-full-match',
        spec={'type': 'string', 'enum': ['full-match', 'no-full-match']}
    )

    results_folder = Inputs.folder(
        description='Path to results folder for visualization.',
        path='results'
    )

    @command
    def grid_images(self):
        return 'honeybee-vtk export grid-images input.hbjson --folder target_folder'\
            ' --config config.json --image-type {{self.image_type}}'\
            ' --image-width {{self.image_width}} --image-height {{self.image_height}}'\
            ' --background-color {{self.background_color}} --grid-options'\
            ' {{self.grid_options}} --grid-display-mode {{self.grid_display_mode}}'\
            ' --grid-filter "{{self.grid_filter}}" --{{self.full_match}}'

    images = Outputs.folder(
        description='Folder location where the images are exported.',
        path='target_folder'
    )


@dataclass
class TimeStepImages(Function):
    """Export images of the grids in an HBJSON file."""

    hbjson_file = Inputs.file(
        description='HBJSON file.',
        path='input.hbjson'
    )

    config_path = Inputs.path(
        description='File path to the config json file which can be used to mount'
        'simulation data on HBJSON.',
        path='config.json',
    )

    results_folder = Inputs.folder(
        description='Path to results folder for visualization.',
        path='results'
    )

    time_step_path = Inputs.path(
        description='File path to the time step data json file that has the information'
        ' needed to export time step images.',
        path='time_step_data.json',
    )

    grid_filter = Inputs.str(
        description='Filter for the grids to be exported using a regex pattern.'
        'If not set, all grids will be exported.',
        default='*',
    )

    full_match = Inputs.str(
        description='A flag to indicate if the grids should be filtered by their'
        ' identifiers as full matches.',
        default='no-full-match',
        spec={'type': 'string', 'enum': ['full-match', 'no-full-match']}
    )

    label_images = Inputs.str(
        description='Flag to indicate whether to label images or not. A label is a'
        ' timestep information that is added to the bottom center of the image. If the'
        ' exported images are going to be post-processed, it is advised to not label'
        ' the images.',
        default='no-label',
        spec={'type': 'string', 'enum': ['label', 'no-label']}
    )

    image_width = Inputs.int(
        description='Width of images in pixels. If not set, x dimension of a radiance'
        ' view will be used.',
        default=0
    )

    image_height = Inputs.int(
        description='Height of images in pixels.If not set, y dimension of a radiance'
        ' view will be used.',
        default=0
    )

    @command
    def time_step_images(self):
        return 'honeybee-vtk export time-step-images input.hbjson --folder target_folder'\
            ' --config config.json --time-step-file time_step_data.json'\
            ' --grid-filter "{{self.grid_filter}}" --{{self.full_match}}'\
            ' --{{self.label_images}}'\
            ' --image-width {{self.image_width}} --image-height {{self.image_height}}'\

    images = Outputs.folder(
        description='Folder location where the images are exported.',
        path='target_folder'
    )
