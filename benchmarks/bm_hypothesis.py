import benchutil
benchutil.add_external_path("hypothesis-3.4.2/src/")
benchutil.add_external_path("enum34-1.1.6/")

import hypothesis
import hypothesis.strategies
import random
import operator

settings = hypothesis.settings(database=None, timeout=-1)

def func():
    def large_mostly_non_overlapping(xs):
        hypothesis.assume(xs)
        hypothesis.assume(all(xs))
        union = reduce(operator.or_, xs)
        return len(union) >= 30

    result = hypothesis.find(
        hypothesis.strategies.lists(hypothesis.strategies.sets(hypothesis.strategies.integers())),
        large_mostly_non_overlapping, settings=settings)
    union = reduce(operator.or_, result)
    assert len(union) == 30
    assert max(union) == min(union) + len(union) - 1
    for x in result:
        for y in result:
            if x is not y:
                assert not (x & y)

if __name__ == '__main__':
    benchutil.main(func)
