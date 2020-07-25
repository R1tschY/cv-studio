from enum import Enum


class ColorSpace(str, Enum):
    GRAY = "GRAY"

    RGB = "RGB"
    RGBA = "RGBA"

    BGR = "BGR"


