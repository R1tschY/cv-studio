import importlib
import os
import re
import sys
import shutil
from pathlib import Path

import pytest
from pyhotreload.xreload import xreload

filetests = Path(__file__).parent / "filetests"


def pytest_generate_tests(metafunc):
    if "testfile" in metafunc.fixturenames:

        tests = []
        with os.scandir(filetests) as iter:
            for entry in iter:
                tests.append(entry)

        metafunc.parametrize(
            "testfile", tests, ids=lambda p: os.path.splitext(p.name)[0])


def test_xreload(pypackage, testfile: os.DirEntry):
    test_name = os.path.splitext(testfile.name)[0]
    pkg = f"pyhotreload_tests_{test_name}"
    testfile_path = Path(pypackage) / pkg / testfile.name

    # create module
    os.mkdir(Path(pypackage) / pkg)
    (Path(pypackage) / pkg / "__init__.py").write_bytes(b"")
    shutil.copy(testfile.path, testfile_path)

    # import mod
    oldmod = importlib.import_module(f"{pkg}.{test_name}")
    test_after = oldmod.test_after
    if hasattr(oldmod, "test_before"):
        oldmod.test_before()

    # patch
    content = testfile_path.read_text(encoding="utf-8")
    content = re.sub(r"^([ ]*)(.*)#[ ]*PATCH:(.*)$",
                     lambda m: m.group(1) + m.group(3).strip(),
                     content,
                     flags=re.MULTILINE)
    testfile_path.write_text(content, encoding="utf-8")

    # reload
    xreload(oldmod)

    # test
    test_after()
