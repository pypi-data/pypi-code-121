from core.number.BigFloat import BigFloat

from coreutility.number.BigFloatOperation import BigFloatOperation


class BigFloatAdd(BigFloatOperation):

    def __init__(self, amount: BigFloat, other: BigFloat):
        super().__init__(amount, other)

    def result(self):
        self.number = self.amount.number + self.other.number
        self.leading_zeros = self.calculate_different_leading_zeros()
        fraction = self.add_fractions()
        return BigFloat(self.number, fraction, self.leading_zeros)

    def add_fractions(self):
        largest_fraction_size_before = self.largest(self.amount.fraction, self.other.fraction)
        fraction = self.amount.fraction + self.other.fraction
        fraction_size_after = self.size(fraction)
        if fraction_size_after > largest_fraction_size_before:
            leading_zeros = self.leading_zeros - (fraction_size_after - largest_fraction_size_before)
            if leading_zeros < 0:
                number_to_add = fraction // (10 * abs(leading_zeros))
                self.number = self.number + number_to_add
                fraction = fraction % (10 * abs(leading_zeros))
                self.leading_zeros = 0
            else:
                self.leading_zeros = leading_zeros
        return fraction
