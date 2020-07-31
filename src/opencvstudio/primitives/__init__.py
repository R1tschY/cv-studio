from dataclasses import dataclass
from typing import Tuple, Union

import numpy


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_size(cls, size: Union["Size", Tuple[int, int]]):
        return cls(0, 0, size[0], size[1])

    def __str__(self):
        return f"{self.x}x{self.y}x{self.width}x{self.height}"


@dataclass(frozen=True)
class Size:
    width: int
    height: int

    def __str__(self):
        return f"{self.width}x{self.height}"


@dataclass(frozen=True)
class RgbColor:
    r: int
    g: int
    b: int

    def __str__(self):
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"


@dataclass(frozen=True)
class RgbaColor:
    r: int
    g: int
    b: int
    a: int

    def __str__(self):
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"


ImageData = numpy.ndarray
