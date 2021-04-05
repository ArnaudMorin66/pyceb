from sympy.solvers import solve
from sympy import Symbol, symbols
x,a,b,c,d = symbols('x,a,b,c,d')
sol = solve(a*x**3+2*b*x**2+c*x+d,x)
print(sol)
