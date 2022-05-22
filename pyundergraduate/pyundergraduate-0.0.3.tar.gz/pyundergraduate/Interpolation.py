from matplotlib import pyplot as plt
import numpy as np

# Lagrange's Interpolation


class LagrangeInterp():
    '''
    This is a class and hence, an object needs to be created for this class.
    Input parameters:
    - x_list: Array-like. The list of independent points for interpolation.
              Doesn't need to be equally spaced.
    - y_list: Array-like. The list of dependent points for interpolation. 

    The class returns the x_list, y_list and the interpolating function upon calling.
    **Note:** 
    The values in x_list don't need to be equally spaced.
    The points where interpolation is needed lie outside of the given
    range of x_list. However, it is not advisable to do this.


    Example code:
    - import numpy as np
    - x_list = [1,2,3,4] # independent
    - y_list = [1,4,9,16] # dependent
    - interpolator = LagrangeInterp(x_list = x_list, y_list = y_list) # Object
    - func = interpolator.GetFunc() # returns the interpolating function.
    - x_pts = np.linspace(1, 9, 1000) # pts where interpolation is needed
    - y_pts = func(x_pts) # solutions
    '''

    def __init__(self, x_list, y_list):
        self.x_list = x_list  # initial independent variables
        self.y_list = y_list  # initial dependent variables

    def GetFunc(self):
        import numpy as np

        def InterFunc(x):
            func = 0  # Initiation value of the function coefficients
            # x and y values zipped as (x, y)
            pts = list(zip(self.x_list, self.y_list))

            for j in pts:
                x_temp = np.array([x[0] for x in pts if x[0] != j[0]])
                '''choosing the x list 
                 excluding one point at every iteration'''

                # numerator and denominator gets updated to 1 for next loop
                numerator, denominator = 1, 1
                for i in range(len(x_temp)):
                    # Numerator gets updated as (x-x_n)
                    numerator *= (x - x_temp[i])
                    denominator *= j[0] - x_temp[i]
                    '''Denominator gets updated as (x0 - x_n) where x_n = j[0], i.e, the excluded point'''
                func += numerator*j[1]/denominator
                x_temp = self.x_list  # X_temp gets updated back to x_list for next loop
            return func
        return InterFunc  # The interpolating function is returned by GetFunc()


# Newton Forward Interpolation
def NewtonForward(x_list, y_list, x):
    '''
     **Input variables:**
    - x_list : values of the independent parameters as a list
    - y_list : values of the independent parameter as a list
    - x: Array or list: Values of x for which interpolation is needed

     Formula used:
     F(a+uh) = F(a) + u/2! D{F(a)} + u(u-1)/3! D2{F(a)} + ..........
     Here: Dn{F(a)} represents the 'n' th forward difference
          a + uh = value of x at which interpolation is needed.
          NOTE: The h is has to be  constant in this method.

    NOTE: This method can also be done using the numpy function 'np.diff'.
          However, we are not using that to preserve the simplicity of the code.

    Returns : List: The interpolated answer for the given data points of the independent
              variable.
    '''


    # Convert x lists and y lists into numpy arrays for faster computation
    x_list = np.array(x_list)
    y_list = np.array(y_list)

    ''' First we will throw some checks to see
    1) If length of x_list and y_list are same
    2) If the difference of consecutive elements in the x list
    is constant or not. This method only works for a constant difference.
    If the difference is not constant, then function will throw an Error and a comment.
    3) If the type of the input parameters is numeric or not.
    '''

    # Check if length of x_list and y_list are same
    if len(x_list) != len(y_list):
        raise AssertionError('x_list and y_list must be of same length')

    # Check if the difference between consecutive elements of x_list are same or not
    if all(i == np.diff(x_list)[0] for i in np.diff(x_list)) == False:
        raise ArithmeticError('Difference of consecutive elements in x_list is not same')

    # Check if x_list is  list-like or not
    if isinstance(x_list, (list, np.ndarray, tuple))  == False:
        raise TypeError('Please input numeric values for x_list ')

    # Check if y_list is list-like or not
    if isinstance(y_list, (list, np.ndarray, tuple))  == False:
        raise TypeError('Please input numeric values for y_list ')

    # Check if x is list-like or not
    if isinstance(x, (list, np.ndarray, tuple))  == False:
        raise TypeError('Please input numeric values for x')

    ''' Now we modify the x_list and the y_list to work for data 
    when the data is taken from in between the data and not from the beginning of the 
    data. 
    NOTE: This is not recommended. For data from the middle of the data, we should
    use Strirling's formula and for data from the end of the data, we should use
    Newton's backard interpolation method
    '''
    solutions = []  # Solution vector for the interpolated points

    for x_pt in x:

        if isinstance(x_pt, (int, float)) == False:
            raise ValueError('Enter numbers in x')
        # Check if the given point lies within the given x data. Otherwise, throw error
        if (x_pt > max(x_list) or x_pt < min(x_list)):
            raise ValueError('Enter a number within the given x data')

        extra_x_indices = []  # Extra unnecessary elements indices in the x_list
        extra_y_indices = []  # Extra unnecessary elements indices in the y_list
        for i in enumerate(x_list):
            if i[1] < x_pt:
                extra_x_indices.append(i[0])
                extra_y_indices.append(i[0])
        if len(extra_y_indices) and len(extra_x_indices) != 0:
            # Make sure that there is 1 element before x_pt in the table
            # So that a difference may be taken
            extra_y_indices.pop()
            extra_x_indices.pop()
        x_list = np.delete(arr=x_list, obj=extra_x_indices)
        y_list = np.delete(arr=y_list, obj=extra_y_indices)

        diff_table = []  # Forward difference table
        x0 = x_list[0]  # Initial value for forward interpolation

        interp_ans = y_list[0]  # Final answer

        h = x_list[1] - x_list[0]  # This has to be constant

        counter = 1

        coeff = (x_pt - x0) / h
        '''This is the 'u' parameter we see in the formula which takes form u/1!, u(u-1)/2!, u(u-1)(u-2)/3!, .....'''

        for i in range(len(y_list), 1, -1):
            ''' Why do we implement a double loop?
            The double loop is implemented to calculate the consecutive forward differences.
            Every 'n' th iteration calculates the 'n' forward difference.
            
            The range of the first loop is [number of y elements, 2] as is obvious because after every iteration,
            the number of elements in the diff tables get reduced by 1 element.
            
            '''
            for j in range(i - 1):
                '''
                The range of the second loop is (i-1) because of the simple reason that the number of elements in
                the consecutive difference tables are decreasing by 1.
                Example: y = [1,2,3,4,5]  {Length = 5}
                First forward difference = [1, 1, 1, 1]  {Length = 4}
                Second forward difference = [0, 0, 0]  {Length = 3}
                Third forward difference = [0, 0]   {Length = 2}
                Fourth forward difference = [0]    {Length = 1}
                '''
                new_diff = y_list[j + 1] - y_list[j]  # Every diff value is the diff between the '(n+1)' th and 'n' th value
                diff_table.append(new_diff)  # Appending values to the difference table
            interp_ans += coeff * diff_table[0]

            '''We take the first element of diff table and use formula.
            Eg: u * D{f(a)} / 1!,    u * (u-1) * D2{f(a)} / 2! and so on.
            Final answer gets updated as 
            ans = f(a) + uD(f(a)) + u(u-1) D2 (f(a))/2! + u(u-1)u(u-2) D3(f(a))/3! + ....
            '''

            coeff *= (coeff - counter) / (counter + 1)  # Coefficient gets updated as u(u-1)(u-2)....(u-n)/(n+1)!
            counter += 1  # Counter gets updated

            diff_table = []  # Clear the difference table for next iteration

        solutions.append(interp_ans)
    return solutions  # The final interpolated answer gets returned








if __name__ == '__main__':
    def func(x):
        return np.sin(x)

    # xlist doesn't need to be evenly spaced
    x_list = [1, 2, 2.5, 3.7,  4, 4.6, 5, 6, 6.7, 7.2, 8.5, 9]
    y_list = func(x_list)
    interpolator = LagrangeInterp(x_list=x_list, y_list=y_list)

    f = interpolator.GetFunc()  # The interpolatin function

    x_pts = np.linspace(0, 10, 1000)
    y_pts = f(x_pts)
    plt.style.use(['science', 'notebook', 'grid'])
    plt.plot(x_pts, y_pts, label='interpolated function')
    plt.plot(x_list, y_list, 'o', markersize=10)
    plt.legend(loc='best')
    plt.show()
