from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class Gif(Function):
    """Export a GIF from a folder of time step images."""

    input_folder = Inputs.folder(
        description='The folder containing the time step images using the'
        ' time-step-images sub-command of the honeybee-vtk export command.',
        required=True,
        path='time_step_images'
    )

    transparency = Inputs.str(
        description='A flag to indicate whether to use gradient transparency or a flat'
        ' transparency in GIF composition.',
        default='no-gradient-transparency',
        spec={'type': 'string', 'enum': [
            'gradient-transparency', 'no-gradient-transparency']}
    )

    duration = Inputs.int(
        description='The duration of each frame in the GIF in milliseconds. Defaults to'
        ' 1000ms.',
        default=1000
    )

    loop_count = Inputs.int(
        description='The number of times to loop the GIF. Default is 0 (infinite).',
        default=0
    )

    linger_last_frame = Inputs.int(
        description='The multiple of duration to linger the last frame of the GIF.'
        ' Defaults to 3.',
        default=3
    )

    @command
    def gif(self):
        return 'honeybee-vtk post-process gif ./time_step_images --folder target_folder'\
            ' --{{self.transparency}} --duration {{self.duration}}'\
            ' --loop-count {{self.loop_count}} --linger-last-frame'\
            ' {{self.linger_last_frame}}'

    images = Outputs.folder(
        description='Folder location where the images are exported.',
        path='target_folder'
    )


@dataclass
class TransparentImages(Function):
    """Export overlappable transparent images from a folder of time step images."""

    time_step_images_folder = Inputs.folder(
        description='The folder containing the time step images.',
        required=True,
        path='time_step_images'
    )

    transparency = Inputs.float(
        description='The transparency value to use. Acceptable values are decimal'
        ' point numbers between 0 and 1 inclusive. 0 is completely transparent and 1'
        ' is completely opaque. Defaults to 0.5.',
        default=0.5,
    )

    @command
    def create_transparent_images(self):
        return 'honeybee-vtk post-process transparent-images ./time_step_images'\
            ' --folder target_folder --transparency {{self.transparency}}'

    images = Outputs.folder(
        description='Folder location where the images are exported.',
        path='target_folder'
    )
