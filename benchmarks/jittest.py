import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pypydir = os.path.join(parentdir, "pypy")
testfile = os.path.join(pypydir, "rpython", "jit", "metainterp", "test", "test_recursive.py")
sys.path.append(pypydir)

import pytest
import pypy
import benchutil
import os
import time



def func():
    pytest.main([testfile])


if __name__ == '__main__':
    benchutil.main(func)
