# SymPy for symbolic operations
from sympy import *

# Enable pretty LATEX printing to show equations
init_printing()

x, y, z = symbols('x y z')
expr = 2*x + y

# Pretty print, instead of normal print
pprint(expr)


d = diff(sin(x)*exp(x), x)
pprint(d)

q = integrate(d*cos(x), x)

pprint(q)
