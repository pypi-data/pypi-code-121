import matplotlib.pyplot as plt
import os
import typing as ty

from strax import exporter as strax_exporter

export, __all__ = strax_exporter()


@export
def save_canvas(name: str,
                save_dir: str = './figures',
                dpi: int = 200,
                tight_layout: bool = False,
                pickle_dump: bool = False,
                other_formats: ty.Union[ty.List[str], None] = None,
                ) -> None:
    """
    Wrapper for saving current figure. Saves to PNG by default and also
    adds pdf and svg formats

    :param name: How to name the figure (no extension required)
    :param save_dir: Base where to store figures
    :param dpi: dots per inch for saving the option
    :param tight_layout: if true use plt.tight_layout
    :param pickle_dump: DEPRECATED option
    :param other_formats: other formats to save in (by default svg and pdf)
    :return: None
    """
    assert not pickle_dump, "Allowing pickle dumps is deprecated"
    if other_formats is None:
        other_formats = 'pdf svg'.split()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir + '/.')
    for sub_folder in other_formats:
        sub_dir = os.path.join(save_dir, sub_folder)
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
    if tight_layout:
        plt.tight_layout()

    plt.savefig(f"{save_dir}/{name}.png", dpi=dpi, bbox_inches="tight")

    for extension in other_formats:
        plt.savefig(
            os.path.join(
                save_dir,
                extension,
                f'{name}.{extension}'),
            dpi=dpi,
            bbox_inches="tight")
