from sympy import symbols, integrate, simplify, exp, Function, diff, solveset, log, S,oo, sin, I 

class my_func(Function): 
    @classmethod
    def eval(cls, x):
        if x.is_Number: 
            if x is S.Zero: 
                return S.One 
            elif x is S.Infinity: 
                return S.Zero
    def _eval_is_real(self): 
        return self.args[0].is_real
x = S('x')
print(my_func(0)+sin(0))
print(my_func(oo))
print(my_func(3.54).n())
print(my_func(I).is_real)