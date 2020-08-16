import sys

import pytest


@pytest.fixture()
def pypackage(tmpdir):
    tmpdir_str = str(tmpdir)
    sys.path.append(tmpdir_str)
    yield tmpdir
    sys.path.remove(tmpdir_str)
