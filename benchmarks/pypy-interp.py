import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pypydir = os.path.join(parentdir, "pypy")
sys.path.append(pypydir)

import pypy
import benchutil
import os
import time

from pypy.tool.pytest.objspace import gettestobjspace
space = gettestobjspace()

def func():
    w_l = space.appexec([], """():
        class A(object):
            def __init__(self, x):
                self.x = x
        l = []
        a, b = 1, 1
        for i in range(5000):
            l.append((i, a, str(i), float(i), {i: a}, A(b)))
            a, b = b, a + b
        print len(l)
        return l
    """)

if __name__ == '__main__':
    benchutil.main(func)
