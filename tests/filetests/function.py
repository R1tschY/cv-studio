
def function():
    return 0  # PATCH: return 42


def test_before():
    assert function() == 0


def test_after():
    assert function() == 42
