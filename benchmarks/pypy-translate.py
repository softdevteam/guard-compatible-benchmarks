import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pypydir = os.path.join(parentdir, "pypy")
sys.path.append(pypydir)

import pypy
import benchutil
import os
import time

def func():
    from rpython.translator.interactive import Translation
    from rpython.translator.goal import richards
    t = Translation(richards.entry_point, [int])
    t.annotate()
    t.rtype()
    t.backendopt()
    t.source_c()


if __name__ == '__main__':
    benchutil.main(func)
