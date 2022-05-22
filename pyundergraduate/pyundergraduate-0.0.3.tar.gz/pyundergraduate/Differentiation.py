'''
differentiation using finite difference method for forward diff, backward diff and central diff
 Derivatives are given till 4th order derivative however, the solution functions may be differentiated again to get still higher
derivatives
'''


import numpy as np



class FiniteDiff():
    '''
    **Input Parameters:**
    -f: Function whose differention is needed
    -h: step size. Usually small
    NOTE: too small a h can cause the results to diverge

    **Returns:**
    <1> Attributes:
    - The function
    - The step size

    <2> Methods:
    - Differentiation upto 4th derivative using Forward first differences- A function
    - Differentiation upto 4th derivative using backward first differences- A function
    - Differentiation upto 4th derivative using central first differences- A function
    NOTE: The function isn't limited to the 4th order derivative. Higher order derivatives can be found by differentiating the 
          the first order derivatives or higher order derivatives over and over again.

    Functions are provided as output for every function and these can be used to evaluate the derivative at all points.
    '''
    def __init__(self, func, h): #x_pts):
        self.func = func   #Differentiating functoion
        self.h = h  # step size


    # Forward differences
    def Forward_First_Deriv(self):
        def f_first_deriv(x):
            return (self.func(x+self.h) - self.func(x))/self.h
        return f_first_deriv
    
    def Forward_Second_Deriv(self):
        def f_second_deriv(x):
            return (self.func(x+2*self.h) - 2*self.func(x + self.h) + self.func(x))/self.h**2
        return f_second_deriv
        
    def Forward_Third_Deriv(self):
        def f_third_deriv(x):
            return (self.func(x + 3*self.h) - 3*self.func(x + 2*self.h) + 3*self.func(x + self.h) - self.func(x))/self.h**3
        return f_third_deriv

    def Forward_Fourth_Deriv(self):
        def f_fourth_deriv(x):
            return (self.func(x + 4*self.h) - 4*self.func(x+3*self.h) + 6*self.func(x + 2*self.h) - 4*self.func(x + self.h) + self.func(x))/self.h**4
        return f_fourth_deriv

    
    
    # Backward differences
    def Backward_First_Deriv(self):
        def b_first_deriv(x):
            return (self.func(x) - self.func(x - self.h))/self.h
        return b_first_deriv
    
    def Backward_Second_Deriv(self):
        def b_second_deriv(x):
            return (self.func(x) - 2*self.func(x - self.h) + self.func(x - 2*self.h))/self.h**2
        return b_second_deriv
        
    def Backward_Third_Deriv(self):
        def b_third_deriv(x):
            return (self.func(x) - 3*self.func(x - self.h) + 3*self.func(x - 2*self.h) - self.func(x - 3*self.h))/self.h**3
        return b_third_deriv

    def Backward_Fourth_Deriv(self):
        def b_fourth_deriv(x):
            return (self.func(x) - 4*self.func(x - self.h) + 6*self.func(x - 2*self.h) - 4*self.func(x - 3*self.h) + self.func(x - 4*self.h))/self.h**4
        return b_fourth_deriv

    # Central differences
    def Central_First_Deriv(self):
        def central_first_deriv(x):
            return (self.func(x + self.h) - self.func(x - self.h))/(2*self.h)
        return central_first_deriv
    
    def Central_Second_Deriv(self):
        def central_second_deriv(x):
            return (self.func(x + self.h) - 2*self.func(x) + self.func(x - self.h))/self.h**2
        return central_second_deriv
        
    def Central_Third_Deriv(self):
        def central_third_deriv(x):
            return (self.func(x + 2*self.h) - 2*self.func(x + self.h) + 2*self.func(x - self.h) - self.func(x - 2*self.h))/(2*self.h**3)
        return central_third_deriv

    def Central_Fourth_Deriv(self):
        def central_fourth_deriv(x):
            return (self.func(x + 2*self.h) - 4*self.func(x + self.h) + 6*self.func(x) - 4*self.func(x - self.h) + self.func(x - 2*self.h))/self.func**4
        return central_fourth_deriv











if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    f = lambda x: np.sin(x)
    g = lambda x: np.cos(x)
    x_pts = np.linspace(0, 10, 100000)

    h = .005
    plt.style.use(['science', 'grid', 'notebook'])

    differentiator = FiniteDiff(func = f, h = h)
    fd1 = differentiator.Forward_Fourth_Deriv()
    bc1 = differentiator.Backward_Third_Deriv()
    c1 = differentiator.Central_Third_Deriv()

    plt.plot(x_pts, fd1(x_pts), label = 'forward')
    plt.plot(x_pts, bc1(x_pts), label = 'backward')
    plt.plot(x_pts, c1(x_pts), label = 'central')

    plt.legend()
    plt.show()