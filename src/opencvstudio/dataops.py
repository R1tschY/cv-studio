import os
from pathlib import Path
from typing import Union

import cv2
from opencvstudio.primitives import Box, ImageData
from opencvstudio.primitives.color import ColorSpace
from opencvstudio.primitives.error import ImageOperationError


def open_image(path: Union[str, Path]) -> ImageData:
    img = cv2.imread(str(path))
    if img is None:
        raise IOError(f"Failed to load image at {path}")
    return img


def crop(img: ImageData, box: Box) -> ImageData:
    return img[box.y:box.y+box.height, box.x:box.x+box.width]


def convert_color(
        img: ImageData, from_: ColorSpace, to: ColorSpace) -> ImageData:
    conv = getattr(cv2, f"COLOR_{from_}2{to}")
    if conv is not None:
        return cv2.cvtColor(img, conv)
    else:
        raise ImageOperationError(
            f"No color convertion from {from_} to {to} supported")


def can_convert_color(from_: ColorSpace, to: ColorSpace) -> bool:
    return hasattr(cv2, f"COLOR_{from_}2{to}")
