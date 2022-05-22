

def Integration_trapezoidal(f, lower_lim, upper_lim, intervals=1000):
    '''
        - f:     A function which needs to be integrated.
                The function should have the forn f(x), where x
                is the dependent variable. If other parameters
                are present they need to be mentioned while giving the function
                in the method.
        - lower_lim : Lower limit of integration - A float.
        - upper_lim : Upper limit of integration: a float
        - Intervals : Number of intervals for which integration needs to be calculated.
                    This is used to calculate the 'h' parameter in the Trapezoidal rule.
                    It is set to 1000 by default.



    **Trapezoidal Rule:**
    Integral = h(1/2[f(Xn) + f(X0)] + f(X1) + f(X2) + f(X3) +......+f(X{n-1}))

    Here: X0 = initial lower limit of integration
          Xn = upper limit of integration
          Xi = X0 + i*h
          h = (upper limit - lower limit)/(no. of intervals we wish to break up the interval in).

    ***Returns:*** The final integral
    '''

    step_size = (upper_lim - lower_lim) / intervals  # The step size for the integratiom, i.e 'h' parameter.

    S = 1 / 2 * (f(lower_lim) + f(upper_lim))  # Integral starts with 1/2(f(X0) + f(Xn))

    for i in range(1, intervals):
        S += f(lower_lim + i * step_size)  # f(xi = x0 + ih) gets appended after every loop

    return step_size * S  # final Integral is returned



def Simpson_one_third(f, lower_lim, upper_lim, intervals=1000):
    '''
    ###Input Parameters:###
    - f:        A function which needs to be integrated.
                The function should have the forn f(x), where x
                is the dependent variable. If other parameters
                are present they need to be mentioned while giving the function in the method.

    - lower_lim :    Lower limit of integration - A float.
    - upper_lim :    Upper limit of integration - A float
    - Intervals : Number of intervals for which integration needs to be calculated.
                    This is used to calculate the 'h' parameter in the Trapezoidal rule.
                    It is set to 1000 by default.

    **NOTE:** The Simpsons rule only works for positive number of intervals. If provided with an odd number of
              interval, the function will prompt to input an even number.


    **Simpson's rule:**
    Integral = h/3([f(X0) + f(Xn)] + 4(f(X1) + f(X2) + f(X3) + .......) + 2(f(X2) + f(X4) + f(X6)+........))

    which is essentially = h/3([f(upper_limit)+ f(lower_limit)] + 4(odd terms sum) + 2(even terms sum))

    **NOTE:** Here, in the even terms sum, f(upper limit), though being 'an even term', should not be used.
    Here: X0 = initial lower limit of integration
          Xn = upper limit of integration
          Xi = X0 + i*h
          h = (upper limit - lower limit)/(no. of intervals we wish to break up the interval in).

    ### Returns:### The integral

    '''

    # Checking if the number of intervals is even or odd. Throw error message if it is NOT even.
    if intervals % 2 == 1:
        raise ValueError('Choose a different interval which is even')

    # The h parameter for the method
    step_size = (upper_lim - lower_lim) / intervals

    odd_terms_sum, even_terms_sum = 0, 0  # Odd terms and even terms

    integral = (f(upper_lim) + f(lower_lim))  # Integral starts with f(upper_lim) + f(lower_lim)

    for i in range(1, intervals):
        if i % 2 == 1:  # n = odd
            odd_terms_sum += f(lower_lim + i * step_size)  # Odd terms get updated
        if i % 2 == 0:  # n = even
            even_terms_sum += f(lower_lim + i * step_size)  # Even terms get updated
    integral = step_size / 3 * (
                integral + 4 * odd_terms_sum + 2 * even_terms_sum)  # Integral gets updated with formula.

    return integral  # Returns just the answer



def Simpson_three_eighth(f, lower_lim, upper_lim, intervals=1000):
    '''
    ###Input Parameters:###
    - f:        A function which needs to be integrated.
                The function should have the forn f(x), where x
                is the dependent variable. If other parameters
                are present they need to be mentioned while giving the function in the method.

    - lower_lim :    Lower limit of integration - A float.
    - upper_lim :    Upper limit of integration - A float
    - Intervals : Number of intervals for which integration needs to be calculated.
                    This is used to calculate the 'h' parameter in the Trapezoidal rule.
                    It is set to 1000 by default.

    **NOTE:** The 3/8 Simpsons rule only works for number of intervals which are integral multiples  of 3.
              If provided with an odd number of intervals, the function will prompt to input an appropriate number..


    **Simpson's 3/8 rule:**
    Integral = 3h/8([f(X0) + f(Xn)] + 3(f(X1) + f(X2) + f(X4) + .......) + 2(f(X3) + f(X6) + f(X9)+........))

    which is essentially = 3h/8([f(upper_limit)+ f(lower_limit)] +  2(terms which are multiples of 3 sum) +
    3(remaining terms sum))

    **NOTE:** Here, in the 'multiple of 3' terms sum, f(upper limit), even if it is  'a multiple of 3 term',
    should not be used.
    Here: X0 = initial lower limit of integration
          Xn = upper limit of integration
          Xi = X0 + i*h
          h = (upper limit - lower limit)/(no. of intervals we wish to break up the interval in).

    ### Returns:### The integral

    '''

    # Checking if the number of intervals is even or odd. Throw error message if it is NOT even.
    if intervals % 3 != 0:
        raise ValueError('Choose a different interval which is a multiple of 3')

    # The h parameter for the method
    step_size = (upper_lim - lower_lim) / intervals

    extra_terms_sum, three_multiple_terms_sum = 0, 0  # Odd terms and even terms

    integral = (f(upper_lim) + f(lower_lim))  # Integral starts with f(upper_lim) + f(lower_lim)

    for i in range(1, intervals):
        if i % 3 == 0:  # n = multiple of 3
            three_multiple_terms_sum += f(lower_lim + i * step_size)  # Odd terms get updated
        else:  # n = not multiple of 3
            extra_terms_sum += f(lower_lim + i * step_size)  # Even terms get updated
    integral = 3 * step_size / 8 * (
                integral + 2 * three_multiple_terms_sum + 3 * extra_terms_sum)  # Integral gets updated with formula.

    return integral  # Returns just the answer


# composite rules of integration

class CompositeIntegration():
    '''
    This class calculates the intergral of a function using Composite Simpson's
    Rule and Composite Trapezoidal rule.
    
    **Input parameters:**
    - Function: The function whose integration is neede
    - lowerlim : Float - The lower limit of integration
    - upperlim : Float - The upper limit of integration
    - intervals : Number of intervals to break up the integral in (2000 by default).
    **Note** A huge number of intervals may seem to make the integral more accurate.
        However, the integral may take up excessive computational power.

    **Returns**
    
    <1> Upon calling, the class resturns the attributes:
    - the function
    - the lower limit
    - the upper limit
    - the number of intervals
    - the 'h' parameter in the formula

    <2>Upon calling, the class resturns the methods:
    -  Answer with Composite Trapezoidal Rule
    - Answer with Composite Simpsons Rule


    '''

    def __init__(self, func, lowerlim, upperlim, intervals=2000):
        self.f = func
        self.lowerlim = lowerlim
        self.upperlim = upperlim
        self.n = intervals
        self.h = float(self.upperlim - self.lowerlim)/self.n
    
    def Comp_Trapezoidal_Rule(self):

        # Initialization
        result = 0.5 * (self.f(self.lowerlim) + self.f(self.upperlim))

        for i in range(1, self.n):
            # X term gets updated
            independent_var = self.lowerlim + i*self.h

            # Solution gets updated
            result += self.f(independent_var)

        return result*self.h

    def Comp_Simpsons_Rule(self):
        # Initialization
        result = self.f(self.upperlim) + self.f(self.lowerlim)

        d = [2 , 4]  # Coefficients for the method
        for i in range(1, self.n):
            new_x = self.lowerlim + i*self.h # X gets updated as x_new = x + ih
            result += d[-1] * self.f(new_x)  # Solution gets updated
            d.reverse()  # List gets reversed
        return result*self.h/3



if __name__ == '__main__':
    import numpy as np
    f = lambda x: x*np.sin(x)
    lowerlim = 0
    upperlim = 10
    intervals = 1000

    # Trapezoidal rule
    trap_ans = Integration_trapezoidal(f=f, lower_lim=lowerlim, upper_lim=upperlim, intervals=intervals)

    # Simpsons one third rule
    simp_one_third_ans = Simpson_one_third(f=f, lower_lim=lowerlim, upper_lim=upperlim, intervals=intervals)

    # Simpsons three eight rule
    simp_three_eight_ans = Simpson_three_eighth(f=f, lower_lim=lowerlim, upper_lim=upperlim, intervals=intervals + 2)

    # Composite rules
    integrator = CompositeIntegration(func=f, lowerlim=lowerlim, upperlim=upperlim, intervals=intervals)

    ## Composite Trapezoidal rule
    comptrap_ans = integrator.Comp_Trapezoidal_Rule()

    ## Composite Simpson's rule
    compsimp_ans = integrator.Comp_Simpsons_Rule()

    print(f'trap_ans = {trap_ans}')
    print(f'simp3/8 = {simp_three_eight_ans}')
    print(f'simp1/3 = {simp_one_third_ans}')
    print(f'comp_simp = {compsimp_ans}')
    print(f'comptrap = {comptrap_ans}')
    