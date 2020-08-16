from enum import Enum


class TestEnum(Enum):
    A, B = range(2)  # PATCH: A, B, C = range(3)


def test_before():
    assert "C" not in TestEnum.__members__


def test_after():
    assert "C" in TestEnum.__members__
