import argparse
import os, shutil
import json
import subprocess
import filecmp
import datetime
import time
import sys
import threading
import signal

from collections import deque, defaultdict

try:
    import pypyjit
except ImportError:
    pypyjit = None

RESULTS = "RESULTS"

now = datetime.datetime.now()

def get_metadata():
    return dict(
        version=sys.version,
        executable=sys.executable,
        time=str(now),
    )

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help="number of iterations", default=50)
    parser.add_argument("--count-executed-lines", help="count the lines executed by the benchmark", action='store_true')
    return parser

def count_lines(func):
    import sys
    import collections

    count = collections.defaultdict(int)

    def trace_calls(frame, event, arg):
        if event != 'line':
            return trace_calls
        lineno = frame.f_lineno
        code = frame.f_code
        filename = code.co_filename
        count[filename, lineno] += 1
        return trace_calls
    print "counting lines"
    sys.settrace(trace_calls)
    func()
    sys.settrace(None)
    print RESULTS
    print dict(count)

def extra_info():
    if pypyjit is None:
        return {}
    result = dict(asm_memory=pypyjit.get_stats_asmmemmgr()[1])
    snap = pypyjit.get_stats_snapshot()
    result.update(snap.counters)
    for name, tim in snap.counter_times.items():
        result[name + "_TIME"] = tim
    return result

def extract_extra_info(d, info1, info2):
    if pypyjit is None:
        return
    for key, value in info2.iteritems():
        d[key] = value - info1[key]

def main(func):
    parser = make_parser()
    args = parser.parse_args()

    if args.count_executed_lines:
        count_lines(func)
        return

    times = []
    for i in range(int(args.n)):
        info1 = extra_info()
        t1 = time.time()
        func()
        t2 = time.time()
        info2 = extra_info()
        d = {"runtime": t2 - t1, "iteration": i}
        extract_extra_info(d, info1, info2)
        times.append(d)
    print RESULTS
    print json.dumps(times, indent=4)

# ____________________________________________________________
def avg(l):
    return sum(l) / len(l)

class BenchError(Exception):
    pass

class Scheduler(object):
    def __init__(self, jobs, outfile):
        self.torun = deque(jobs)
        self.done = []
        self.errors = []
        self.metadata = get_metadata()
        self.outfile = outfile

    def run(self):
        try:
            starttime = time.time()
            t1 = starttime
            while self.torun:
                job = self.torun.popleft()
                try:
                    job.run()
                except BenchError, e:
                    print "a benchmark failed, disabling:"
                    print e
                    self.done.append(job)
                else:
                    if not job.done():
                        self.torun.append(job)
                    else:
                        self.done.append(job)
                t2 = time.time()
                job.add_job_time(t2 - t1)
                print "elapsed: %0.2f min, this job: %0.2f min, remaining: %0.2f min (estimated)" % (
                        (t2 - starttime) / 60, (t2 - t1) / 60, self.time_remaining() / 60)
                self.dump_results("intermediate")
                t1 = t2
        except BaseException, e:
            self.dump_results("error")
            raise
        self.dump_results("final")

    def dump_results(self, status="final"):
        results = defaultdict(list)
        for job in self.done + list(self.torun):
            group, res = job.get_results()
            results[group].append(res)
        d = dict(status=status, metadata=self.metadata, results=results)
        with file(self.outfile, "w") as f:
            json.dump(d, f, sort_keys=True, indent=2)


    def time_remaining(self):
        return sum(job.time_remaining() for job in self.torun)


class Job(object):
    # default estimate: 1 min, randomly
    all_estimates = [60]

    def __init__(self, name, group, numruns):
        self.name = name
        self.group = group
        self.numruns = numruns
        self.results = []
        self.estimates = []
        self.results = []

    def add_job_time(self, t):
        self.estimates.append(t)
        self.all_estimates.append(t)

    def done(self):
        return len(self.results) >= self.numruns

    def get_results(self):
        return self.results

    def run(self):
        result = self.really_run()
        self.results.append(result)

    def really_run(self):
        raise NotImplementedError("abstract")

    def time_remaining(self):
        if not self.estimates:
            est = avg(self.all_estimates)
        else:
            est = avg(self.estimates)
        return est * (self.numruns - len(self.estimates))



class CmdlineJob(Job):
    def __init__(self, name, group, numruns, cmdline, workingdir=None, timeout=None):
        Job.__init__(self, name, group, numruns)
        self.cmdline = cmdline
        self.workingdir = workingdir
        self.timeout = timeout

    def get_results(self):
        return self.group, dict(
                name=self.name, cmdline=self.cmdline,
                results=self.results)

    def really_run(self):
        if self.workingdir is not None:
            old = os.getcwd()
            os.chdir(self.workingdir)
        t = None
        try:
            if self.timeout is None:
                self._run_subprocess()
            else:
                def run():
                    self._run_subprocess(threaded=True)
                t = threading.Thread(target=run)
                t.start()
                t.join(self.timeout)
                if t.is_alive(): # timeout
                    print "timeout, killing"
                    # kill using process groups, to make sure not only the
                    # shell dies
                    self._kill()
                    raise BenchError("A benchmark timed out", self.cmdline)
            pipe = self._process
            if pipe.returncode != 0:
                raise BenchError("A benchmark failed to run", self.cmdline, self._results)
            results = self.parse_results(self._results)
            return results
        finally:
            if t is not None and t.is_alive():
                # eg a KeyboardInterrupt
                self._kill()
            self._process = None
            self._results = None
            if self.workingdir is not None:
                os.chdir(old)

    def _kill(self):
        os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
        time.sleep(1)
        try:
            os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
        except OSError:
            pass

    def _run_subprocess(self, threaded=False):
        print((">>> Running: cmdline=%s") %
                (self.cmdline, ))
        pipe = subprocess.Popen(
                self.cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, preexec_fn=os.setpgrp)
        self._process = pipe
        self._results = pipe.communicate()[0]


    def parse_results(self, results):
        lines = results.splitlines()
        index = lines.index(RESULTS)
        if index == -1:
            raise BenchError("Wrong format of results: %s" % result)
        return json.loads("\n".join(lines[index + 1:]))
