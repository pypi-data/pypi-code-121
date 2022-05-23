"""ASCII art algorithm implementation."""

from pathlib import Path
import pkg_resources
from string import ascii_letters, digits, punctuation
from typing import Dict, Generator, Optional, Tuple, Union
from typing_extensions import TypeAlias

import nptyping as npt
from numba import jit
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageOps import equalize, grayscale
from tqdm import tqdm


Font: TypeAlias = ImageFont.ImageFont
GrayGrid: TypeAlias = npt.NDArray[npt.Shape['*, *'], npt.UInt8]
ImageType: TypeAlias = Image.Image
MetaPixelGen = Generator[Generator[ImageType, None, None], None, None]

MAX_CHANNEL_VALUE = 255
MAX_INTENSITY_DELTA = 0.1


def draw_char(font: Font, char: str) -> ImageType:
    """
    Draw ASCII character glyph and shrink image to fit the size.

    :param font: Font to draw a character.
    :param char: A character to draw.
    :return: ASCII character glyph.
    """

    image = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(image)
    size = draw.textsize(char, font=font)

    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), char, font=font, fill='black')

    return grayscale(image)


def get_tiles(image: ImageType,
              tile_size: Tuple[int, int],
              ) -> MetaPixelGen:
    """
    Crop an image into tiles of fixed size.

    Right and bottom boundary tiles might be incomplete.

    :param image: Input image to crop.
    :param tile_size: Tile size.
    :return: Image tiles generator.
    """

    width, height = image.size
    tile_width, tile_height = tile_size
    for top in range(0, height, tile_height):
        yield (
            image.crop((left, top, left + tile_width, top + tile_height))
            for left in range(0, width, tile_width)
        )


@jit(fastmath=True)
def score_similarity(lhs: GrayGrid, rhs: GrayGrid) -> np.float64:
    r"""
    Evaluate score similarity between two gray images.

    Get score similarity based on Frobenius matrix norm
    for two gray images represented as 2D numpy arrays,
    i.e. for grayscale matrices :math:`A` and :math:`B` the score is

    .. math::
        -\Vert A - B\Vert_F^2 = -\sum_{i,j} \left(A_{ij} - B_{ij}\right)^2

    :param lhs: Left score operand.
    :param rhs: Right score operand.
    :return: Similarity score.
    """

    return -np.linalg.norm(lhs.astype(np.float64) - rhs.astype(np.float64))


@jit(fastmath=True)
def calculate_intensity(image: GrayGrid) -> float:
    """
    Evaluate intensity value for gray image.

    Intensity is calculated as mean value
    for the gray image represented as 2D numpy array.

    :param image: Input gray image.
    :return: Intensity value.
    """

    return 1 - image.mean() / MAX_CHANNEL_VALUE


class AsciiManager:
    """Manager class for ASCII art transformation and settings storage."""

    def __init__(self,
                 fontname: Optional[Union[str, Path]] = None,
                 fontsize: int = 42,
                 verbose: bool = True):
        """
        Initialize ASCII art transformation manager.

        :param fontname: Font name or path for image approximation, defaults to "courier.ttf".
        :param fontsize: Font size for image approximation.
        :param verbose: Verbosity flag.
        :raises OSError: No access to the requested font.
        """

        if fontname is None:
            fontname = pkg_resources.resource_filename(__name__, 'courier.ttf')
        try:
            font = ImageFont.truetype(fontname, fontsize)
        except OSError:
            raise OSError(f'No access to the requested font {fontname} of size {fontsize}.')

        self.verbose = verbose

        alphabet = ''.join((ascii_letters, digits, punctuation))
        self.chars = {
            char: draw_char(font, char)
            for char in tqdm(
                alphabet,
                desc='Initializing glyphs',
                disable=not self.verbose)
        }

        self.char2intensity = {
            char: calculate_intensity(np.array(glyph))
            for char, glyph in self.chars.items()
        }
        max_intensity = max(self.char2intensity.values())
        self.char2intensity = {
            char: intensity / max_intensity
            for char, intensity in self.char2intensity.items()
        }

    def _find_closest_char(self,
                           image: ImageType,
                           chars: Dict[str, GrayGrid],
                           ) -> str:
        """
        Find a character with a glyph closest to the given image.

        Runs exhaustive search over all the characters.
        Assumes the image and all character glyphs have common shape.
        Closeness is treated in terms of Frobenius matrix norm.
        Characters are filtered by intensity for speed up.

        :param image: Input image to compare with glyphs.
        :param chars: Mapping from characters to grayscaled 2D glyphs.
        :return: Character with the closest glyph.
        """

        grid = np.array(image)
        best_score, best_char = float('-inf'), 'F'
        grid_intensity = calculate_intensity(grid)

        for char, glyph in chars.items():
            delta_intensity = abs(self.char2intensity[char] - grid_intensity)
            if delta_intensity > MAX_INTENSITY_DELTA:
                continue

            score = score_similarity(grid, glyph)
            if score > best_score:
                best_score, best_char = score, char
        return best_char

    @staticmethod
    def _get_tile_size(input_size: Tuple[int, int],
                       output_size: Tuple[int, int],
                       ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        r"""
        Get tile size based on the given input and output image sizes.

        Calculate sizes of tiles :math:`(T_W \times T_H)`
        and tile coverage window :math:`(C_W \times C_H)`
        given input image :math:`(I_W \times I_H)`
        and tiled image :math:`(O_W \times O_H)` sizes.

        .. math::
            \begin{gather*}
            T_W = \left\lfloor \frac{I_W}{O_W} \right\rfloor, \quad
            T_H = \left\lfloor \frac{I_H}{O_H} \right\rfloor  \\
            C_W = O_W * T_W, \quad C_H = O_H * T_H
            \end{gather*}

        :param input_size: Input image size.
        :param output_size: Tiled image size.
        :return: Tile and tile coverage window sizes.
        :raises ValueError: Tiled image size cannot be larger \
            than the original one along any axis or have non-positive size.
        """

        input_width, input_height = input_size
        output_width, output_height = output_size

        if not (0 < output_width <= input_width and 0 < output_height <= input_height):
            raise ValueError('Tiled image size cannot be larger '
                             'than the original one along any axis '
                             'or have non-positive size.')
        tile_width = input_width // output_width
        tile_height = input_height // output_height

        cover_width = output_width * tile_width
        cover_height = output_height * tile_height

        return (tile_width, tile_height), (cover_width, cover_height)

    def _process_image_rowspan(self,
                               metapixels: MetaPixelGen,
                               resized_chars: Dict[str, GrayGrid],
                               output_size: Tuple[int, int],
                               ) -> str:
        """
        Process an image cropped into metapixels and transform it into ASCII art.

        :param metapixels: Image tiles generator.
        :param resized_chars: Mapping from characters to grayscaled 2D glyphs.
        :param output_size: Output ASCII art size in form (width, height).
        :return: String containing ASCII art.
        """

        _, output_height = output_size
        return '\n'.join(
            ''.join(
                self._find_closest_char(metapixel, resized_chars)
                for metapixel in row
            )
            for row in tqdm(
                metapixels,
                total=output_height,
                desc='Processing ASCII art rows',
                disable=not self.verbose,
            )
        )

    def transform(self, image: ImageType, output_size: Tuple[int, int]) -> str:
        """
        Transform an image into an ASCII art via glyph similarity scoring.

        :param image: Input image to transform.
        :param output_size: Output ASCII art size in form (width, height).
        :return: String containing ASCII art.
        :raises ValueError: Output ASCII art cannot be larger \
            than the original one along any axis or have non-positive size.
        """

        try:
            pixel_size, cover_size = AsciiManager._get_tile_size(image.size, output_size)
        except ValueError:
            raise ValueError('Output ASCII art cannot be larger '
                             'than the original one along any axis '
                             'or have non-positive size.')

        image = equalize(grayscale(image).resize(cover_size))

        metapixels = get_tiles(image, pixel_size)
        resized_chars = {
            char: np.array(glyph.resize(pixel_size))
            for char, glyph in self.chars.items()
        }

        return self._process_image_rowspan(metapixels, resized_chars, output_size)
