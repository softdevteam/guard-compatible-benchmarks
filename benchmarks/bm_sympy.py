import benchutil
benchutil.add_external_path("sympy-1.0")
benchutil.add_external_path("mpmath-0.19")

from sympy import expand, symbols, integrate, tan, summation
from sympy.core.cache import clear_cache

def bench_expand():
    x, y, z = symbols('x y z')
    expand((1+x+y+z)**20)

def bench_integrate():
    x, y = symbols('x y')
    f = (1 / tan(x)) ** 10
    return integrate(f, x)

def bench_sum():
    x, i = symbols('x i')
    summation(x**i/i, (i, 1, 400))

def bench_str():
    x, y, z = symbols('x y z')
    str(expand((x+2*y+3*z)**30))

def func():
    bench_expand()
    clear_cache()
    bench_integrate()
    clear_cache()
    bench_sum()
    clear_cache()
    bench_str()
    clear_cache()

if __name__ == '__main__':
    benchutil.main(func)
