from core.number.BigFloat import BigFloat


class BigFloatOperation:

    def __init__(self, amount: BigFloat, other: BigFloat):
        self.number = 0
        self.leading_zeros = 0
        self.amount = amount
        self.other = other
        self.__pad_fractions()

    def __pad_fractions(self):
        fraction_length = self.amount.fraction_leading_zeros + self.size(self.amount.fraction)
        other_fraction_length = self.other.fraction_leading_zeros + self.size(self.other.fraction)
        if fraction_length > other_fraction_length:
            pad = fraction_length - other_fraction_length
            self.other.fraction = self.other.fraction * (10 ** pad)
        elif fraction_length < other_fraction_length:
            pad = other_fraction_length - fraction_length
            self.amount.fraction = self.amount.fraction * (10 ** pad)

    @staticmethod
    def size(number):
        return len(str(number))

    def largest(self, number, another):
        number_size = self.size(number)
        another_number_size = self.size(another)
        if number_size > another_number_size:
            return number_size
        elif another_number_size > number_size:
            return another_number_size
        return another_number_size

    def calculate_different_leading_zeros(self):
        if self.amount.fraction_leading_zeros > self.other.fraction_leading_zeros:
            return self.other.fraction_leading_zeros
        elif self.amount.fraction_leading_zeros < self.other.fraction_leading_zeros:
            return self.amount.fraction_leading_zeros
        return self.amount.fraction_leading_zeros

    def result(self):
        pass
