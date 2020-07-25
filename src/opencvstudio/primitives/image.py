from dataclasses import dataclass
from typing import Optional, Tuple

import numpy
from opencvstudio.primitives.color import ColorSpace


ImageData = numpy.ndarray


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


@dataclass(frozen=True)
class ImageSpec:
    size: Tuple[int, int]
    color: ColorSpace
