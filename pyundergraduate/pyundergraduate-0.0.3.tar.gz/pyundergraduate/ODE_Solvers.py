# Euler function to solve a differential equation of 1st, 2nd and 3rd order numerically using Euler's formula.

from cProfile import label
from matplotlib import pyplot as plt
plt.style.use(['science', 'notebook', 'grid'])

def euler(f, ics, step_size, x1):
    ''' 
    This function solves ODEs upto 3rd Order
    **Input variables:**
    f :

    - If a 1st order differential equation is required to solve,
                  f is differential equation of the form :
                   dy/dx = f(y, x)

    - If a 2nd order ODE is required to  be solved then f = du/dx(u, y, x) where
        u is dy/dx, i.e the first order derivative of the dependent variable with respect to the
        independent variable.

    - If a 3rd order ODE is required to be solved then f = dv/dx(v, u, y, x) where v = y''(x), i.e, the second derivative
        of the dependent variable w.r.t to the independent variable and u = y'(x), i.e the first derivative of the
        dependent variable with respect to the independent variable.

    ics: Initial conditions which should contain atleast 2(including x0, which is compulsory) of:
        - x0 = starting value of independent variable (Example: time)
        - y0 = initial value of dependent variable (Example: position)
        - y'0 = initial value of the first derivative of the dependent variable (Example: velocity)
        - y''0 = initial value of the second derivative of the dependent variable (Example: Acceleration)
        The order should be (independent variable, dependent variable, 1st derivative of dependent variable,
        second derivative of dependent variable).

        Example: ics = - 3rd order ODE : [initial time, initial amplitude, initial velocity, initial acceleration].
                       - 2nd order ODE: [initial time, initial amplitude, initial velocity]
                       - 1st order ODE: [initial time, initial amplitude]

    step_size = value of the 'h' parameter in Euler's method

    x1 = final value of independent variable

    **Returns:**
    - y_deriv_deriv_vals = solution vector of y''(x) if a 3rd order ODE is being solved
    - y_deriv_vals = solution vector of y'(x) if a 3rd order ODE or 2nd order ODE is being solved
    - y_vals = solution vector of dependent variable.
    - x_vals = vector of the independent variable for which the
    dependent variable was calculated'''

    # For solving 1st order ODEs
    if len(ics) == 2:

        x0 = ics[0]  # Initial value of independent variable
        y0 = ics[1]  # Iniial value of dependent variable

        x_vals = [x0]  # Solution vector for the independent variable
        y_vals = [y0]  # Solution vector for the dependent variable
        # Number of iterations based on given step size
        iterations = round((x1 - x0) / step_size)
        '''Number of almost equally spaced points for
         the given step_size and range(x1-x0).
         Iterations are rounded to be able to be used as a range'''

        for i in range(int(iterations)):
            next_approx = y_vals[-1] + step_size * f(y_vals[-1], x_vals[-1])
            '''last element of y vector gets updates as 
                y(x+h) = y(x) + h*y'(x)'''

            y_vals.append(next_approx)
            x_vals.append(x_vals[-1] + step_size)

        return y_vals, x_vals

    # For solving 2nd order ODEs
    if len(ics) == 3:

        x0 = ics[0]  # Initial value of independent parameter
        y0 = ics[1]  # Initial value of dependent parameter
        # Initial value of first derivative of dependent parameter.
        y_deriv0 = ics[2]

        x_vals = [x0]  # Solution vector for independent variable
        y_vals = [y0]  # Solution vector for the dependent variable
        # Solution vector for the first derivative of dependent variable
        y_deriv_vals = [y_deriv0]

        # Number of iterations based on given step size.
        iterations = round((x1 - x0) / step_size)
        '''Number of almost equally spaced points for
             the given step_size and range(x1-x0).
             Iterations are rounded to be able to be used as a range'''

        for i in range(int(iterations)):
            '''Formulas used:
            - x(n+1) = x(n) + h
            - y(n+1) = y(n) + h*(y_deriv(n))
            - y'(n+1) = y'(n) + h*d(y')/dx (y'(n), y(n), x(n))'''

            # New values of dy/dx, y, x
            y_new = y_vals[-1] + step_size * y_deriv_vals[-1]
            y_deriv_new = y_deriv_vals[-1] + step_size * f(y_deriv_vals[-1], y_vals[-1], x_vals[-1])
            x_new = x_vals[-1] + step_size

            # New values get appended to solution vectots
            y_vals.append(y_new)
            y_deriv_vals.append(y_deriv_new)
            x_vals.append(x_new)

        return y_deriv_vals, y_vals, x_vals

    # For solving 3rd order ODEs:

    if len(ics) == 4:
        x0 = ics[0]  # Initial value of independent parameter
        y0 = ics[1]  # Initial value of dependent parameter
        # Initial value of first derivative of dependent parameter
        y_deriv0 = ics[2]
        # Initial value of second derivative of dependent parameter
        y_deriv_deriv0 = ics[3]

        x_vals = [x0]  # Solution vector for independent variable
        y_vals = [y0]  # Solution vector for the dependent variable
        # Solution vector for the first derivative of dependent variable
        y_deriv_vals = [y_deriv0]
        # solution vector for the second derivative of dependent variable
        y_deriv_deriv_vals = [y_deriv_deriv0]

        # Number of iterations based on given step size.
        iterations = round((x1 - x0) / step_size)
        '''Number of almost equally spaced points for
             the given step_size and range(x1-x0).
             Iterations are rounded to be able to be used as a range'''

        # Calculating new values of y''(x), y'(x), y(x), x and making solution vectors

        for i in range(int(iterations)):
            '''Formulas used:
            - x(n+1) = x(n) + h
            - y(n+1) = y(n) + h*(y_deriv(n))
            - y'(n+1) = y'(n) + h*d(y')/dx 
            - y''(n+1) = y''(n) + h*f(y'')/d(x){x, y, y', y''}
            '''

            # new values of dependent variable
            y_new = y_vals[-1] + step_size * y_deriv_vals[-1]
            # new values of y'(x)
            y_deriv_new = y_deriv_deriv_vals[-1] + \
                step_size * y_deriv_deriv_vals[-1]
            y_deriv_deriv_new = y_deriv_deriv_vals[-1] + step_size * f(y_deriv_deriv_vals[-1], y_deriv_vals[-1],
                                                                       y_vals[-1], x_vals[-1])  # new values of y''(x)

            # new values of independent variable
            x_new = x_vals[-1] + step_size

            # Appending new values to solution vectors
            x_vals.append(x_new)
            y_vals.append(y_new)
            y_deriv_vals.append(y_deriv_new)
            y_deriv_deriv_vals.append(y_deriv_deriv_new)

        return y_deriv_deriv_vals, y_deriv_vals, y_vals, x_vals


'''Function for solving a differential equation numerically using modified euler's method
up to 2nd Order.
'''


def mod_euler(f, ics, step_size, x1):
    ''' 
    Function for solving a differential equation numerically using modified euler's method
    up to 2nd Order.
      
    Input variables:
    f :

    - If a 1st order differential equation is required to solve,
                  f is differential equation of the form :
                   dy/dx = f(y, x)

    - If a 2nd order ODE is required to be solved then f = du/dx(u, y, x) where
        u is dy/dx, i.e the first order derivative of the dependent variable with respect to the
        independent variable.

    ics: Initial conditions which should contain at least 2(including x0, which is compulsory) of:
        - x0 = starting value of independent variable (Example: time)
        - y0 = initial value of dependent variable (Example: position)
        - y'0 = initial value of the first derivative of the dependent variable (Example: velocity)
        The order should be (independent variable, dependent variable, 1st derivative of dependent variable,
        second derivative of dependent variable).
        Examples : ics =
                       - 2nd order ODE: [initial time, initial amplitude, initial velocity]
                       - 1st order ODE: [initial time, initial amplitude]

    step_size = value of the 'h' parameter in Euler's method

    x1 = final value of independent variable

    **Returns:**

    - y_deriv_vals = solution vector of y'(x) if a 2nd order ODE is being solved
    - y_vals = solution vector of dependent variable.
    - x_vals = solution vector of the independent variable for which the
    dependent variable was calculated
    '''

    # For solving 1st order ODE
    if len(ics) == 2:

        x0 = ics[0]  # Initial value of independent variable
        y0 = ics[1]  # Initial value of dependent variable

        y_vals = [y0]  # Solution vector for the dependent variable
        x_vals = [x0]  # Solution vector for independent variable
        iterations = int(round((x1 - x0) / step_size))

        '''Number of almost equally spaced points for
         the given step_size and range(x1-x0).
         Iterations are rounded to be able to be used as a range'''

        for i in range(iterations):
            c1 = step_size * f(y_vals[-1], x_vals[-1])  # c1 = h*f(y, x)
            c2 = step_size * f(y_vals[-1] + c1, x_vals[-1] + step_size)  # c2 = h*f(y+c1, x+h)

            next_approx = y_vals[-1] + (0.5 * (c1 + c2))
            '''last element of y vector gets updates as 
                y(x+h) = y(x) + 1/2(c1 + c2)
                c1 and c2 are as defined before '''

            y_vals.append(next_approx)  # Append values of dependent variable to solution vector
            x_vals.append(x_vals[-1] + step_size)  # Append values of independent variable to solution vector

        return y_vals, x_vals

    # For solving 2nd order ODE
    if len(ics) == 3:

        x0 = ics[0]  # Initial value of independent variable
        y0 = ics[1]  # Initial value of dependent variable
        y_deriv0 = ics[2]  # Initial value of first derivative of dependent variable, i.e, y'(y, x)

        y_vals = [y0]  # Solution vector for dependent variable
        y_deriv_vals = [y_deriv0]  # Solution vector for y'(y, x)
        x_vals = [x0]  # Solution vector for independent variable

        iterations = int(round((x1 - x0) / step_size))
        '''Number of almost equally spaced points for
         the given step_size and range(x1-x0).
         Iterations are rounded to be able to be used as a range'''

        for i in range(iterations):
            ''' 
            Here, we shall break up the ODE into 2 ODEs which would form a coupled system of equations.
            - dydx = z(y, x), where z is a function of y and x.
            - dz/dz = f(z, y, x) where f is the given function.
            '''

            # Value of 'C1' for a coupled system
            c1 = step_size * f(y_deriv_vals[-1], y_vals[-1], x_vals[-1])
            m1 = step_size * y_deriv_vals[-1]

            # Value of 'C2' for a coupled system
            m2 = step_size * (y_deriv_vals[-1] + c1)
            c2 = step_size * f(y_deriv_vals[-1] + c1, y_vals[-1] + m1, x_vals[-1] + step_size)

            y_new = y_vals[-1] + (
                    (1 / 2) * (m1 + m2))  # New values of y according to formula y_{n+1} = y_n + 1/2(m1+m2)

            # New values of y according to formula y'_{n+1} = y'_n + 1/2(c1+c2)
            y_deriv_new = y_deriv_vals[-1] + ((1 / 2) * (c1 + c2))

            x_new = x_vals[-1] + step_size  # New values of x as x_{n+1} = x_n + h

            y_vals.append(y_new)  # Append values of dependent variable to solution vector
            y_deriv_vals.append(y_deriv_new)  # Append values of y'(y, x) to solution vector
            x_vals.append(x_new)  # Append values of independent variable to solution vector

        return y_deriv_vals, y_vals, x_vals


''' Range Kutta 4 ODE solver for solving ODEs upto 2nd order '''


def RK4_solver(f, ics, step_size, x1):
    ''' 
    Range Kutta 4 ODE solver for solving ODEs upto 2nd order

    **Input variables:**
    f :

    - If a 1st order differential equation is required to solve,
                  f is differential equation of the form :
                   dy/dx = f(y, x)

    - If a 2nd order ODE is required to be solved then f = du/dx(u, y, x) where
        u is dy/dx, i.e the first order derivative of the dependent variable with respect to the
        independent variable.

    ics: Initial conditions which should contain at least 2(including x0, which is compulsory) of:
        - x0 = starting value of independent variable (Example: time)
        - y0 = initial value of dependent variable (Example: position)
        - y'0 = initial value of the first derivative of the dependent variable (Example: velocity)
        The order should be (independent variable, dependent variable, 1st derivative of dependent variable)

        Example: ics = - 2nd order ODE: [initial time, initial amplitude, initial velocity]
                       - 1st order ODE: [initial time, initial amplitude]

    step_size = value of the 'h' parameter in RK4 method

    x1 = final value of independent variable

    **Returns:**
    - y_deriv_vals = solution vector of y'(x) if a 2nd order ODE is being solved
    - y_vals = solution vector of dependent variable.
    - x_vals = solution vector of the independent variable for which the
    dependent variable was calculated'''

    # For solving first order ODEs
    if len(ics) == 2:

        ''' Formulas used:
        - k1 = hf(y_n, x_n)
        - k2 = hf(y_n + k1/2, x_n + h/2)
        - k3 = hf(y_n + k2/2, x_n + h/2)
        - k4 = hf(y + k3, x + h)

        - y_(n+1) = y_n + 1/6 * (k1 + 2k2 + 2k3 + k4)
        - x_(n+1) = x_n + h
        '''

        x0 = ics[0]  # Initial value of independent variable
        y0 = ics[1]  # Initial value of dependent variable

        y_vals = [y0]  # Solution vector for dependent variable
        x_vals = [x0]  # Solution vector for independent variable

        # Number of iterations based on given step size
        iterations = int(round((x1 - x0) / step_size))
        '''Number of almost equally spaced points for
         the given step_size and range(x1-x0).
         Iterations are rounded to be able to be used as a range'''

        for i in range(iterations):
            k1 = step_size * f(y_vals[-1], x_vals[-1])  # k1 = hf(y_n, x_n)

            # k2 = hf(y_n + k1/2, x_n + h/2)
            k2 = step_size * f(y_vals[-1] + k1 / 2, x_vals[-1] + step_size / 2)

            # k3 = hf(y_n + k2/2, x_n + h/2)
            k3 = step_size * f(y_vals[-1] + k2 / 2, x_vals[-1] + step_size / 2)

            # k4 = hf(y + k3, x + h)
            k4 = step_size * f(y_vals[-1] + k3, x_vals[-1] + step_size)

            # y_(n+1) = y_n + 1/6 * (k1 + 2k2 + 2k3 + k4)
            y_new = y_vals[-1] + 1 / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            x_new = x_vals[-1] + step_size  # x_(n+1) = x_n + h

            # Solution vector of dependent variable gets updated
            y_vals.append(y_new)
            # Solution vector of independent variable gets updated
            x_vals.append(x_new)

        return y_vals, x_vals  # Returns solution vector of dependent and independent variable

    # For solving 2nd order ODEs

    if len(ics) == 3:

        x0 = ics[0]  # Initial value of independent variable
        y0 = ics[1]  # Initial value of dependent variable
        y_deriv0 = ics[2]  # Initial value of derivative of dependent variable

        # Solution vector for derivative of dependent variable
        y_deriv_vals = [y_deriv0]
        y_vals = [y0]  # Solution vector for dependent variable
        x_vals = [x0]  # Solution vector for independent variable

        # Number of iterations based on given step size
        iterations = int(round((x1 - x0) / step_size))
        '''Number of almost equally spaced points for
         the given step_size and range(x1-x0).
         Iterations are rounded to be able to be used as a range'''

        for i in range(iterations):
            ''' 
            Here, we shall break up the ODE into 2 ODEs which would form a coupled system of equations.
            - dydx = z(y, x), where z is a function of y and x.
            - dz/dz = f(z, y, x) where f is the given function.
            '''

            # Value of 'K1' for the system
            k1 = step_size * f(y_deriv_vals[-1], y_vals[-1], x_vals[-1])
            m1 = step_size * y_deriv_vals[-1]

            # Value of 'K2' for the system
            m2 = step_size * (y_deriv_vals[-1] + (0.5 * k1))
            k2 = step_size * \
                f(y_deriv_vals[-1] + (0.5 * k1), y_vals[-1] +
                  (0.5 * m1), x_vals[-1] + (0.5 * step_size))

            # Value of 'K3' for the system
            m3 = step_size * (y_deriv_vals[-1] + (0.5 * k2))
            k3 = step_size * \
                f(y_deriv_vals[-1] + (0.5 * k2), y_vals[-1] +
                  (0.5 * m2), x_vals[-1] + (0.5 * step_size))

            # Value of 'K4' for the system
            m4 = step_size * (y_deriv_vals[-1] + k3)
            k4 = step_size * \
                f(y_deriv_vals[-1] + k3, y_vals[-1] +
                  m3, x_vals[-1] + step_size)

            # y gets updated as y_new = y_old + 1/6(m1 + 2m2 + 2m3+ m4)
            y_new = y_vals[-1] + ((1 / 6) * (m1 + 2 * m2 + 2 * m3 + m4))

            # y' gets updated as y'_new = y'_old + 1/6(k1 + 2k2 + 2k3+ k4)
            y_deriv_new = y_deriv_vals[-1] + \
                ((1 / 6) * (k1 + 2 * k2 + 2 * k3 + k4))

            # x gets updated as x_new = x_old + h
            x_new = x_vals[-1] + step_size

            # Append values of y'(y, x), y and x to solution vectors
            y_deriv_vals.append(y_deriv_new)
            y_vals.append(y_new)
            x_vals.append(x_new)

        return y_deriv_vals, y_vals, x_vals


if __name__ == '__main__':
    import numpy as np

    # Solving a 1D ODE
    def dydx(y, x):
        return 1/x
    ics1 = [1, 0]
    # Euler method solutions
    y_euler, x_euler = euler(f=dydx, ics=ics1, step_size=0.001, x1=5)

    # Modified euler method solutions
    y_mod, x_mod = mod_euler(f=dydx, ics=ics1, step_size=0.001, x1=5)

    # RK4 solutions
    y_rk4, x_rk4 = RK4_solver(f=dydx, ics=ics1, step_size=0.001, x1=5)

    # Solving a 2D ODE - Equation of a damped harmonis oscillator

    def dudt(u, x, t):  # u = dxdt
        b = 0.2  # damping parameter
        k = 20  # Spring constant
        return -b*u - k*x
    ics = [0, np.pi/50, 0] # At t=0, x = pi/50, vel = 0
   
    # Euler solutions
    u_euler, x_euler2, t_euler = euler(f = dudt, ics = ics, step_size=0.001, x1 = 15)

    # Modified euler solutions
    u_modeuler, x_modeuler2, t_modeuler = mod_euler(f = dudt, ics = ics, step_size=0.001, x1 = 15)

    # RK4 solutions
    u_rk4, x_rk4_2, t_rk4 = RK4_solver(f = dudt, ics = ics, step_size=0.001, x1 = 15)

    plt.plot(x_mod, y_mod, label= 'mod_euler')
    plt.plot(x_euler, y_euler, label = 'euler')
    # plt.plot(u_euler, t_euler, label = 'euler')
    # plt.plot(u_modeuler, t_modeuler, label = 'modeuler')
    # plt.plot(u_rk4, t_rk4, label = 'rk4')


    plt.legend()
    plt.show()

