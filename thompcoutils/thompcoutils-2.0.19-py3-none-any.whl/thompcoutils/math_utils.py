

class MovingAverage:
    """
    Keeps a moving average of values (could be int, float, time_diff, etc)
    """

    def __init__(self, zero_value):
        """
        Initializes a MovingAverage object.

        param: zero_value the initial zero value of the type to be averaged (int, float, time_diff, etc)
        """
        self.zero_value = zero_value
        self.running_count = 0
        self.running_total = zero_value

    def new_value(self, value):
        """
        Appends a new value to the MovingAverage

        param: value: the new value to add
        return: the average after adding this value
        """
        self.running_count += 1
        self.running_total += value

    def get_average(self):
        """
        Calculates the average so far

        return: the current running total
        """
        return self.running_total / self.running_count

    def reset(self):
        """
        Resets the values
        """
        self.running_count = 0
        self.running_total = self.zero_value
