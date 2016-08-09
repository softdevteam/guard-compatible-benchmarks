import os, sys, shutil, glob
import zipfile
import urllib

import contextlib
import os

DEBUG = True

@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

def section(s):
    print "======"
    print s

def copy(pattern, dest):
    fn = None
    for fn in glob.glob(pattern):
        shutil.copy(fn, dest)
    if DEBUG and fn is None:
        print "nothing matched when copying", pattern, dest

def remove_if_exists(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif DEBUG:
        print "can't remove", path

def system(cmd):
    if DEBUG:
        print "running:", cmd
        print "in:", os.getcwd()
    exit = os.system(cmd)
    if DEBUG and exit:
        print "exitcode %s of %s" % (exit, cmd)
    return exit
# ____________________________________________________________
# cleaning everything

def distclean():
    remove_if_exists('pypy')

# ____________________________________________________________
# cleaning build outputs

def clean():
    pass


# ____________________________________________________________
# download files


def download():
    checkout_stuff()

def checkout_stuff():
    section("cloning PyPy")
    system("hg clone https://bitbucket.org/pypy/pypy -u guard-compatible")

def build_pypy():
    with working_directory("pypy/pypy/goal"):
        cmdline = "../../rpython/bin/rpython"
        if system("pypy --version") != 0:
            # no pypy on the path:
            cmdline = "python " + cmdline
        cmdline = "%s -Ojit --no-shared targetpypystandalone.py" % (cmdline, )
        system(cmdline)


def build():
    section("building PyPy")
    build_pypy()

# ____________________________________________________________
# run benchmarks

def runbench():
    pass

def quickbench():
    pass

# ____________________________________________________________
# make pdf

def makepdf():
    pass

# ____________________________________________________________
commands = set("download build clean distclean runbench quickbench makepdf".split())

USAGE = "usage: python make.py <download | build | clean | distclean | runbench | quickbench | makepdf>"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print USAGE
    elif sys.argv[1] in commands:
        globals()[sys.argv[1]]()
    else:
        print "unknown command", sys.argv[1]
        print USAGE

