from dataclasses import dataclass
from typing import Tuple

import numpy
from opencvstudio.dataops import convert_color
from opencvstudio.primitives.color import ColorSpace


class Image:
    def __init__(self, image_data: numpy.ndarray, color: ColorSpace):
        self._data = image_data
        self._color = color

    def replace_data(self, data: numpy.ndarray) -> "Image":
        """
        Replace data without changing color space.
        """
        return Image(data, self._color)

    def replace_color_data(self, data: numpy.ndarray,
                           color: ColorSpace) -> "Image":
        """
        Replace data and color space.
        """
        return Image(data, color)

    @property
    def size(self) -> Tuple[int, int]:
        """
        :return: Size of image
        """
        return self._data.shape

    @property
    def data(self) -> numpy.ndarray:
        """
        :return: Data of image
        """
        return self._data

    @property
    def color(self) -> ColorSpace:
        """
        :return: Data of image
        """
        return self._color

    def convert_color(self, color: ColorSpace) -> "Image":
        if self._color != color:
            return Image(
                convert_color(self._data, self._color, ColorSpace.RGB),
                ColorSpace.RGB)
        else:
            return self


@dataclass(frozen=True)
class ImageSpec:
    size: Tuple[int, int]
    color: ColorSpace
