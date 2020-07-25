from dataclasses import dataclass
from typing import Tuple, Union


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_size(cls, size: Union["Size", Tuple[int, int]]):
        return cls(0, 0, size[0], size[1])


@dataclass(frozen=True)
class Size:
    width: int
    height: int


@dataclass(frozen=True)
class RgbColor:
    r: int
    g: int
    b: int


@dataclass(frozen=True)
class RgbaColor:
    r: int
    g: int
    b: int
    a: int
