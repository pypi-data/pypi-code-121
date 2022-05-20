"""
Sprite Module. Contains the class
which is used to store a game element's sprite.
"""

from os.path import basename, isdir
from typing import List

from ..color import Color, ColorsDict
from ..consts import CUSTOMEXT, abs_path
from ..files import count_files, path_join

FramesList = List[ColorsDict]


class Sprite:
    """
    The sprite of an element.
    """

    def __init__(self, folder_path: str) -> None:
        """
        Initializes an instance of 'Sprite'.

        'folder_path' should be a folder path relative to the 'textures' package.
        """

        subpackage, *name = folder_path.rsplit('/', 1)
        if not name:
            name = subpackage
            subpackage = None
        else:
            name = name[0]
            subpackage = subpackage.replace('/', '.')

        realpath = abs_path(name, ("textures" + (f".{subpackage}" if subpackage else '')))

        if not isdir(realpath):
            raise ValueError(f"'{folder_path}' is not a directory.")

        self._width: int = 0
        self._height: int = 0
        self._frames: FramesList = []
        self.current_frame_index: int = 0

        spr_name = basename(realpath)
        frames = count_files(realpath, CUSTOMEXT)

        for frame in range(1, len(frames) + 1):

            fr_path = path_join(realpath, f"{spr_name}_{frame:03d}.{CUSTOMEXT}")
            with open(fr_path,
                      mode='r',
                      encoding="utf-8") as file:

                pixels: ColorsDict = {}
                pix_x = pix_y = -1

                for line in file:
                    sep = line.split()
                    sep_str = ''.join(sep)
                    sep_size = len(sep)

                    # get rid of all whitespace and check comments
                    if not sep_str or sep_str.startswith('#'):
                        continue

                    if sep_size == 2: # It's the sprite dimensions
                        wid, hei = sep

                        if (not self._width) and (not self._height):
                            self._width, self._height = int(wid), int(hei)

                        if (not self._width == int(wid)) or (not self._height == int(hei)):
                            raise Exception("The dimensions of the frames are not the same.")

                        continue

                    if not sep_size % 4 == 0:
                        raise Exception("One of the lines has an invalid amount of values.")

                    # by now we are sure this is a row of pixels
                    pix_y += 1


                    for elem in range(0, sep_size, 4):
                        pix_x += 1
                        rgba = sep[elem:elem+4]

                        for i, comp in enumerate(rgba):
                            if comp == '-':
                                rgba[i] = None
                            else:
                                rgba[i] = int(comp)

                        alpha = rgba[3]
                        if alpha and (alpha > 0):
                            red, green, blue, alpha = rgba
                            color = Color(red, green, blue, int(alpha / 255 * 100))
                        else:
                            color = None

                        pixels[(pix_x, pix_y)] = color

                    pix_x = -1

                self.frames.append(pixels)


        if not self._frames:
            raise ValueError("There must be at least 1 frame.")


    @property
    def width(self) -> int:
        """
        Returns the width of the sprite.
        """

        return self._width


    @property
    def height(self) -> int:
        """
        Returns the height of the sprite.
        """

        return self._height


    @property
    def frames(self) -> FramesList:
        """
        Returns all the frames of the sprite.
        """

        return self._frames


    @property
    def current_frame(self) -> ColorsDict:
        """
        Returns the current frame of the sprite.
        """

        return self.frames[self.current_frame_index]


    def is_first(self) -> bool:
        """
        Checks if the current frame is the first one.
        """

        return self.current_frame_index == 0


    def is_last(self) -> bool:
        """
        Checks if the current frame is the last one.
        """

        return self.current_frame_index == (len(self.frames) - 1)


    def previous_frame(self, circular: bool=True) -> None:
        """
        Makes the current frame of the sprite be the previous.

        `circular` means if it should cycle back to the first
        one in case of being the last.
        """

        if circular:
            self.current_frame_index = (self.current_frame_index - 1) % len(self.frames)
            return

        self.current_frame_index -= (0 if self.is_first() else 1)


    def next_frame(self, circular: bool=True) -> None:
        """
        Makes the current frame of the sprite be the next.

        `circular` means if it should cycle back to the first
        one in case of being the last.
        """

        if circular:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            return

        self.current_frame_index += (0 if self.is_last() else 1)
