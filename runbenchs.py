import sys
import os

thisdir = os.path.dirname(os.path.abspath(__file__))
benchdir = os.path.join(thisdir, "benchmarks")
sys.path.append(benchdir)

import datetime
import argparse
import time

import benchutil

TIMEOUT = 60 * 60.0 # one hour

def add_benchmarks(jobs, interpreter, args):
    for name in ["jittest", "pypy-translate", "pypy-interp", "nx", "bm_sympy", "bm_hypothesis"]:
        cmdline = "%s benchmarks/%s.py -n %s" % (interpreter, name, args.inprocess)
        jobs.append(benchutil.CmdlineJob(name, "bench", int(args.n), cmdline, timeout=TIMEOUT))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help="number of process iterations", default=3)
    parser.add_argument("--inprocess", help="number of in-process iterations", default=10)
    parser.add_argument("interpreters", help="interpreters to use", nargs='*', default=[sys.executable])
    parser.add_argument("--output", help="where to write the results", default=benchutil.now.strftime("output-%G-%m-%dT%H_%M.json"))
    args = parser.parse_args()

    print args.interpreters
    jobs = []
    for interpreter in args.interpreters:
        add_benchmarks(jobs, interpreter, args)
    sched = benchutil.Scheduler(jobs, args.output)
    sched.run()


if __name__ == '__main__':
    main()
