
class Class:

    def method(self):
        return 0  # PATCH: return 42


def test_before():
    assert Class().method() == 0


def test_after():
    assert Class().method() == 42
