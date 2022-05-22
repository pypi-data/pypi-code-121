from matplotlib import pyplot as plt
import numpy as np
from sympy import re


def NewtonRaphson(f, f_deriv, x0, error=0.001, iterations=1000):
    '''
    The formula for this function is given as
        x_new = x_old - f'(x_old)/f(x_old)

    f : f(x) - The function whose root is needed. x is the independent variable.

    f_deriv : derivative of the given function.

    x0 : initial value for starting the iterations.

    error: maximum difference to tolerate between x_{n+1} and x_n to consider x_n as a root of f.
           By default, it is 0.001

    iterations : No. of iterations for the function. By default, it is 1000.
    '''

    x = x0  # Initial value of parameter

    for i in range(iterations):
        y_x = f(x)  # Value of the function at x
        y_deriv_x = f_deriv(x) # Value of the derivative of the function at x

        if y_deriv_x == 0: # Check if derivative of y at x = 0
            y_deriv_x += 10**(-15)
        x_new = x - (y_x / y_deriv_x)  # Calculate x_new

        if abs(x_new - x) <= error: break  # If x_new - x <= tolerance error, break and return result

        x = x_new  # X gets updated for next iteration

    return print(f'An estimate of the root of the function: {x_new}. \n Number of iterations: {i}')


# Secant method for solving for root if a non linear equation




class SecantMethod():
    '''
    This class returns the root of an equation using the Secant Method

    **Input parameters:**

    - func: f(x) The function whose root is needed
    - guess1 : initial first guess
    - guess2: initial second guess
    
    NOTE: The guesses don't need to be on the opposite sides of the root like bisection method 
    but can be on the same side as well.
    - iterations: No. of iterations to carry for the method
    - tolerance : maximum difference between solutions obtained by consecutuve iterations for that 
    iteration to be considered as a root.
    NOTE: This tolerance should be small for a good root.

    **Returns**
    <1> Upon calling, the class returns the following attributes:
    - guess 1
    - guess 2
    - the function
    - no. of iterations
    - tolerance
    - Number of iterations required for the solution

    <2> Upon calling, The class returns the following methods:
    - The solution upon calling the .solve() method

    '''

    def __init__(self, func, guess1, guess2, iterations, tolerance):
        # Parameters
        self.x1 = guess1
        self.x2 = guess2
        self.func = func
        self.iterations = iterations
        self.tolerance = tolerance
    
    def solve(self):
        for i in range(self.iterations):

            # Checking is denominator is ever 0 and if it is, answer = 0
            numerator = (self.x2 - self.x1)*self.func(self.x2)
            denominator = (self.func(self.x2)-self.func(self.x1))
            if denominator == 0: 
                self.required_iterations = 1
                return 0
            # xn = x2 - (x2-x1)/(f2-f1) according to formula
            x_new = self.x2 - (numerator/denominator)
            err = abs(x_new - self.x2)

            # Checking for error with tolerance level
            if err <= self.tolerance: 
                break
            else:
                # Loop gets updated for next iteration
                self.x1 = self.x2
                self.x2 = x_new
        
        # If error is greater than tolerance even after given number of iterations, function throws warning.
        if err > self.tolerance:
            return 'Warning! Convergence failure'
        
        else:
            self.required_iterations = i # Number of required iterations
            return x_new # Ans






if __name__ == '__main__':
    
    def func1(x):
        return x**2 + 4*x + 4
    def deriv1(x):
        return 2*x + 2
    x = np.linspace(-100, 100, 1000)
    plt.style.use(['science', 'notebook', 'grid'])
    plt.plot(x, func1(x))
    plt.show()
    # Secant method
    root_finder = SecantMethod(func = func1, guess1=-5, guess2 = -3, iterations=20000, tolerance=0.00000001)
    print(f'Secant root = {root_finder.solve()}')
    required_iterations = root_finder.required_iterations
    print(required_iterations)



    # Newton Raphson Method
    sol_newton = NewtonRaphson(f = func1, f_deriv= deriv1, x0 = 1, error = 0.0000000001, iterations=20000)
