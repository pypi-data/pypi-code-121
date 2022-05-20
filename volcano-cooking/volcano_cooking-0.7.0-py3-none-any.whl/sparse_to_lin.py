"""CLI to interpolate raw volcanic forcing to npz format.

It takes a filename as a mandatory input parameter.
"""

import os
from typing import List, Optional, Tuple

import click
import numpy as np

import volcano_cooking.helper_scripts as hs


def sparse_to_lin(
    t: np.ndarray,
    sy: Optional[int] = None,
    ey: Optional[int] = None,
    samples_per_year: int = 12,
    remove: int = 1,
) -> Tuple[np.ndarray, List, List]:
    """Re-sample an uneven time axis to one with linear spacing.

    The function returns the new linearly spaced time axis, as well as two
    masks, one for the original time and one for the new time, which makes them
    as equal as possible for the given resolution (resolution is set to 12,
    i.e. months).

    Parameters
    ----------
    t: np.ndarray
        The time axis with uneven time stamps.
    sy: int, optional
        The assumed first year of the time axis
    ey: int, optional
        The assumed end year of the time axis
    samples_per_year: int
        The number of samples per year.
    remove: int
        Remove the number of elements at the end of the time array equal to 'remove'.

    Returns
    -------
    np.ndarray:
        The new linearly spaced time axis
    list:
        Masking of the original time axis that give the time stamps we want to
        keep that match best with the new time axis
    list:
        Masking of the new new time axis that give the time stamps kept from
        the original

    Examples
    --------
    >>> t = np.array(
    >>>     [
    >>>         0, 1e-3, 2e-3, 3e-3, 4e-3, 5e-3, 4, 6, 7.85, 7.91,
    >>>         7.92, 7.925, 7.93, 7.96, 7.99, 8.001, 8.002, 8.003,
    >>>     ]
    >>> )
    >>> t2, t_m, t2_m = sparse_to_lin(t)
    >>> assert t[t_m].shape == t2[t2_m].shape
    Elements are within half a time step from each other: True
    """
    # New time axis (stop at December)
    sy = int(t[0]) if sy is None else sy
    ey = int(t[-1] + 1) if ey is None else ey
    t_i = np.linspace(sy, ey, (ey - sy) * samples_per_year + 1)[
        : -int(remove * samples_per_year / 12)
    ]
    # Find indices in `t_i` that are closest to `t`. If one element in `t_i` is closest
    # to two or more elements in `t`, only the one closest in `t` is kept (avoid
    # repetition of indices).
    # Make `t` a row vector (1, N) and `t_i` a column vector (M, 1), compute the
    # absolute difference -> (M, N) and pick the minimum along N -> (N,)
    mask = np.abs(t[None, :] - t_i[:, None]).argmin(axis=0)
    _, mask_idx = np.unique(mask, return_index=True)
    mask_sections = [mask[m : mask_idx[i + 1]] for i, m in enumerate(mask_idx[:-1])]
    if len(mask_sections) == 0:
        return t_i, [], []
    mask_sections.append(mask[mask_idx[-1] :])
    # Now we find the indices of `t` that we want to keep. `c` works as the index of the
    # first item in each array inside mask_sections
    c = 0
    t_mask: List[int] = []
    t_mask_app = t_mask.append
    ti_mask: List[int] = []
    ti_mask_app = ti_mask.append
    for arr in mask_sections:
        # Find index of t (arr) that is closest to t_i[arr]
        idx = abs(t[c : c + len(arr)] - t_i[arr[0]]).argmin()
        t_mask_app(c + idx)
        ti_mask_app(arr[0])
        c += len(arr)
    closeness = np.allclose(t[t_mask], t_i[ti_mask], atol=1 / (2 * samples_per_year))
    print(f"Elements are within half a time step from each other: {closeness}")
    return t_i, t_mask, ti_mask


@click.command()
@click.argument("filename", type=click.Path(exists=True), required=True)
@click.option(
    "--save/--no-save",
    "-s/-S",
    default=False,
    show_default=True,
    type=bool,
    help="Save the new synthetic forcing array.",
)
@click.option(
    "-sy",
    default=None,
    show_default=True,
    type=int,
    help="Set the starting year.",
)
@click.option(
    "-ey",
    default=None,
    show_default=True,
    type=int,
    help="Set the end year.",
)
@click.option(
    "-spy",
    "--samples-per-year",
    "samples_per_year",
    default=12,
    show_default=True,
    type=int,
    help="Set the number of samples per year.",
)
@click.option(
    "-lm",
    default="Dec",
    show_default=True,
    type=str,
    help="Set the last month using the three first letters.",
)
@click.option(
    "--show/--no-show",
    default=False,
    show_default=True,
    type=bool,
    help="Show an example plot of original and new.",
)
def main(
    filename: str,
    save: bool,
    show: bool,
    sy: int,
    ey: int,
    samples_per_year: int,
    lm: str,
):
    """View a plot of `filename`.

    Parameters
    ----------
    filename: str
        Name of the file you want plotted
    save: bool
        Save the arrays to a .npz file. Defaults to False
    show: bool
        Show a plot of the original and new volcanic forcing arrays
    sy: int
        The assumed first year of the time axis
    ey: int
        The assumed end year of the time axis
    samples_per_year: int
        The number of samples per year.
    lm: str
        The last month of the last year
    """
    # Decide on the last month
    lm = lm.lower()
    # fmt: off
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    # fmt: on
    if lm not in months:
        print(f"{lm} =  is not a valid month. Using 'Dec'...")
        last_month = 1
    else:
        last_month = 13 - months[lm]
    # Grab forcing file with list of timing of volcanic events (uneven in time)
    t, tes = hs.frc_datetime2float(in_file=filename)
    # Remove data points outside of `sy` and `ey`
    if sy is not None:
        tes = tes[t >= sy]
        t = t[t >= sy]
    if ey is not None:
        tes = tes[t <= ey]
        t = t[t <= ey]
    # Get a linspaced time axis and two masks.
    t_i, t_mask, ti_mask = sparse_to_lin(t, sy, ey, samples_per_year, last_month)

    # Create new total emission array with linear sampling in time
    tes_new = np.zeros_like(t_i)
    tes_new[ti_mask] = tes[t_mask]
    if save:
        filebase = os.path.splitext(filename)[0]
        np.savez(f"{filebase}-linspace.npz", times=t_i, data=tes_new)
    if show:
        import matplotlib.pyplot as plt

        plt.plot(t_i, tes_new, "x-", label="Zeros")
        plt.plot(t, tes, "+-", label="Orig")
        plt.plot(t_i[ti_mask], tes[t_mask], "*-r", label="New")
        plt.legend()
        plt.grid()
        plt.show()


def example() -> None:
    """Show an example use of function."""
    # fmt: off
    a = np.array(
        [
            0, 1e-3, 2e-3, 3e-3, 4e-3, 5e-3, 4, 6, 7.85, 7.91,
            7.92, 7.925, 7.93, 7.96, 7.99, 8.001, 8.002, 8.003,
        ]
    )
    # fmt: on
    sparse_to_lin(a)


if __name__ == "__main__":
    example()
