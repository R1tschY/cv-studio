
def function():  # PATCH: def function(arg):
    return 0  # PATCH: return arg


def test_before():
    assert function() == 0


def test_after():
    assert function(42) == 42
