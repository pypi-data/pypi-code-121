from core.number.BigFloat import BigFloat

from coreutility.number.BigFloatOperation import BigFloatOperation


class BigFloatSubtract(BigFloatOperation):

    def __init__(self, amount: BigFloat, other: BigFloat):
        super().__init__(amount, other)

    def result(self):
        self.number = self.amount.number - self.other.number
        self.leading_zeros = self.calculate_different_leading_zeros()
        fraction = 0
        return BigFloat(self.number, fraction, self.leading_zeros)
