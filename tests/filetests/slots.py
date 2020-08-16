
class Class:
    __slots__ = ("abc",)  # PATCH: __slots__ = ("abc", "def")


def test_before():
    assert Class.__slots__ == ("abc",)


def test_after():
    assert Class.__slots__ == ("abc", "def")
